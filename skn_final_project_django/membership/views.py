from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import *
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from .tokens import account_activation_token
from .models import *
import random, json
from django.http import JsonResponse
import requests
from django.db import connections
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Max

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(email=email).exists():
            messages.error(request, '이미 존재하는 이메일입니다. 다른 이메일을 사용해주세요.')
            return render(request, 'membership/signup.html')  # 에러 메시지를 포함해 다시 회원가입 페이지로 이동
        if User.objects.filter(username=username).exists():
            messages.error(request, '이미 존재하는 유저이름입니다. 다른 유저이름을 사용해주세요.')
            return render(request, 'membership/signup.html')  # 에러 메시지를 포함해 다시 회원가입 페이지로 이동
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False  # 계정 비활성화
        user.save()

        # 이메일 인증 링크 생성
        current_site = get_current_site(request)
        mail_subject = 'Activate your account.'
        message = render_to_string('membership/account_activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        to_email = email
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()

        messages.success(request, '회원가입 신청이 처리되었습니다.\n이메일 확인을 거쳐야 정상적으로 완료됩니다.')
        #return redirect('login')
    return render(request, 'membership/signup.html')

@login_required
def delete_account_view(request):
    user = request.user
    user.delete()
    return redirect('login')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('upload_resume')  # 'upload_resume'는 URL 패턴의 이름입니다.
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['session_id'] = user.id  # 사용자 ID나 고유 값을 세션에 저장
                print(f"Session ID stored: {request.session['session_id']}")
                return redirect('upload_resume')  # 로그인 성공 후 홈으로 리다이렉트
        else:
            # 인증 실패 - 에러 메시지 설정
            messages.error(request, 'ID와 비밀번호가 일치하지 않습니다.')
            return render(request, 'membership/login.html', {'form': form})
    else:
        form = AuthenticationForm()
    return render(request, 'membership/login.html', {'form': form})

# 로그아웃 뷰
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')  # 로그아웃 후 홈으로 리다이렉트

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))  # force_text -> force_str로 수정
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('login')
    else:
        return render(request, 'activation_invalid.html')

def find_id_view(request):
    if request.method == 'POST':
        form = FindIDForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                username = user.username
                return render(request, 'membership/find_id_result.html', {'username': username})
            except User.DoesNotExist:
                error_message = '해당 이메일로 등록된 사용자가 없습니다.'
                return render(request, 'membership/find_id.html', {'form': form, 'error_message': error_message})
    else:
        form = FindIDForm()
    return render(request, 'membership/find_id.html', {'form': form})

def intro(request):
    return render(request, 'membership/intro.html')

def main(request):
    return render(request, 'membership/main.html')

def terms_view(request):
    return render(request, 'membership/terms.html')

def custom_404(request, exception):
    return render(request, 'membership/404.html', status=404)

def custom_500(request):
    return render(request, 'membership/500.html', status=500)

@login_required
def upload_resume_view(request):
    # 기업정보 조회: 같은 이름의 기업 중 업로드_일시가 가장 최근인 항목만 가져오기
    companies = CorporateInfo.objects.values('기업_이름').annotate(
        최신_업로드_일시=Max('업로드_일시')
    ).order_by('-최신_업로드_일시')

    # 최신 기업 정보만 다시 쿼리하여 가져오기
    recent_companies = CorporateInfo.objects.filter(
        기업_이름__in=[company['기업_이름'] for company in companies],
        업로드_일시__in=[company['최신_업로드_일시'] for company in companies]
    )

    # 직무정보 조회
    jobs = JobInfo.objects.all()
    # 사용자의 이력서 목록 가져오기
    resumes = Resume.objects.filter(사용자_아이디=request.user.id).order_by('-업로드_일시')[:4]  # 로그인한 사용자의 이력서만 가져오기

    context = {
        'companies': recent_companies,  # 최신 기업 정보만 포함
        'jobs': jobs,
        'resumes': resumes,
        'user': request.user,
    }
    
    return render(request, 'membership/upload_resume.html', context)

