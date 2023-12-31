# Generated by Django 4.2 on 2023-06-12 18:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('urunler', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Odeme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.IntegerField()),
                ('odendiMi', models.BooleanField(default=False)),
                ('odeme_tarih', models.DateTimeField(auto_now_add=True)),
                ('urunler', models.ManyToManyField(to='urunler.urun')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
