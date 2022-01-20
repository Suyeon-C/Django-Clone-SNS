from django.urls import path
from .views import *

urlpatterns = [
    path('signup',Signup.as_view(), name='signup'),
    path('success',Success.as_view(), name='success'),
    path('login',Login.as_view(), name='login'),
    path('logout',Logout.as_view(), name='logout'),
    path('email/search',Ajax_email_search.as_view(), name='email_search'),
    path('pw/auth/send',Ajax_pw_auth_send.as_view(), name='pw_search'),
    path('pw/auth/confirm',Ajax_pw_auth_confirm.as_view(), name='pw_auth_confirm'),
    path('pw/change',auth_pw_reset_view,name='pw_change'),
    path('profile',Profile.as_view(), name='profile'),
    path('update',UpdateProfile.as_view(),name='update'),
    path('insert/follow',InsertFollow.as_view(),name='insert_follow'),
]