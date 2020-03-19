import logging
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import \
    UserCreationForm as BaseUserCreationForm
from django.utils.text import slugify
from ..models import Profile
from ..utils import ActivationMailFormMixin


logger = logging.getLogger(__name__)



class ProfileCreationForm(ActivationMailFormMixin, BaseUserCreationForm):

    mail_validation_error = ('User created. Could not send activation '
                             'email. Please try again later. (Sorry!)')

    class Meta(BaseUserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'email')

    def clean_username(self):
        username = self.cleaned_data['username']
        disallowed = ('activate', 'signup', 'disable', 'login', 'logout',
                      'password', 'posts', 'tags', 'post', 'tag', 'ckeditor',
                      'admin')
        if username in disallowed:
            raise ValueError("A user with that username already exists.")
        if username and get_user_model().objects.filter(username__iexact=username).exists():
            self.add_error('username', 'A user with that username already exists.')
        return username

    def save(self, **kwargs):
        user = super().save(commit=False)
        if not user.pk:
            user.is_active = False
            user.is_member = True
            send_mail = True
        else:
            send_mail = False
        user.save()
        self.save_m2m()
        Profile.objects.update_or_create(user=user,
                                              defaults={'slug': slugify(
                                                  user.get_username()),})
        if send_mail:
            self.send_mail(user=user, **kwargs)


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'bio', 'current_state',
                  'current_city', 'WhatsApp_phone_number',
                  'address',)
                  #'next_of_kin_mobile', )

