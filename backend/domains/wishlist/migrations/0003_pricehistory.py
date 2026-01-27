# Generated manually for PriceHistory model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wishlist', '0002_pricealert'),
    ]

    operations = [
        migrations.CreateModel(
            name='PriceHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField(verbose_name='Price')),
                ('checked_at', models.DateTimeField(auto_now_add=True, verbose_name='Checked At')),
                ('wishlist_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_history', to='wishlist.wishlistitem')),
            ],
            options={
                'verbose_name': 'Price History',
                'verbose_name_plural': 'Price Histories',
                'db_table': 'price_history',
                'ordering': ['-checked_at'],
            },
        ),
        migrations.AddIndex(
            model_name='pricehistory',
            index=models.Index(fields=['wishlist_item', '-checked_at'], name='price_histo_wishlis_idx'),
        ),
    ]
