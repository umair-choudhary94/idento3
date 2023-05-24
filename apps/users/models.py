import hashlib
import random
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group
# from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db import models
from django.db.models import CharField
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.safestring import mark_safe
from django_countries.fields import CountryField
from webcampicture.fields import WebcamPictureField

from apps.users.managers import CustomUserManager
from apps.users.utils import account_activation_token
from apps.verification.utils import extract, check


class User(AbstractUser):
    username = models.EmailField('Username', blank=True, null=True)

    email = models.EmailField('Email', unique=True)
    name = CharField('Name', blank=True, max_length=255)
    address = CharField('Address', blank=True, max_length=255)
    tel = models.CharField(max_length=50, blank=True, null=True, verbose_name='Tel')
    dob = models.DateTimeField('Date of Birth', blank=True, null=True)

    TYPE_PERSONAL = 'Personal'
    TYPE_COMPANY = 'Company'
    TYPE_CHOICES = (
        (TYPE_PERSONAL, TYPE_PERSONAL),
        (TYPE_COMPANY, TYPE_COMPANY)
    )
    type = CharField('Account Type', choices=TYPE_CHOICES, blank=True, null=True, max_length=255)
    company_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Company Name')
    logo = models.ImageField('Company Logo', upload_to='logos', null=True, blank=True)

    country = models.ForeignKey(to='users.Country', blank=True, null=True, on_delete=models.SET_NULL)
    picture = models.ImageField('Profile Picture', upload_to='profile_pictures', null=True, blank=True)

    email_verified = models.BooleanField('Email Verified', default=False)

    token = models.CharField('Token', blank=True, null=True, max_length=256)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    @property
    def plan(self):
        from apps.dashboard.models import MyPlan
        my_plan = MyPlan.objects.filter().last()
        if my_plan:
            return my_plan.plan

    def has_paid_plan(self):
        from apps.dashboard.models import MyPlan
        return MyPlan.objects.filter(user=self, is_active=True).exists()

    def __str__(self):
        return self.email

    def profile_picture(self):
        return mark_safe('<img src="%s"/>' % self.picture)

    profile_picture.allow_tags = True

    # def get_absolute_url(self):
    #     return reverse("users:detail", kwargs={"username": self.email})

    def send_signup_email(self):
        domain = settings.EMAIL_SEND_DOMAIN
        link = f'{domain}/verify/?uid={self.token}&token={self.token}'
        print(link)
        message = render_to_string('web/verification_email.html', {
            'user': self,
            'domain': domain,
            'link': link
        })
        self._send_email(message, "Account Verification")

    def send_identification_email(self):
        domain = settings.EMAIL_SEND_DOMAIN
        link = f'{domain}/verification/begin/?xid={self.identity.xid}&identifier={self.identity.identifier}'
        print(link)
        message = render_to_string('web/identification_email.html', {
            'user': self,
            'link': link,
        })
        self._send_email(message, "Identity Verification Request")

    def send_reset_password_email(self, context):
        message = render_to_string('web/password_reset_email.html', context)
        self._send_email(message, "Reset Password")

    def _send_email(self, message, subject):

        try:
            send_mail(
                subject=subject,
                message=message,
                html_message=message,
                from_email='freelancer7rg@gmail.com',
                recipient_list=[self]
            )
        except:
            pass

    def generate_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.pk))
        token = account_activation_token.make_token(self)
        self.token = token
        self.save()

    def add_manager_permissions(self):
        manager_group = Group.objects.get(name='Manager')
        manager_group.user_set.add(self)

    def add_limited_permissions(self):
        limited_group = Group.objects.get(name='Limited')
        limited_group.user_set.add(self)

    @property
    def is_limited(self):
        return self.groups.filter(name='Limited').exists()

    @property
    def is_manager(self):
        return self.groups.filter(name='Manager').exists()

    @property
    def added_by(self):
        from apps.dashboard.models import Employee
        from apps.dashboard.models import Customer
        person = Customer.objects.filter(user=self).last() or Employee.objects.filter(user=self).last()
        return person.added_by if person else None
    def calculate_verification_risk_score(self):
        # Get the identity associated with the user
        identity = self.identity
        

        if identity:
            risk_score = 0
            print("entered")
            # Calculate the risk score based on relevant fields

            # Increase risk score if email is not verified
            if not self.email_verified:
                print("email")
                risk_score += 10
            print(risk_score)
            # Increase risk score based on identity status
            if identity.status == Identity.STATUS_PENDING:
                print("status")
                risk_score += 10
            elif identity.status == Identity.STATUS_NOT_VERIFIED:
                print("status")
                risk_score += 10

            # Increase risk score based on document type
            document_type = identity.document_type
            if document_type == 'Passport':
                risk_score += 0
            elif document_type == 'Drivers Licence':
                risk_score += 0
            else:
                risk_score += 10
            # Increase risk score if the user has a paid plan
            if self.has_paid_plan():
                risk_score += 0
            else:
                risk_score += 10

           

            # Decrease risk score if the user is verified
            if identity.is_verified:
                risk_score += 0
            else:
                risk_score += 10

            # Decrease risk score if the user has uploaded certain files
            if identity.document:
                risk_score += 0
            else:
                risk_score += 10             

            if identity.document_back:
                risk_score += 0
            else:
                risk_score += 10

            if identity.selfie:
                risk_score += 0
            else:
                risk_score += 10

            if identity.temp_document:
                risk_score +=0
            else:
                risk_score += 10

            if identity.temp_back:
                risk_score += 0
            else:
                risk_score += 10
            # Return the calculated risk score
            risk_score = 40
            return max(risk_score, 0)

        return 0

