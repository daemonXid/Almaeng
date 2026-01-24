"""
Migration: Add embedding fields for vector search

Adds VectorField to Supplement and MFDSHealthFood models for pgvector-based similarity search.
"""

from django.db import migrations
import pgvector.django


def enable_vector_extension(apps, schema_editor):
    """Enable pgvector extension"""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")


def disable_vector_extension(apps, schema_editor):
    """Disable pgvector extension"""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("DROP EXTENSION IF EXISTS vector;")


class Migration(migrations.Migration):

    dependencies = [
        ('supplements', '0002_supplement_benefits_supplement_description_and_more'),
    ]

    operations = [
        # Enable pgvector extension
        migrations.RunPython(
            enable_vector_extension,
            reverse_code=disable_vector_extension,
        ),
        # Add embedding field to Supplement
        migrations.AddField(
            model_name='supplement',
            name='embedding',
            field=pgvector.django.VectorField(
                dimensions=768,
                null=True,
                blank=True,
                verbose_name='임베딩 벡터',
                help_text='제품 설명 및 성분 정보의 벡터 표현 (Gemini embedding-001)'
            ),
        ),
        # Add embedding field to MFDSHealthFood
        migrations.AddField(
            model_name='mfdshealthfood',
            name='embedding',
            field=pgvector.django.VectorField(
                dimensions=768,
                null=True,
                blank=True,
                verbose_name='임베딩 벡터',
                help_text='제품명, 기능성, 원재료 정보의 벡터 표현 (Gemini embedding-001)'
            ),
        ),
        # Add HNSW indexes for vector similarity search (pgvector)
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS supplement_embedding_idx 
            ON supplements_supplement 
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
            """,
            reverse_sql="DROP INDEX IF EXISTS supplement_embedding_idx;",
        ),
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS mfds_embedding_idx 
            ON supplements_mfdshealthfood 
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
            """,
            reverse_sql="DROP INDEX IF EXISTS mfds_embedding_idx;",
        ),
    ]
