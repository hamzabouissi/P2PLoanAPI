# Generated by Django 2.2.3 on 2019-08-15 09:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_notification_creation_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loan',
            name='final_amount',
        ),
    ]