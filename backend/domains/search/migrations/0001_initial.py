# Generated migration for search domain

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='SearchHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(blank=True, db_index=True, null=True, verbose_name='User ID')),
                ('query', models.TextField(verbose_name='Original Query')),
                ('keywords', models.JSONField(default=list, verbose_name='Extracted Keywords')),
                ('category', models.CharField(blank=True, max_length=100, verbose_name='Category')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
            ],
            options={
                'verbose_name': 'Search History',
                'verbose_name_plural': 'Search History List',
                'ordering': ['-created_at'],
            },
        ),
    ]
