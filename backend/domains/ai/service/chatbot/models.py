from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ChatSession(models.Model):
    """
    사용자의 챗봇 대화 세션
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions",
        null=True,
        blank=True,
        help_text=_("세션 소유자 (비로그인 시 null 가능)"),
    )
    title = models.CharField(max_length=255, default="New Chat", verbose_name=_("세션 제목"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = _("채팅 세션")
        verbose_name_plural = _("채팅 세션 목록")

    def __str__(self):
        return f"{self.title} ({self.updated_at.strftime('%Y-%m-%d %H:%M')})"


class ChatMessage(models.Model):
    """
    개별 채팅 메시지 (User <-> Assistant)
    """

    ROLE_CHOICES = [
        ("user", "사용자"),
        ("assistant", "AI 상담사"),
        ("system", "시스템"),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages", verbose_name=_("세션"))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField(verbose_name=_("메시지 내용"))
    sources = models.JSONField(
        default=list, blank=True, verbose_name=_("참조 출처 (제품/문서)"), help_text=_("검색된 상품 정보 등 JSON 저장")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("채팅 메시지")
        verbose_name_plural = _("채팅 메시지 목록")

    def __str__(self):
        return f"[{self.role}] {self.content[:30]}..."
