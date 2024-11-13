from django.contrib.auth.models import AbstractUser, Permission, Group
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
import uuid

class CustomUser(AbstractUser):
    # 추가 필드가 필요하다면 여기에 작성
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # related_name을 추가하여 충돌 해결
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='customuser_set',  # related_name 추가
        help_text='Specific permissions for this user.',
    )

class Membership(AbstractBaseUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username
    
# class ChatMessage(models.Model):
#     MESSAGE_TYPES = (
#         ('question', 'Question'),
#         ('answer', 'Answer'),
#     )
#     text = models.TextField()
#     message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.get_message_type_display()}: {self.text[:20]}"
    
class Feedback(models.Model):
    overall_comment = models.TextField()
    strengths = models.TextField()
    weaknesses = models.TextField()
    advice = models.TextField()

    def __str__(self):
        return "면접 피드백"
    
class Resume(models.Model):
    이력서_아이디 = models.CharField(max_length=36, primary_key=True)
    사용자_아이디 = models.IntegerField(default=1)  # 사용자 테이블과의 연결
    이력서_이름 = models.CharField(max_length=36)
    이력서_파일 = models.TextField()  # 파일을 저장하는 컬럼
    이력서_전처리 = models.TextField(null=True, blank=True)
    업로드_일시 = models.DateTimeField(auto_now_add=True, null=True)
    수정_일시 = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '이력서'  # MySQL의 실제 테이블 이름

class CorporateInfo(models.Model):
    기업정보_아이디 = models.CharField(max_length=36, primary_key=True, db_column='기업정보_아이디')
    기업_이름 = models.CharField(max_length=36, db_column='기업_이름')
    기업_파일 = models.TextField(db_column='기업_파일')
    기업_전처리 = models.TextField(null=True, blank=True, db_column='기업_전처리')
    업로드_일시 = models.DateTimeField(null=True, blank=True, db_column='업로드_일시')
    수정_일시 = models.DateTimeField(null=True, blank=True, db_column='수정_일시')

    class Meta:
        db_table = '기업정보'
        managed = False

    def __str__(self):
        return self.기업_이름

class JobInfo(models.Model):
    직무정보_아이디 = models.CharField(max_length=36, primary_key=True, db_column='직무정보_아이디')
    기업정보_아이디 = models.CharField(max_length=36, db_column='기업정보_아이디')
    직무_이름 = models.CharField(max_length=36, db_column='직무_이름')
    직무_파일 = models.TextField(db_column='직무_파일')
    직무_전처리 = models.TextField(null=True, blank=True, db_column='직무_전처리')
    업로드_일시 = models.DateTimeField(null=True, blank=True, db_column='업로드_일시')
    수정_일시 = models.DateTimeField(null=True, blank=True, db_column='수정_일시')

    class Meta:
        db_table = '직무정보'
        managed = False

    def __str__(self):
        return self.직무_이름

class Result(models.Model):
    면접기록_아이디 = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)
    사용자_아이디 = models.IntegerField()
    직무정보_아이디 = models.UUIDField()
    채용정보_아이디 = models.UUIDField()
    면접_유형 = models.CharField(max_length=50)  # 예: soft, hard, etc.
    난이도 = models.IntegerField()
    피드백 = models.TextField(null=True, blank=True)
    면접_일시 = models.DateTimeField()
    총점_요약 = models.TextField(null=True, blank=True)

    class Meta:
        db_table = '면접기록'  # MySQL의 실제 테이블 이름
        managed = False

class ChatMessage(models.Model):
    질문_아이디 = models.UUIDField(primary_key=True)  # 기본 키로 UUID 사용
    면접기록_아이디 = models.CharField(max_length=36)  # 외래 키로 사용될 수 있는 UUID 필드
    질문_내용 = models.TextField()  # 질문 내용 (텍스트 필드)
    모범답변 = models.TextField(null=True, blank=True)  # 모범 답변 (텍스트 필드)
    생성일 = models.DateTimeField()  # 생성일 (날짜 및 시간 필드)
    사용자_답변 = models.TextField(null=True, blank=True)  # 사용자 답변 (텍스트 필드)
    피드백_내용 = models.TextField(null=True, blank=True)  # 피드백 내용 (텍스트 필드)
    음성_감정 = models.CharField(max_length=50, null=True, blank=True)  # 음성 감정 (문자열 필드)
    이미지_감정 = models.CharField(max_length=50, null=True, blank=True)  # 이미지 감정 (문자열 필드)

    class Meta:
        db_table = '질문'  # 테이블 이름 설정
        managed = False