from django.urls import include, path,re_path
from rest_framework import routers
from restapi import views

router = routers.DefaultRouter()
router.register(r'^Users',views.UserViewSet)
    

urlpatterns = [
    path('UserDetail/<int:pk>',views.UserDetail.as_view(),name='user-detail'),
    path('Login',views.Login.as_view()),
    path('GithubAuth',views.GithubAuth),


    path('request',views.Request.as_view()),
    path('accept/<str:pk>',views.Accept.as_view(),name='loan-detail'),
    re_path(r'^(?P<loan>(requested|received))/(?P<loans_type>(accepted|waiting))/$',views.Loans,name='Loans'),
    path('VerifyYourself',views.VerifyYourself.as_view()),
] + router.urls