from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, name, email, user_type, password):
        if not email:
            raise ValueError('Email must be specified!')

        user = self.model(
            name=name,
            email=self.normalize_email(email),
        )
        if user_type == 'client':
            user.is_client = True
        elif user_type == 'tutor':
            user.is_tutor = True
        else:
            raise ValueError('User type can be either client or tutor')

        user.set_password(password)
        user.save(self._db)
        return user

    def create_superuser(self, name, email, password):
        if not email:
            raise ValueError('Email must be specified!')

        user = self.model(
            name=name,
            email=self.normalize_email(email),
        )
        user.is_admin = True
        user.set_password(password)
        user.save(self._db)
        return user


class User(AbstractBaseUser):
    """The user model, it is a user profile as well"""
    email = models.EmailField(
        verbose_name='Email address',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    is_tutor = models.BooleanField(default=False)
    name = models.CharField(max_length=100, null=False, verbose_name='Full name')
    bio = models.CharField(max_length=1000, verbose_name='Bio')
    location = models.CharField(max_length=1000, verbose_name='Location')
    gender = models.CharField(max_length=20, verbose_name='Gender')
    title = models.CharField(max_length=1000, verbose_name='Overview title')  # Overview title
    overview = models.TextField(verbose_name='Overview')
    expertise = models.CharField(max_length=1000, verbose_name='Expertise')
    profile_img = models.TextField(verbose_name='Profile Image', blank=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        return self.is_admin

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        return True

    def has_module_perms(self, app_label):
        """"Does the user have permissions to view the app `app_label`?"""
        return True

    def __str__(self):
        return self.email


class Phone(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_no = models.CharField(max_length=20, null=False)

    def __str__(self):
        return '{} - {}'.format(self.user.email, self.phone_no)


class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    institute = models.CharField(max_length=200, null=False, verbose_name='Institute')
    department = models.CharField(max_length=200, verbose_name='Department')
    degree = models.CharField(max_length=200, verbose_name='Degree')
    result = models.CharField(max_length=200, verbose_name='Result')
    from_year = models.DateField(null=False, verbose_name='From year')
    to_year = models.DateField(null=False, verbose_name='To year')

    def __str__(self):
        return self.institute


class Verification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, verbose_name='File Type')
    file = models.TextField(verbose_name='File location')
    verified = models.BooleanField(verbose_name='Verified', default=False)

    def __str__(self):
        return '{} - {}'.format(self.user.email, self.type)
