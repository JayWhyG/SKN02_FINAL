from django.contrib.auth.backends import BaseBackend
from .models import Membership  # membership 테이블 모델을 참조
from django.contrib.auth.hashers import check_password

class MembershipBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            # membership 테이블에서 사용자 찾기
            user = Membership.objects.get(username=username)

            # 비밀번호를 확인 (비밀번호가 해싱되어 있다면 check_password 사용)
            if check_password(password, user.password):
                return user
        except Membership.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Membership.objects.get(pk=user_id)
        except Membership.DoesNotExist:
            return None