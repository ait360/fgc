import logging
from logging import CRITICAL, ERROR
import traceback
from smtplib import SMTPException
from django.contrib.auth.tokens import default_token_generator as \
    token_generator
from django.conf import settings
from django.core.mail import BadHeaderError, send_mail
from django.contrib.auth import get_user
from django.contrib.messages import success, error
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.db.models.fields.related import ManyToManyField
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.utils.text import slugify
from django.views.generic import UpdateView as BaseUpdateView


logger = logging.getLogger(__name__)


class ActivationMailFormMixin:
    mail_validation_error = ''


    def log_mail_error(self, **kwargs):
        msg_list = [
            'Activation email did not send. \n,'
            'from email: {from_email}\n'
            'subject: {subject}\n'
            'message: {message\n'
        ]
        recipient_list = kwargs.get('recipient_list', [])
        for recipient in recipient_list:
            msg_list.insert('recipient: {r}\n'.format(r=recipient))
        if 'error' in kwargs:
            level = ERROR
            error_msg = (
                'error: {0.__class__.__name__}\n'
                'args:  {0.args}\n')
            error_info = error_msg.format(kwargs['error'])
            msg_list.insert(1, error_info)
        else:
            level = CRITICAL
        msg = ''.join(msg_list).format(**kwargs)
        logger.log(level, msg)

    @property
    def mail_sent(self):
        if hasattr(self, '_mail_sent'):
            return self._mail_sent
        return False

    @mail_sent.setter
    def set_mail_sent(self, value):
        raise TypeError('Cannot set mail_set attribute')

    def get_message(self, **kwargs):
        email_template_name = kwargs.get('email_template_name')
        context = kwargs.get('context')
        return render_to_string(email_template_name, context)

    def get_subject(self, **kwargs):
        subject_template_name = kwargs.get('subject_template_name')
        context = kwargs.get('context')
        subject = render_to_string(subject_template_name, context)
        # subject must not contain newlines
        subject = ''.join(subject.splitlines())
        return subject

    def get_context_data(self, request, user, context=None):
        if context is None:
            context = dict()
        current_site = get_current_site(request)
        if request.is_secure():
            protocol = 'https'
        else:
            protocol = 'http'
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        context.update({
            'domain': current_site.domain,
            'protocol': protocol,
            'site_name': current_site.name,
            'token': token,
            'uid': uid,
            'user': user,
        })
        return context

    def _send_mail(self, request, user, **kwargs):
        kwargs['context'] = self.get_context_data(request, user)
        mail_kwargs = {
            "subject": self.get_subject(**kwargs),
            "message": self.get_message(**kwargs),
            "from_email": (settings.DEFAULT_FROM_EMAIL),
            "recipient_list": [user.email],
        }

        try:
            #number_sent will be 0 or 1
            number_sent = send_mail(**mail_kwargs)
        except Exception as error:
            self.log_mail_error(error=error, **mail_kwargs)
            if isinstance(error, BadHeaderError):
                err_code = 'badheader'
            elif isinstance(error, SMTPException):
                err_code = 'smtperror'
            else:
                err_code = 'unexpectederror'
            return (False, err_code)
        else:
            if number_sent > 0:
                return (True, None)
        self.log_mail_error(**mail_kwargs)
        return (False, 'unknownerror')

    def send_mail(self, user, **kwargs):
        request = kwargs.pop('request', None)
        if request is None:
            tb = traceback.format_stack()
            tb = [' ' + line for line in tb]
            logger.warning(
                'send_mail called without '
                'request.\nTraceback:\n{}'.format(
                    ''.join(tb)))
            self._mail_sent = False
            return self.mail_sent
        self._mail_sent, error = (self._send_mail(
                            request, user, **kwargs))
        if not self.mail_sent:
            self.add_error(
                None,  # no field - form error
                ValidationError(
                    self.mail_validation_error,
                    code=error))
        return self.mail_sent


class MailContextViewMixin:
    email_template_name = 'user/email_create.txt'
    subject_temaplate_name = ('user/subject_create.txt')

    def get_save_kwargs(self, request):
        return {
            'email_template_name': self.email_template_name,
            'request': request,
            'subject_template_name': self.subject_temaplate_name
        }

class ProfileGetObjectMixin:

    def get_object(self, queryset=None):
        current_user = get_user(self.request)
        if self.model().__class__.__name__ == 'Passenger':
            return current_user.passenger
        elif self.model().__class__.__name__ == 'LineOperator':
            return current_user.lineoperator
        elif self.model().__class__.__name__ == 'LineStaff':
            return current_user.linestaff
        elif self.model().__class__.__name__ == 'LineTripStaff':
            return current_user.linetripstaff
        else:
            return None

#def to_dict(instance):
#    opts = instance._meta
#    data = {}
#    for f in opts.concrete_fields + opts.many_to_many:
#        if isinstance(f, ManyToManyField):
#            if instance.pk is None:
#                data[f.name] = []
#            else:
#                a = f.value_from_object(instance).values_list('pk', flat=True)
#                data[f.name] = list(a)
#        else:
#            data[f.name] = f.value_from_object(instance)
#    return data


class UpdateMixin:
    models = {}
    form_classes = {}
    template_name = ''
    redirect_url_namespace=''
    initial = {}

    def get(self, request, username):
        user = get_object_or_404(self.models['user'], username__iexact=username)
        self.initial = model_to_dict(user)
        profile = get_object_or_404(self.models['profile'],
                                    slug__iexact=username)


        user_form = self.form_classes['user_form'](instance=user, initial=self.initial)
        profile_form = self.form_classes['profile_form'](instance=profile)

        context= {'user_form': user_form, 'profile_form': profile_form,
                  'user' : user, self.models['profile'].__name__.lower():profile}

        return render(request, self.template_name, context)


    @method_decorator(csrf_protect)
    def post(self, request, username):
        user = get_object_or_404(self.models['user'], username__iexact=username)
        profile = get_object_or_404(self.models['profile'],
                                    slug__iexact=username)

        if request.user.is_authenticated and request.user.id == user.id:
            user_form = self.form_classes['user_form'](request.POST, request.FILES,
                                                  instance=request.user,
                                                  initial=self.initial)
            profile_form = self.form_classes['profile_form'](request.POST,
                                request.FILES, instance=profile)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save(request=request, profile=profile)
                profile_form.save()
                success(request, _('Updated!!'))
                return redirect(self.get_success_url(username=username))
            else:
                context = {'user_form': user_form, 'profile_form': profile_form,
                  'user' : user, self.models['profile'].__name__.lower():profile}
                error(request, _('Please correct the error(s) below'))
                return render(request, self.template_name, context)

    def get_success_url(self, username):
        self.success_url = reverse_lazy('{}:{}_detail'.format(
            self.redirect_url_namespace,
            self.models['profile'].__name__.lower()), kwargs={'username':slugify(username)})
        return self.success_url


class ObjectMixin:

    def get_object(self, queryset=None):
        slug = self.kwargs.get(self.slug_url_kwarg)
        profile_object = get_object_or_404(self.model, slug__iexact=slug)

        return profile_object
