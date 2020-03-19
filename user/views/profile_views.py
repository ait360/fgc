from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import get_user, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.messages import error, success
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import DetailView, View

from ..forms.profile_forms import ProfileCreationForm, ProfileUpdateForm
from ..forms.other_forms import UserUpdateForm
from ..models import Profile
from ..utils import MailContextViewMixin, ProfileGetObjectMixin, UpdateMixin, ObjectMixin


User = get_user_model()

class ProfileSignup(MailContextViewMixin, View):
        form_class = ProfileCreationForm
        success_url = reverse_lazy('other_urls:signup_done')
        template_name = 'user/user_signup.html'

        def get_context_data(self, **kwargs):
            kwargs['user_type'] = 'Passenger'
            return super().get_context_data(**kwargs)

        @method_decorator(csrf_protect)
        def get(self, request):
            return TemplateResponse(request, self.template_name,
                                    {'form': self.form_class(), 'user_type' : 'member'})

        @method_decorator(csrf_protect)
        @method_decorator(sensitive_post_parameters('password1', 'password2'))
        def post(self, request):
            bound_form = self.form_class(request.POST)
            if bound_form.is_valid():
                # no catching return user
                bound_form.save(**self.get_save_kwargs(request))
                if bound_form.mail_sent:  # mail sent?
                    return redirect(self.success_url)
                else:
                    errs = (bound_form.non_field_errors())
                    for err in errs:
                        error(request, err)
                    return redirect('other_urls:resend_activation')
            return TemplateResponse(request, self.template_name,
                                    {'form': bound_form})


@method_decorator(login_required, name='dispatch')
class ProfileDetail(ObjectMixin, DetailView):
    model = Profile
    slug_url_kwarg = 'username'
    context_object_name = 'profile'


@method_decorator(login_required, name='dispatch')
class ProfileUpdate(UpdateMixin, View):
    models = {'user': User, 'profile': Profile}
    form_classes = {'user_form':UserUpdateForm,
                    'profile_form':ProfileUpdateForm}
    template_name = 'user/profile_update.html'
    redirect_url_namespace = 'profile_urls'

