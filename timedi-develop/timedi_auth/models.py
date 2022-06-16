"""Models for Hospital Management System"""
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.contrib.auth.validators import UnicodeUsernameValidator

from timedi_auth.choices import *


class TimeStampMixin(models.Model):
    """Class representing the created_at and updated_at fields declared
    globally"""
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """This model will not create any Database Table"""
        abstract = True


class UserManager(BaseUserManager):

    def _create_user(self, username, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        account = Account.objects.create(name=username, country_code='IN')
        user = self.model(username=username, account=account, **extra_fields)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        role = Role.objects.get(name='super_admin')
        extra_fields.setdefault('role_id', role.id)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')

        return self._create_user(username, password, **extra_fields)


class Account(TimeStampMixin):
    """Class representing Accounts."""
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    country_code = models.CharField(max_length=30)

    class Meta:
        """Meta class for accounts table"""
        db_table = 'account'

    def __str__(self):
        return '{}'.format(self.name)

    def __repr__(self):
        return str(self)


class User(AbstractBaseUser, TimeStampMixin, PermissionsMixin):
    """Class representing an user."""

    username_validator = UnicodeUsernameValidator()

    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, null=False, blank=False)
    profile_pic = models.TextField(null=True, blank=True)
    gender = models.CharField(max_length=30, choices=GENDER_CHOICES, null=False, blank=False)
    email = models.EmailField(max_length=50, null=True, )
    company_name = models.CharField(max_length=50, null=True)
    mobile_number = models.CharField(max_length=50, null=True)
    assigned_hospital = models.CharField(max_length=50, null=True, blank=True)
    is_new_user = models.BooleanField(default=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='users')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    role = models.ForeignKey('Role', null=True, related_name='users', on_delete=models.CASCADE)
    username = models.CharField(_('username'), max_length=150, unique=True,
                                help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
                                validators=[username_validator],
                                error_messages={'unique': _("A user with that username already exists."), }, )
    timedi_permissions = models.ManyToManyField('TimediPermission',
                                                through='UserTimediPermissionMap')
    is_superuser = models.BooleanField(
        _('superuser status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin'
            ' site.',
        ),
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin'
            ' site.',
        ),
    )

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email',)

    class Meta:
        ordering = ['-updated_at', ]

    @property
    def full_name(self):
        return '{}'.format(self.name)

    def has_perm(self, perm, obj=None):
        """
        Return True if the user has the specified permission. Query all
        available auth backends, but return immediately if any backend returns
        True. Thus, a user who has permission from a single auth backend is
        assumed to have permission in general. If an object is provided, check
        permissions for that object.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return True

    def has_permission(self, permission_code, write=None, read=None):
        try:
            if self.is_superuser:
                return True
            else:
                timedi_permission_obj = self.permission_maps.get(permission__code=permission_code)
                if write is not None and timedi_permission_obj.write != write:
                    return False
                if read is not None and timedi_permission_obj.read != read:
                    return False
                return True
        except UserTimediPermissionMap.DoesNotExist:
            return False

    def __str__(self):
        return "{},{},{}".format(self.full_name, self.username, self.role)


class Token(models.Model):
    """Class representing a token. Used for reset password, signup."""
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    expires_at = models.DateTimeField(_('expires at'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    token = models.TextField(_('token'), validators=[MinLengthValidator(64)], unique=True)

    def __str__(self):
        """Format user, action and token."""

        return "{}-{}-{}".format(self.user, self.action, self.token)


class Role(models.Model):
    """
    """
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=48, null=False, unique=True)

    def __str__(self):
        return self.name


class TimediPermission(models.Model):
    """
    """
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(max_length=64, unique=True)
    code = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.display_name


class UserTimediPermissionMap(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="permission_maps")

    permission = models.ForeignKey(TimediPermission, on_delete=models.CASCADE)

    read = models.BooleanField(default=False)

    write = models.BooleanField(default=False)

    class Meta:
        unique_together = (('user', 'permission'),)

    def __str__(self):
        return "{}, {}, {}, {} ,{}".format(self.user.name, self.user.role.name, self.permission, self.read, self.write)


class AccessToken(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    token = models.TextField()
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Access token for {}'.format(self.user)


class BlacklistedAccessToken(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    token = models.TextField()
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Blacklisted token for {}'.format(self.user)


from timedi_auth.signal_receivers import *
