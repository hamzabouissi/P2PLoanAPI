from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
import requests

from django.core.files import File
from tempfile import NamedTemporaryFile


class CustomSocialAdapter(DefaultSocialAccountAdapter):


    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social login. In case of auto-signup,
        the signup form is not available.
        """
        u = sociallogin.user
        info = sociallogin.serialize()
        url = info['account']['extra_data']['avatar_url']
        file_name = info['account']['provider'] + info['account']['extra_data']['name' ] + '.jpg'
        if info['account']['provider']=='github':
            if not u.picture:
                with NamedTemporaryFile(delete=True) as img_temp:
                    r = requests.get(url)
                    img_temp.write(r.content)
                    img_temp.flush()
                    u.picture.save(file_name,File(img_temp),save=True)
        super().save_user(request,sociallogin,form)
   




 