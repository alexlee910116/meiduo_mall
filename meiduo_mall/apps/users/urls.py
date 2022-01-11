from django.urls import path
from apps.users.views import UsernameCountView,MobileCountView,RegisterView

urlpatterns = [
    path('usernames/<username:username>/count/',UsernameCountView.as_view()),
    path('mobile/<mobile:mobile>/count/',MobileCountView.as_view()),
    path('register/',RegisterView.as_view()),
]