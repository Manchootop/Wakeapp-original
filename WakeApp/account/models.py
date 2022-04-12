from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models

from WakeApp.account.managers import WakeAppUserManager


def get_profile_image_filepath(self, filename):
    return f'profile_images/{self.pk}/profile_image.png'


def get_default_image():
    return 'default_image/logo.png'


def validate_only_letters(value):
    if not all(ch.isalpha() for ch in value):
        raise ValidationError('Value must contain only letters')


class WakeAppUser(AbstractBaseUser, PermissionsMixin):
    USERNAME_MAX_LENGTH = 30

    # email = models.CharField(
    #     max_length=USERNAME_MAX_LENGTH,
    #     unique=True,
    # )

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
    )

    date_joined = models.DateTimeField(
        auto_now_add=True,
    )

    is_staff = models.BooleanField(
        default=False,
    )

    USERNAME_FIELD = 'username'

    objects = WakeAppUserManager()


class Profile(models.Model):
    FIRST_NAME_MIN_LENGTH = 2
    FIRST_NAME_MAX_LENGTH = 30
    LAST_NAME_MIN_LENGTH = 2
    LAST_NAME_MAX_LENGTH = 30

    MALE = 'Male'
    FEMALE = 'Female'
    DO_NOT_SHOW = 'Do not show'

    GENDERS = [(x, x) for x in (MALE, FEMALE, DO_NOT_SHOW)]

    first_name = models.CharField(
        max_length=FIRST_NAME_MAX_LENGTH,
        validators=(
            MinLengthValidator(FIRST_NAME_MIN_LENGTH),
            validate_only_letters,
        )
    )

    last_name = models.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
        validators=(
            MinLengthValidator(LAST_NAME_MIN_LENGTH),
            validate_only_letters,
        )
    )

    profile_image = models.ImageField(
        max_length=255,
        upload_to=None,
        null=get_profile_image_filepath,
        blank=True,
        default=get_default_image,
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )

    description = models.TextField(
        null=True,
        blank=True,
    )

    email = models.EmailField()

    gender = models.CharField(
        max_length=max(len(x) for x, _ in GENDERS),
        choices=GENDERS,
        null=True,
        blank=True,
        default=DO_NOT_SHOW,
    )

    user = models.OneToOneField(
        WakeAppUser,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    def get_profile_image_filename(self):
        return str(self.profile_image)[str(self.profile_image).index('profile_images/' + str(self.pk) + "/"):]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class FriendsStore(models.Model):
    friends = models.ManyToManyField(Profile)


class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        Profile,
        related_name='from_user',
        on_delete=models.CASCADE,

    )
    to_user = models.ForeignKey(
        Profile,
        related_name='to_user',
        on_delete=models.CASCADE,

    )
