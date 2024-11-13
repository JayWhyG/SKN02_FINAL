from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from interview_model.interview_assistant_model import InterviewAssistant, call_ollama_api_streaming, FinalFeedbackGenerator, InterviewAssistant2, AutoGenInterviewAssistant
from interview_model.general_questions_generator_model import GeneralQuestionsGenerator  # 질문 생성 모델
from models.db_models import *  # DB 모델
from routers.db_router import *  # DB에서 데이터를 가져오는 함수
import base64
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import tempfile
import os
import traceback
import requests
import ormsgpack


router = APIRouter()
feedback_model = FinalFeedbackGenerator(llm_model_name="gpt-4o-mini")


class InterviewRequest(BaseModel):
    user_id: str  # 사용자 ID
    resume_id: str
    corporate_id: str
    job_id: str
    interview_style: str  # 면접관 스타일 (일반, 부드러운, 압박)
    difficulty_level: int  # 면접 난이도 (1~3)

class AnswerRequest(BaseModel):
    user_id: str  # 사용자 ID
    user_answer: str

class UserInUse():
    def __init__(self,user_id,interview_assistant,question_id_in_use,interview_id) :
        self.user_id = user_id  # 사용자 ID
        self.interview_assistant = interview_assistant
        self.question_id_in_use = question_id_in_use
        self.interview_id = interview_id


