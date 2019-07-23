from django.db.models.signals import post_delete
from django.dispatch import receiver
from app.models import User
 
 

 
@receiver(post_delete, sender=User)
def submission_delete(sender, instance, **kwargs):
    instance.picture.delete(False) 