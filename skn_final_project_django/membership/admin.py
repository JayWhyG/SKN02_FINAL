from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ChatMessage

# CustomUser 모델을 관리자 페이지에 등록
admin.site.register(CustomUser, UserAdmin)
admin.site.register(ChatMessage)
