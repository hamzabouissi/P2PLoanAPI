from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
import os,urllib
from django.conf import settings


def downloader(image_url,username):

    
    urllib.request.urlretrieve(image_url,username)

class CustomSocialAdapter(DefaultSocialAccountAdapter):


    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social login. In case of auto-signup,
        the signup form is not available.
        """
        u = sociallogin.user
        info = sociallogin.serialize()
        if info['account']['provider']=='github':
            url = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT)
            file_name = url + info['account']['provider'] + info['account']['extra_data']['name' ] + '.jpg'
            downloader(info['account']['extra_data']['avatar_url'] , file_name)
            u.picture = file_name
        super().save_user(request,sociallogin,form)
   




 