def upload_resume_to_fastapi(request):
    print(request.method)
    if request.method == "POST":
        
        file = request.FILES["file"]
        이력서_이름 = request.POST.get("이력서_이름")
        print(이력서_이름)
        try : 
            
            url = "api_url/db/upload_resume/"

            params = {
                'user_id': request.user.id,
                'resume_name': 이력서_이름
            }

            # 파일은 multipart/form-data 형식으로 전달
            files = {
                'file': (file.name, file.read(), file.content_type),
            }

            try:
                # FastAPI 서버로 POST 요청
                response = requests.post(url, params=params, files=files)
                response_data = response.json()

                if response.status_code == 200:
                    return JsonResponse({"message": "이력서가 성공적으로 업로드되었습니다."})
                else:
                    return JsonResponse({"error": response_data.get('detail', '오류가 발생했습니다.')}, status=400)
            except Exception as e :
                JsonResponse({f"error": "{e}"}, status=400)
        except Exception as e :
            JsonResponse({f"error": "{e}"}, status=400)
        
    resumes = Resume.objects.filter(사용자_아이디=request.user.id)
    print(f"사용자의 이력서 목록: {resumes}")

    return JsonResponse({"error": "잘못된 요청 방식입니다."}, status=400)

def interview_form(request):
    return render(request, 'membership/interview_form.html')

@csrf_exempt
@login_required
def question(request):
    # 세션에서 session_id와 initial_message 가져오기
    session_id = request.session.get('session_id')
    print(f"Retrieved session_id: {session_id}")
    if not session_id:
        # 세션 정보가 없으면 인터뷰 시작 페이지로 리디렉션
        return redirect('upload_resume')  # 업로드 페이지로 리디렉션

    if request.method == 'POST':
        # 사용자의 답변을 받아 FastAPI로 전송
        answer_text = request.POST.get('answer')
        if answer_text.strip() == '':
            # 빈 입력은 무시
            return redirect('question')

        data = {
            'user_id': session_id,
            'user_answer': answer_text,
        }

        # FastAPI로 답변 전송
        response = requests.post('api_url/interview/answer/', json=data)
        if response.status_code == 200:
            response_data = response.json()
            next_question = response_data.get('message')[0]
            end_signal = response_data.get('message')[1]

            if end_signal == 'end':
                # 인터뷰 종료 처리
                return redirect('interview_result')

            context = {
                'question': next_question,
            }
            return render(request, 'membership/question.html', context)
        else:
            # 오류 처리
            return render(request, 'membership/question.html', {'error': '답변 처리 중 오류가 발생했습니다.'})
    else:
        # GET 요청일 경우
        initial_message = request.session.get('initial_message')
        print(f"Retrieved initial_message: {initial_message}")
        # if not initial_message:
        #     # 초기 메시지가 없으면 인터뷰 시작 페이지로 리디렉션
        #     return redirect('upload_resume')
        context = {
            'question': initial_message,
        }
        return render(request, 'membership/question.html', context)

@csrf_exempt
@login_required
def start_interview(request):
    if request.method == 'POST':
        # 프론트엔드로부터 데이터를 받음
        data = json.loads(request.body)

        # FastAPI로 인터뷰 시작 요청을 보냄
        try:
            response = requests.post('api_url/interview/create_interview/', json=data)
            if response.status_code == 200:
                response_data = response.json()
                session_id = response_data.get('session_id')
                initial_message = response_data.get('message')

                # Django 세션에 저장
                request.session['session_id'] = session_id
                request.session['initial_message'] = initial_message

                print(f"Stored session_id: {session_id}")
                print(f"Stored initial_message: {initial_message}")

                return JsonResponse({'message': '인터뷰가 시작되었습니다.'})
            else:
                return JsonResponse({'error': '인터뷰 시작 중 오류가 발생했습니다.'}, status=500)
        except requests.exceptions.RequestException as e:
            # 네트워크 오류 처리
            return JsonResponse({'error': 'FastAPI 서버와 통신할 수 없습니다.'}, status=500)
    else:
        return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)
    
