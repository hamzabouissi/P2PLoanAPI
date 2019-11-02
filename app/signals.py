from django.db.models.signals import post_delete,post_save
from django.dispatch import receiver
from app.models import User,Track,Loan,Notification
from twilio.rest import Client
from django.urls import reverse
 
@receiver(post_delete, sender=User)
def submission_delete(sender, instance, **kwargs):
    instance.picture.delete(False) 




def create_notif(receiver,type,desc,url=None):
    Notification.objects.create(
        receiver = receiver,
        notification_type = type,
        description=desc,
        item = url 
    )


# @receiver(post_save, sender=Track)
def notify_user(sender, instance, **kwargs):
    if instance.received:
        account_sid = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        auth_token = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        client = Client(account_sid, auth_token)

        client.messages.create(
                                body='Thanks for paying Your Payment ',
                                from_='+xxxxxx',
                                to='+216' + str(instance.loan.receiver.phone)
                                )

@receiver(post_save, sender=Loan)
def LoanNotif(instance,created,**kwargs):
    if instance.giver_acceptance ==False and instance.receiver_acceptance==False and created:
        create_notif(instance.giver,'Request','user request a loan from you ',reverse('loan-detail',args=[instance.uuid]))
    elif instance.giver_acceptance and instance.receiver_acceptance==False :
        if created:
            create_notif(instance.receiver,'Giver Request','SomeOne want to give u a loan ',reverse('loan-detail',args=[instance.uuid]))
        else:
            create_notif(instance.receiver,'Giver Accepted','Your Loan has been accepted ',reverse('loan-detail',args=[instance.uuid]))
    elif instance.receiver_acceptance:
        create_notif(instance.giver,'Loan Created','you have borrowed a money ',reverse('loan-detail',args=[instance.uuid]))



@receiver(post_save, sender=Track)
def PaymentNotif(instance,created,**kwargs):
    if created:
        create_notif(instance.loan.receiver,'Payment Info',f'Your Next Payment would be at : {instance.expected_date}',reverse('track-detail',args=[instance.id]))
    if instance.received:
        create_notif(instance.loan.receiver,'Payment Paid','Thanks for Paying Your bill',reverse('track-detail',args=[instance.id]))
