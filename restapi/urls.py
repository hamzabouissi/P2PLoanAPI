from django.urls import include, path,re_path
from rest_framework import routers
from restapi import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r'users',views.UserViewSet)

urlpatterns = [
   

    path('registration/',views.Registration.as_view(),name='registration'),
    path('login/',views.Login.as_view(),name='login'),
    path('password/reset',views.password_reset,name='password-reset'),
    path('password/reset/complete',views.password_reset_complete,name='password-reset-complete'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),



    
    path('Loan/<str:uuid>',views.LoanDetail.as_view(),name='loan-detail'),
    path('request/',views.Request.as_view(),name='request-loan'),
    path('accept/<uuid:Loan_uuid>',views.Accept.as_view(),name='accept'),
    path('Loan/',views.Loans.as_view(),name='Loan'),
    path('track/<int:pk>',views.TrackDetail.as_view(),name='track-detail'),
    path('notifs/',views.NotifList.as_view(),name='notif-list'),
    path('notif/<int:pk>',views.NotifDetail.as_view(),name='notif-detail')
] + router.urls