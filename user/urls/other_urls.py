from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm
from django.urls import path, re_path, include
from django.urls import reverse_lazy
from django.views.generic import RedirectView, TemplateView
from ..views import other_views



app_name='user'

password_urls = [
    path('', RedirectView.as_view(
                pattern_name='other_urls:pw_reset_start',
                permanent=False)),
    path('change/', auth_views.PasswordChangeView.as_view(
                template_name='user/password_change_form.html',
                success_url=reverse_lazy('other_urls:pw_change_done')),
                name='pw_change'),
    path('change/done/', auth_views.PasswordChangeDoneView.as_view(
                template_name='user/password_change_done.html'),
                name='pw_change_done'),
    path('reset/', auth_views.PasswordResetView.as_view(
                template_name='user/password_reset_form.html',
                email_template_name='user/password_reset_email.txt',
                subject_template_name='user/password_reset_subject.txt',
                success_url=reverse_lazy('other_urls:pw_reset_sent')),
                name='pw_reset_start'),
    path('reset/sent/', auth_views.PasswordResetDoneView.as_view(
                template_name='user/password_reset_sent.html'),
                name='pw_reset_sent'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
            r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1, 20})/$',
                auth_views.PasswordResetConfirmView.as_view(
                template_name='user/password_reset_confirm.html',
                success_url=reverse_lazy('other_urls:pw_reset_complete')),
                name='pw_reset_comfirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
                template_name='user/password_reset_complete.html',
                extra_context={'form': AuthenticationForm}),
                name='pw_reset_complete'),

]


urlpatterns = [
    path('', RedirectView.as_view(pattern_name='other_urls:login',
                                  permanent=False)),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/'
            r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            other_views.ActivateAccount.as_view(), name='activate'),
    path('activate/', RedirectView.as_view(pattern_name='other_urls:resend_activation',
                                           permanent=False)),
    path('activate/resend/', other_views.ResendActivationEmail.as_view(),
         name='resend_activation'),
    path('disable/', other_views.DisableAccount.as_view(), name='disable'),
    path('login/', other_views.LoginView.as_view(
        template_name='user/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='user/logged_out.html',
        extra_context={'form': AuthenticationForm}),
         name='logout'),
    path('password/', include(password_urls)),
    path('signup/done/', TemplateView.as_view(
        template_name='user/user_signup_done.html'),
        name='signup_done'),
]
