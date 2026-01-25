"""
🔍 Search State Models

검색 히스토리 모델.
"""

from django.db import models


class SearchHistory(models.Model):
    """검색 히스토리"""

    user_id = models.IntegerField(db_index=True, null=True, blank=True, verbose_name="사용자 ID")
    query = models.TextField(verbose_name="원본 질문")
    keywords = models.JSONField(default=list, verbose_name="추출된 키워드")
    category = models.CharField(max_length=100, blank=True, verbose_name="카테고리")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="검색 시각")

    class Meta:
        verbose_name = "검색 히스토리"
        verbose_name_plural = "검색 히스토리 목록"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.query} ({self.created_at})"
