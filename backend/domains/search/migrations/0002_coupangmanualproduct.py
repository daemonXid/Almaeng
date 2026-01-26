# Generated manually for CoupangManualProduct model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoupangManualProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.CharField(db_index=True, help_text='쿠팡 상품 고유 ID', max_length=100, unique=True, verbose_name='상품 ID')),
                ('name', models.CharField(max_length=500, verbose_name='상품명')),
                ('price', models.IntegerField(help_text='원 단위', verbose_name='가격')),
                ('image_url', models.URLField(max_length=1000, verbose_name='이미지 URL')),
                ('affiliate_url', models.URLField(help_text='수동 생성한 쿠팡 파트너스 링크', max_length=1000, verbose_name='파트너스 링크')),
                ('category', models.CharField(blank=True, help_text='예: 건강식품, 운동용품, 전자제품 등', max_length=100, verbose_name='카테고리')),
                ('keywords', models.JSONField(default=list, help_text='검색에 사용될 키워드 리스트', verbose_name='검색 키워드')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='활성화')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='등록일')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일')),
            ],
            options={
                'verbose_name': '쿠팡 수동 상품',
                'verbose_name_plural': '쿠팡 수동 상품 목록',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['is_active', '-created_at'], name='search_coup_is_acti_idx'),
                    models.Index(fields=['category', 'is_active'], name='search_coup_categor_idx'),
                ],
            },
        ),
    ]
