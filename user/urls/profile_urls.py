from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm
from django.urls import path, re_path, include
from django.urls import reverse_lazy
from django.views.generic import RedirectView, TemplateView
from ..views import profile_views

app_name='user'
urlpatterns = [
    path('signup/', profile_views.ProfileSignup.as_view(),
                        name='profile_signup'),
    re_path(r'^(?P<username>[\w\-]+)/$', profile_views.ProfileDetail.as_view(),
                        name='profile_detail'),
    re_path(r'^(?P<username>[\w\-]+)/edit/$', profile_views.ProfileUpdate.as_view(),
                        name='profile_update'),
]