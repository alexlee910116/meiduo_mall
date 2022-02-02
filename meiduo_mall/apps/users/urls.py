from django.urls import path
from apps.users.views import UsernameCountView, MobileCountView, RegisterView, LoginView, LogoutView
from apps.users.views import InfoView, EmailView, EmailVerifyView
from apps.users.views import AddressCreateView, AddressView, UpdateDestroyAddressView, DefaultAddressView, UpdateTitleAddressView

urlpatterns = [
    path('usernames/<username:username>/count/', UsernameCountView.as_view()),
    path('mobile/<mobile:mobile>/count/', MobileCountView.as_view()),
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('info/', InfoView.as_view()),
    path('emails/', EmailView.as_view()),
    path('emails/verification/', EmailVerifyView.as_view()),
    path('addresses/create/', AddressCreateView.as_view()),
    path('addresses/', AddressView.as_view()),
    path('addresses/<address_id>/', UpdateDestroyAddressView.as_view()),
    path('addresses/<address_id>/default/', DefaultAddressView.as_view()),
    path('addresses/<address_id>/title/', UpdateTitleAddressView.as_view()),
]
