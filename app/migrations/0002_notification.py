# Generated by Django 2.2.3 on 2019-08-09 20:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(max_length=25)),
                ('notification_type', models.CharField(max_length=25)),
                ('item', models.URLField(blank=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notif', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