def interview_result(request):
    # 현재 로그인된 사용자 ID 가져오기
    user_id = request.session.get('session_id')  # 세션에서 사용자 ID를 가져옴
    print("user_id:", user_id)

    question_content = None
    model_answer = None
    feedback_content = None
    user_answer = None

    # 해당 사용자 ID로 총점_요약 내용을 조회
    total_summary = Result.objects.filter(사용자_아이디=user_id).values_list('총점_요약', flat=True).order_by('-면접_일시').first()
    if total_summary is None:
        total_summary = "요약 정보가 없습니다."

    # 면접 채팅 기록 가져오기
    # 사용자 ID로 해당 사용자의 가장 최근 면접기록_아이디 가져오기
    interview_record_all = Result.objects.filter(사용자_아이디=user_id).values('면접기록_아이디', '면접_일시').order_by('-면접_일시')
    latest_interview_record = Result.objects.filter(사용자_아이디=user_id).order_by('-면접_일시').first()

    # 면접기록_아이디를 기준으로 가장 최근 생성된 질문 가져오기
    all_questions = ChatMessage.objects.filter(면접기록_아이디=latest_interview_record.면접기록_아이디).order_by('생성일')
    print(all_questions)

    # 각 질문에 대한 질문_내용, 모범답변, 피드백_내용을 추출하여 리스트로 저장
    question_data = []
    for question in all_questions:
        question_content = question.질문_내용
        model_answer = question.모범답변
        feedback_content = question.피드백_내용
        user_answer = question.사용자_답변

        question_data.append({
        '질문_내용': question_content,
        '모범답변': model_answer,
        '피드백_내용': feedback_content,
        '사용자_답변': user_answer
    })
    
    context = {
        'messages': messages,
        'overall_comment': total_summary,
        'question_data': question_data,  # 추가된 질문 데이터
        'interview_record_all': interview_record_all
    }

    # HTML 템플릿에 총점_요약 내용을 전달
    return render(request, 'membership/interview_result.html', context)

def delete_resume(request, resume_id):
    if request.method == 'DELETE':
        try:
            resume = Resume.objects.get(이력서_아이디=resume_id)
            resume.delete()
            return JsonResponse({'success': True})
        except Resume.DoesNotExist:
            return JsonResponse({'success': False, 'error': '이력서가 존재하지 않습니다.'})
    return JsonResponse({'success': False, 'error': '올바른 요청이 아닙니다.'})

def get_jobs_by_company(request, company_id):
    jobs = JobInfo.objects.filter(기업정보_아이디=company_id).values('직무정보_아이디', '직무_이름')
    print(jobs)
    return JsonResponse(list(jobs), safe=False)

def get_interview_details(request, interview_id):
    try:
        # 해당 면접기록에 대한 총점_요약 가져오기
        total_summary = Result.objects.filter(면접기록_아이디=interview_id).values_list('총점_요약', flat=True).first()
        if total_summary is None:
            total_summary = "요약 정보가 없습니다."

        # 해당 면접기록 ID에 대한 질문 및 답변 정보 가져오기
        all_questions = ChatMessage.objects.filter(면접기록_아이디=interview_id).order_by('생성일')
        print(ChatMessage.objects.filter(면접기록_아이디=interview_id))
        question_data = [
            {
                '질문_내용': question.질문_내용,
                '모범답변': question.모범답변,
                '피드백_내용': question.피드백_내용,
                '사용자_답변': question.사용자_답변
            }
            for question in all_questions
        ]

        # JSON으로 반환
        return JsonResponse({
            'overall_comment': total_summary,
            'questions': question_data
        })

    except Result.DoesNotExist:
        return JsonResponse({'error': '해당 면접 기록을 찾을 수 없습니다.'}, status=404)