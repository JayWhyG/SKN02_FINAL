import requests
import ormsgpack

def generate_tts_audio_IU(text, output_path="output_audio.wav"):
    """
    TTS API를 호출하여 텍스트 기반 음성을 생성하고 저장합니다.
    
    Parameters:
        text (str): 생성할 텍스트.
        reference_audio_path (str): 참조 오디오 파일의 경로 (mp3 형식).
        reference_text (str): 참조 오디오의 텍스트 내용.
        output_path (str): 생성된 음성을 저장할 파일 경로. 기본값은 "output_audio.wav".
    
    Returns:
        str: 성공 시 저장된 파일 경로를 반환, 실패 시 오류 메시지를 반환.
    """
    url = "http://127.0.0.1:8080/v1/tts"
    
    # 참조 오디오 파일 로드
    with open("아이유 모닝콜mp3.mp3", "rb") as f:
        audio_data = f.read()

    # 요청 데이터 준비
    data = {
        "text": text,
        "references": [{"audio": audio_data, "text": "일어나. 일어나야지! 지금 너 이거 또, 또, 십 분으로 또, 미루면 문제 있어. 일어나. 하루 다 갔어. 지금. 해 중천이야. 일어나."}],
        "max_new_tokens": 200,
        "chunk_length": 100,
        "top_p": 0.7,
        "repetition_penalty": 1.2,
        "temperature": 0.7,
        "streaming": False,
    }

    headers = {"Content-Type": "application/msgpack"}

    # 데이터 직렬화
    serialized_data = ormsgpack.packb(data)

    # API 요청
    response = requests.post(url, data=serialized_data, headers=headers)

    # 응답 확인
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        return f"TTS audio generated successfully! Saved at {output_path}"
    else:
        return f"요청 실패: 상태 코드 {response.status_code}\n에러 메시지: {response.text}"
    
if __name__=="__main__" :
    # 사용 예시
    result = generate_tts_audio_IU(
        text="이 텍스트를 기반으로 음성을 생성해줘"
    )
    print(result)