interview_sessions = {}  # 사용자 ID 별로 면접 모델을 관리하는 dict
@router.post("/create_interview/")
async def create_interview(request: InterviewRequest):
    global interview_sessions
    try:
        # MySQL에서 이력서, 기업정보, 채용정보, 직무정보 받아오기
        resume = await get_data("이력서", request.resume_id)
        corporate_information = await get_data("기업정보", request.corporate_id)
        job_information,recruitment_information = await get_data("직무정보", request.job_id)

        # GeneralQuestionsGenerator 객체를 생성하고, 질문을 생성 (면접 난이도 추가)
        questions_generator = GeneralQuestionsGenerator(
            resume=resume,
            corporate_information=corporate_information,
            recruitment_information=recruitment_information,
            job_information=job_information,
            difficulty_level=request.difficulty_level  # 면접 난이도 전달
        )
        general_questions = questions_generator.invoke()

        # InterviewAssistant 객체를 생성하여 면접 모델 초기화 (면접관 스타일 및 난이도 추가)
        interview_assistant = InterviewAssistant(
            resume=resume,
            corporate_information=corporate_information,
            recruitment_information=recruitment_information,
            job_information=job_information,
            general_questions=general_questions,
            interview_style=request.interview_style,  # 면접관 스타일
            difficulty_level=request.difficulty_level  # 면접 난이도
        )


        # 면접 시작 메시지를 보내고 결과를 반환
        response, _, _ = interview_assistant.invoke(request.user_id, "","")
        print(response)
        interview_id = save_interview_to_db(request)
        question_id = save_question_to_db(response, interview_id)
        user = UserInUse(request.user_id, interview_assistant, question_id, interview_id)
        # 사용자 ID를 세션 ID로 사용하여 면접 모델을 관리
        interview_sessions[request.user_id] = user
        return {"session_id": request.user_id, "message": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating interview: {str(e)}")

import asyncio

@router.post("/answer/")
async def answer_interview(request: AnswerRequest):
    global interview_sessions
    question_id = None  # 초기값 설정
    try:
        # 사용자 ID를 사용하여 해당 면접 모델을 불러옴
        interview_assistant = interview_sessions.get(request.user_id).interview_assistant
        if not interview_assistant:
            raise HTTPException(status_code=404, detail="Interview session not found")

        # 사용자의 답변을 모델에 입력하고 결과를 반환
        question_id = interview_sessions.get(request.user_id).question_id_in_use
        interview_id = interview_sessions.get(request.user_id).interview_id
        response, feedback, exemplary_answer = interview_assistant.invoke(request.user_id, request.user_answer, question_id)

        # 데이터베이스에 경로 정보 저장
        update_feedback_to_db(request.user_answer, feedback, exemplary_answer, question_id)
        question_id = save_question_to_db(response, interview_id)
        interview_sessions[request.user_id].question_id_in_use = question_id

        end_chack = call_ollama_api_streaming(response)
        print(end_chack)

        # 먼저 응답을 반환
        if end_chack == '종료' or request.user_answer == '차라리 날 죽여라!':
            # 비동기 작업을 실행하는 코드를 추가
            asyncio.create_task(handle_end_session(request.user_id, request.user_answer, question_id))
            if request.user_answer == '차라리 날 죽여라!':
                return {"message": ['죽어라!!', 'end']}
            return {"message": [response, 'end']}

        return {"message": [response, 'run']}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing answer: {str(e)}")


async def handle_end_session(user_id, user_answer, question_id):
    """비동기적으로 세션 종료 작업을 처리하는 함수"""
    # 데이터베이스 업데이트 및 세션 제거
    update_feedback_to_db(user_answer, 'end', 'end', question_id)
    update_final_feedback_to_db(user_id)
    interview_sessions.pop(user_id)

# ====================================================================================================================================================================================
# 음성인식 및 tts 테스트


from whisper import load_model  # whisper 라이브러리를 사용해 모델을 불러옵니다
from pydantic import BaseModel
import tempfile




# ==========================================================================================================================================
# TTS 


def generate_tts_audio(text, reference_audio_path, reference_text, output_path="output_audio.wav"):
    url = "http://127.0.0.1:7860/v1/tts"
    
    # 참조 오디오 파일 로드
    with open(reference_audio_path, "rb") as f:
        audio_data = f.read()

    # 요청 데이터 준비
    data = {
        "text": text,
        "references": [{"audio": audio_data, "text": reference_text}],
        "max_new_tokens": 500,
        "chunk_length": 500,
        "top_p": 0.8,
        "repetition_penalty": 1.2,
        "temperature": 0.8,
        "streaming": False,
    }

    headers = {"Content-Type": "application/msgpack"}
    serialized_data = ormsgpack.packb(data)

    # API 요청
    response = requests.post(url, data=serialized_data, headers=headers)

    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path
    else:
        raise Exception(f"TTS 요청 실패: 상태 코드 {response.status_code}, 에러 메시지: {response.text}")
# Whisper medium 모델 로드
model = load_model("medium")
interview_sessions2 = {}  # 사용자 ID 별로 면접 모델을 관리하는 dict

@router.post("/create_interview_tts/")
async def create_interview_tts(request: InterviewRequest):
    global interview_sessions
    try:
        # MySQL에서 이력서, 기업정보, 채용정보, 직무정보 받아오기
        resume = await get_data("이력서", request.resume_id)
        corporate_information = await get_data("기업정보", request.corporate_id)
        job_information,recruitment_information = await get_data("직무정보", request.job_id)

        # GeneralQuestionsGenerator 객체를 생성하고, 질문을 생성 (면접 난이도 추가)
        questions_generator = GeneralQuestionsGenerator(
            resume=resume,
            corporate_information=corporate_information,
            recruitment_information=recruitment_information,
            job_information=job_information,
            difficulty_level=request.difficulty_level  # 면접 난이도 전달
        )
        general_questions = questions_generator.invoke()

        # InterviewAssistant 객체를 생성하여 면접 모델 초기화 (면접관 스타일 및 난이도 추가)
        interview_assistant = InterviewAssistant2(
            resume=resume,
            corporate_information=corporate_information,
            recruitment_information=recruitment_information,
            job_information=job_information,
            general_questions=general_questions,
            interview_style=request.interview_style,  # 면접관 스타일
            difficulty_level=request.difficulty_level  # 면접 난이도
        )

        # 면접 시작 메시지를 보내고 결과를 반환
        response, _, _ = interview_assistant.invoke(request.user_id, "면접을 시작하세요", "")
        print(response)

        # 면접 ID와 질문 ID 저장
        interview_id = save_interview_to_db(request)
        question_id = save_question_to_db(response, interview_id)
        user = UserInUse(request.user_id, interview_assistant, question_id, interview_id)

        # 사용자 ID를 세션 ID로 사용하여 면접 모델을 관리
        interview_sessions2[request.user_id] = user

         # TTS 변환 및 MP3 생성 - generate_tts_audio로 대체
        tts_audio_path = "output_audio.wav"  # 출력 파일 경로
        try:
            reference_audio_path = "아이유 모닝콜mp3.mp3"  # 참조 오디오 파일 경로
            reference_text = "일어나. 일어나야지! 지금 너 이거 또, 또, 십 분으로 또, 미루면 문제 있어. 일어나. 하루 다 갔어. 지금. 해 중천이야. 일어나."

            generate_tts_audio(response, reference_audio_path, reference_text, tts_audio_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TTS 변환 실패: {str(e)}")

        # 오디오 파일을 Base64로 인코딩
        with open(tts_audio_path, "rb") as audio_file:
            audio_base64 = base64.b64encode(audio_file.read()).decode("utf-8")

        os.remove(tts_audio_path)  # 임시 오디오 파일 삭제

        return {
            "message": response,
            "session_id": request.user_id,
            "audio_base64": audio_base64
        }

    except Exception as e:
        print("An error occurred:")
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=f"Error creating interview: {str(e)}")






# 기존 answer_interview_tts 함수
@router.post("/answer_tts/")
async def answer_interview_tts(user_id: str, file: UploadFile = File(...)):
    try:
        # 사용자 ID를 사용하여 해당 면접 모델을 불러옴
        interview_assistant = interview_sessions2.get(user_id).interview_assistant
        if not interview_assistant:
            raise HTTPException(status_code=404, detail="Interview session not found")

        # 사용자의 답변을 모델에 입력하고 결과를 반환
        question_id_in_use = interview_sessions2.get(user_id).question_id_in_use
        interview_id = interview_sessions2.get(user_id).interview_id

        try:
            # 받은 파일을 임시 파일로 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(await file.read())
                temp_file_path = temp_file.name

            # Whisper 모델로 음성 파일을 변환
            user_answer = model.transcribe(temp_file_path)["text"]

        except Exception as e:
            return {"error": str(e)}
        
        print(f"위스퍼 답변인식 : {user_answer}")

        # 사용자 답변을 통해 InterviewAssistant 모델에서 응답 생성
        response, feedback, exemplary_answer = interview_assistant.invoke(user_id, user_answer, question_id_in_use, temp_file_path)

        # 임시 파일 삭제
        os.remove(temp_file_path)

        # 데이터베이스에 경로 정보 저장
        update_feedback_to_db(user_answer, feedback, exemplary_answer, question_id_in_use)
        question_id = save_question_to_db(response, interview_id)
        interview_sessions2[user_id].question_id_in_use = question_id
        end_check = call_ollama_api_streaming(response)
        print(end_check)

        # TTS 변환 및 MP3 생성 - generate_tts_audio로 대체
        tts_audio_path = "output_audio.wav"  # 출력 파일 경로
        try:
            reference_audio_path = "아이유 모닝콜mp3.mp3"  # 참조 오디오 파일 경로
            reference_text = "일어나. 일어나야지! 지금 너 이거 또, 또, 십 분으로 또, 미루면 문제 있어. 일어나. 하루 다 갔어. 지금. 해 중천이야. 일어나."

            generate_tts_audio(response, reference_audio_path, reference_text, tts_audio_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TTS 변환 실패: {str(e)}")

        # 오디오 파일을 Base64로 인코딩
        with open(tts_audio_path, "rb") as audio_file:
            audio_base64 = base64.b64encode(audio_file.read()).decode("utf-8")

        os.remove(tts_audio_path)  # 임시 오디오 파일 삭제


        # 먼저 응답을 반환
        if end_check == '종료' or user_answer == '차라리 날 죽여라!':
            update_feedback_to_db(user_answer, 'end', 'end', question_id)
            update_final_feedback_to_db(user_id)
            if user_answer == '차라리 날 죽여라!':
                return {"message": ['죽어라!!', 'end'],"audio_base64": audio_base64}
            return {"message": [response, 'end'],"audio_base64": audio_base64}

        return {"message": [response, 'run'],"audio_base64": audio_base64}
    


    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing answer: {str(e)}")



# =======================================================================================================================================
# autogen 테스트

import traceback
interview_sessions3 = {}  # 사용자 ID 별로 면접 모델을 관리하는 dict
@router.post("/create_interview3/")
async def create_interview3(request: InterviewRequest):
    try:
        # MySQL에서 이력서, 기업정보, 채용정보, 직무정보 받아오기
        resume = await get_data("이력서", request.resume_id)
        corporate_information = await get_data("기업정보", request.corporate_id)
        job_information,recruitment_information = await get_data("직무정보", request.job_id)

        # GeneralQuestionsGenerator 객체를 생성하고, 질문을 생성 (면접 난이도 추가)
        questions_generator = GeneralQuestionsGenerator(
            resume=resume,
            corporate_information=corporate_information,
            recruitment_information=recruitment_information,
            job_information=job_information,
            difficulty_level=request.difficulty_level  # 면접 난이도 전달
        )
        general_questions = questions_generator.invoke()

        # InterviewAssistant 객체를 생성하여 면접 모델 초기화 (면접관 스타일 및 난이도 추가)
        # 간단한 테스트를 위해 직접 인스턴스화하는 코드를 추가
        try:
            interview_assistant = AutoGenInterviewAssistant(
                resume=resume,
                corporate_information=corporate_information,
                recruitment_information=recruitment_information,
                job_information=job_information,
                general_questions=general_questions,
                interview_style=request.interview_style,  # 면접관 스타일
                difficulty_level=request.difficulty_level  # 면접 난이도
            )
            print("Model instantiated successfully!")
        except Exception as e:
            print( traceback.format_exc())
            print(f"Error: {str(e)}")


        # 면접 시작 메시지를 보내고 결과를 반환
        response, _, _ = interview_assistant.invoke(request.user_id, "면접을 시작하세요","")
        print(response)
        interview_id = save_interview_to_db(request)
        question_id = save_question_to_db(response, interview_id)
        user = UserInUse(request.user_id, interview_assistant, question_id, interview_id)
        # 사용자 ID를 세션 ID로 사용하여 면접 모델을 관리
        interview_sessions3[request.user_id] = user
        return {"session_id": request.user_id, "message": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating interview: {str(e)}")