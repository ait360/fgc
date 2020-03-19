from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse

from django.contrib.auth.validators import UnicodeUsernameValidator
from .validators import PhoneNumberValidator





class Profile(models.Model):

    ABIA = 'AB'
    ADAMAWA = 'AD'
    AKWA_IBOM = 'AI'
    ANAMBRA = 'AN'
    BAUCHI = 'BA'
    BAYELSA = 'BAY'
    BENUE = 'BE'
    BORNO = 'BO'
    CROSS_RIVER = 'CR'
    DELTA = 'DE'
    EBONYI = 'EB'
    EDO = 'ED'
    EKITI = 'EK'
    ENUGU = 'EN'
    GOMBE = 'GO'
    IMO = 'IM'
    JIGAWA = 'JI'
    KADUNA = 'KA'
    KANO = 'KAN'
    KATSINA = 'KAT'
    KEBBI = 'KE'
    KOGI = 'KO'
    KWARA = 'KW'
    LAGOS = 'LA'
    NASARAWA = 'NA'
    NIGER = 'NI'
    OGUN = 'OG'
    ONDO = 'ON'
    OSUN = 'OS'
    OYO = 'OY'
    PLATEAU = 'PL'
    RIVERS = 'RI'
    SOKOTO = 'SO'
    TARABA = 'TA'
    YOBE = 'YO'
    ZAMFARA = 'ZA'
    FCT = 'FCT'

    STATE_CHOICES = [(ABIA, 'Abia'), (ADAMAWA, 'Adamawa'), (AKWA_IBOM, 'Akwa Ibom'),
                     (ANAMBRA, 'Anambra'), (BAUCHI, 'Bauchi'), (BAYELSA, 'Bayelsa'),
                     (BENUE, 'Benue'), (BORNO, 'Borno'), (CROSS_RIVER, 'Cross River'),
                     (DELTA, 'Delta'), (EBONYI, 'Ebonyi'), (EDO, 'Edo'),
                     (EKITI, 'Ekiti'), (ENUGU, 'Enugu'), (GOMBE, 'Gombe'),
                     (IMO, 'Imo'), (JIGAWA, 'Jigawa'), (KADUNA, 'Kaduna'),
                     (KANO, 'Kano'), (KATSINA, 'Katsina'), (KEBBI, 'Kebbi'),
                     (KOGI, 'Kogi'), (KWARA, 'Kwara'), (LAGOS, 'Lagos'),
                     (NASARAWA, 'Nasarawa'), (NIGER, 'Niger'), (OGUN, 'Ogun'),
                     (ONDO, 'Ondo'), (OSUN, 'Osun'), (OYO, 'Oyo'),
                     (PLATEAU, 'Plateau'), (RIVERS, 'Rivers'), (SOKOTO, 'Sokoto'),
                     (TARABA, 'Taraba'), (YOBE, 'Yobe'), (ZAMFARA, 'Zamfara'),
                     (FCT, 'FCT Abuja')]

    phone_number_validator = PhoneNumberValidator()

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(_('your first name'), max_length=150,
                            help_text=_('Required for first name '
                                        'of alumnus'))
    last_name = models.CharField(_('your last name'), max_length=150,
                                 help_text=_('Required for last name '
                                             'of alumnus'))
    current_state = models.CharField(_('your current state'), max_length=3, choices=STATE_CHOICES)
    current_city = models.CharField(_('your current city/town'), max_length=150,
                                    help_text=_('Required for current city of alumnus'))
    WhatsApp_phone_number = models.CharField(_('your WhatsApp Phone number'),
                                             max_length=11,
                                             help_text=_('Required for WhatsApp'
                                                         ' Phone number'),
                                             validators=[phone_number_validator],
                                             unique=True,
                                             error_messages={
                                                 'unique': _("A user with that phone number already exists."),
                                             },)

    address = models.CharField(_('member address'), max_length=255,
                               help_text=_('Required for easy contact'))
    slug = models.SlugField(max_length=255, unique=True)
    bio = models.TextField()

    def __str__(self):
        return self.user.get_username()

    def get_update_url(self):
        return reverse('profile_urls:profile_update', kwargs={'username': self.slug})

    def get_absolute_url(self):
        return reverse('profile_urls:profile_detail', kwargs={'username': self.slug})



class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):

        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_boss', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_member', True)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field : username})

def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.username, filename)


def user_cover_path(instance, filename):
    return 'user_cover_{0}/{1}'.format(instance.username, filename)


class User(AbstractBaseUser, PermissionsMixin):

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_('email address'), blank=False, unique=True)
    display_picture = models.ImageField(upload_to=user_directory_path, blank=True)
    cover_picture = models.ImageField(upload_to=user_cover_path, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts'
        )
    )

    is_boss = models.BooleanField(
        _('Boss'),
        default=False,
        help_text=_('Designates whether this user should be treated as a site boss')
    )

    is_member = models.BooleanField(
        _('Member'),
        default=False,
        help_text=_('Designates whether this user should be treated as a site member')
    )



    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


    def __str__(self):
        return self.username

    def get_absolute_url(self):
        pass

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

