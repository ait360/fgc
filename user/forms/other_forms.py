import logging
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.messages import warning
from django.contrib.auth.forms import \
    UserCreationForm as BaseUserCreationForm
from django.utils.text import slugify
from ..models import Profile
from ..utils import ActivationMailFormMixin


logger = logging.getLogger(__name__)

class ResendActivationEmailForm(ActivationMailFormMixin, forms.Form):

    email = forms.EmailField()

    mail_validation_error = ('Could not re-send activation email. '
                             'Please try again later.  (Sorry!)')

    def save(self, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(email=self.cleaned_data['email'])
        except:
            logger.warning('Resend Acttivation: No user with '
                           'email: {} .'.format(self.cleaned_data['email']))
            return None
        self.send_mail(user=user, **kwargs)
        return user

class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = get_user_model()
        fields = ('display_picture', 'username', 'email',  'cover_picture')

    def clean_username(self):
        username = self.cleaned_data['username']
        disallowed = ('activate', 'signup', 'disable', 'login', 'logout',
                      'lineoperator', 'linetripstaff', 'linestaff', 'password')
        if username in disallowed:
            raise ValueError("A user with that username already exists.")
        return username

    def save(self, **kwargs):
        user = super().save(commit=False)
        if self.has_changed():

            if 'username' in self.changed_data:

                request = kwargs.get('request')
                profile = kwargs.get('profile')
                profile.slug=slugify(request.POST.get('username'))
                profile.save()
        user.save()
        return user