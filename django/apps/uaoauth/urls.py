from django.urls import re_path as url
from .views import UAOauthLoginView


urlpatterns = [
    url(r'redirect_auth/', UAOauthLoginView.as_view()),
]