class Country(models.Model):
    country = CountryField(blank=True, null=True)

    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', auto_now=True)

    def __str__(self):
        return self.country.name

    def __unicode__(self):
        return self.country.name

    class Meta:
        verbose_name_plural = 'Countries'
        verbose_name = 'Country'


class Company(models.Model):
    name = CharField('Name', max_length=255)

    # manager = models.ForeignKey('users.User', on_delete=models.PROTECT,
    #                             verbose_name='Manager')

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return str(self.name)


def generate_serial_number():
    return f"ID-{random.randint(100000, 999999)}"


class Identity(models.Model):
    serial_number = models.CharField('Serial Number', default=generate_serial_number, max_length=32)
    identifier = models.UUIDField('Identifier', default=uuid.uuid4, blank=True, null=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='identity',
                                blank=True, null=True)
    name = CharField('Name', blank=True, max_length=255)
    card_issuer = models.ForeignKey(Country, blank=True, null=True, on_delete=models.SET_NULL,
                                    verbose_name='Card Issuer')

    DOCUMENT_BACK = {
        'Birth Certificate': False,
        'Drivers Licence': True,
        'Educational Certificate': False,
        'ID Card': False,
        'Passport': False,
        'Proof of Address': False,
        'Proof of Identity': False,
        'Other': False
    }
    DOCUMENT_TYPE_CHOICES = (('Birth Certificate', 'Birth Certificate'),
                             ('Drivers Licence', 'Drivers Licence'),
                             ('Educational Certificate', 'Educational Certificate'),
                             ('ID Card', 'ID Card'),
                             ('Passport', 'Passport'),
                             ('Proof of Address', 'Proof of Address'),
                             ('Proof of Identity', 'Proof of Identity'),
                             ('Other', 'Other'))
    document_type = models.CharField('Document Type', max_length=32, null=True, blank=True,
                                     choices=DOCUMENT_TYPE_CHOICES)

    document = models.ImageField('Document', upload_to='verification_document', blank=True, null=True)
    document_back = models.ImageField('Document Back', upload_to='verification_document', blank=True, null=True)
    selfie = models.ImageField('Selfie', upload_to='selfies', null=True, blank=True)

    temp_document = WebcamPictureField(
        'Temp Document', upload_to='temps', blank=True, null=True
    )
    temp_back = WebcamPictureField(
        'Temp Document Back', upload_to='temps', blank=True, null=True
    )
    temp_selfie = WebcamPictureField(
        'Temp Selfie', upload_to='temps', blank=True, null=True
    )

    verification_reason = models.CharField('Reason for ID Check', blank=True, null=True, max_length=255,
                                           choices=(('Job', 'Job'), ('KYC', 'KYC')))

    STATUS_PENDING = 'Pending'
    STATUS_NOT_VERIFIED = 'Not Verified'
    STATUS_VERIFIED = 'Verified'
    STATUS_CHOICES = ((STATUS_PENDING, STATUS_PENDING),
                      (STATUS_NOT_VERIFIED, STATUS_NOT_VERIFIED),
                      (STATUS_VERIFIED, STATUS_VERIFIED))
    status = models.CharField('Status', blank=True, null=True, max_length=16,
                              choices=STATUS_CHOICES)

    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', auto_now=True)

    class Meta:
        verbose_name = 'Identity'
        verbose_name_plural = 'Identities'

    @property
    def has_back(self):
        return self.DOCUMENT_BACK.get(self.document_type)

    @property
    def temp_document_url(self):
        if self.temp_document and hasattr(self.temp_document, 'url'):
            return self.temp_document.url

    def verify(self):
        extracted_facename = extract(self.document.path)
        res = check(extracted_facename, self.selfie.path)
        return res  # Will return True or false

    def __str__(self):
        return str(self.serial_number)

    @staticmethod
    def initiate_verification(user):
        identity = Identity.objects.create(user=user, status=Identity.STATUS_PENDING, name=user.name)
        return identity

    @property
    def xid(self):
        return str(int(hashlib.sha1(str(self.identifier).encode("utf-8")).hexdigest(), 16) % (10 ** 500))

    @property
    def is_verified(self):
        return self.status == self.STATUS_VERIFIED


class SingletonModel(models.Model):
    _singleton = models.BooleanField(default=True, editable=False, unique=True)

    class Meta:
        abstract = True
