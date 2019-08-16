from django.contrib import admin
from app.models import User, Loan,Track, Citizien,Notification

# Register your models here.

admin.site.register(User)
admin.site.register(Loan)
admin.site.register(Track)
admin.site.register(Citizien)
admin.site.register(Notification)


