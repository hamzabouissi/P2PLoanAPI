from django.db.models.signals import post_delete,post_save
from django.dispatch import receiver
from app.models import User,Track
from twilio.rest import Client


 
@receiver(post_delete, sender=User)
def submission_delete(sender, instance, **kwargs):
    instance.picture.delete(False) 


@receiver(post_save, sender=Track)
def notify_user(sender, instance, **kwargs):
    if instance.received:
        account_sid = 'AC42027c436d422a348e2a58d339c05e39'
        auth_token = '8c2905e74b9ed8165fdd3e5401e23be3'
        client = Client(account_sid, auth_token)

        client.messages.create(
                                body='Thanks for paying Your Payment ',
                                from_='+18652902955',
                                to='+216' + str(instance.loan.receiver.phone)
                                )
