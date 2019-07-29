from django.urls import include, path,re_path
from rest_framework import routers
from restapi import views

router = routers.DefaultRouter()
router.register(r'users',views.UserViewSet)   

urlpatterns = [
    # path('Users/',views.UserList.as_view(),name='users-list'),
    # path('UserDetail/<int:pk>',views.UserDetail.as_view(),name='user-detail'),

    path('registration',views.Registration.as_view(),name='registration'),
    path('Login',views.Login.as_view()),
    path('GithubAuth',views.GithubAuth),

    path('Loan/<str:pk>',views.LoanDetail.as_view(),name='loan-detail'),
    path('request',views.Request.as_view()),
    path('accept/<str:pk>',views.Accept.as_view(),name='loans-detail'),
    path('VerifyYourself',views.VerifyYourself.as_view()),
    re_path(r'^(?P<loan>(requested|received))/(?P<loans_type>(accepted|waiting))/$',views.Loans,name='Loans'),
    path('track/<int:pk>',views.TrackDetail.as_view(),name='track-detail'),
] + router.urls