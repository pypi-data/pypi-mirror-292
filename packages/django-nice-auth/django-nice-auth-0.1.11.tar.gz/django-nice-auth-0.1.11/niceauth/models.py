import uuid
from django.db import models
try:
    from django.utils.translation import gettext_lazy as _
except ImportError:
    from django.utils.translation import ugettext_lazy as _


# Base Model
class BaseModel(models.Model):
    """
    BaseModel contains the common fields for all models.
    """
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True, null=True)

    class Meta:
        abstract = True

# NiceAuthRequest Model
class NiceAuthRequest(BaseModel):
    """
    NiceAuthRequest stores information for the authentication request.
    """
    AUTH_TYPE_CHOICES = [
        ('M', _('Mobile Authentication')),
        ('C', _('Card Verification Authentication')),
        ('X', _('Certificate Authentication')),
        ('U', _('Joint Certificate Authentication')),
        ('F', _('Financial Certificate Authentication')),
        ('S', _('PASS Certificate Authentication')),
    ]

    POPUPYN_CHOICES = [
        ('Y', _('Yes')),
        ('N', _('No')),
    ]

    request_no = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    enc_data = models.TextField(
        _('Encrypted Data'),
        help_text=_("Encrypted data for the request.")
    )
    integrity_value = models.TextField(
        _('Integrity Value'),
        help_text=_("Integrity value for the request.")
    )
    token_version_id = models.CharField(
        _('Token Version ID'),
        max_length=100,
        help_text=_("Token version ID used in the request.")
    )
    key = models.CharField(
        _('Key'),
        max_length=32,
        help_text=_("Key for encryption.")
    )
    iv = models.CharField(
        _('Initialization Vector (IV)'),
        max_length=32,
        help_text=_("Initialization Vector (IV) for encryption.")
    )
    authtype = models.CharField(
        _('Authentication Type'),
        max_length=1,
        choices=AUTH_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text=_("Type of authentication (e.g., M for mobile).")
    )
    popupyn = models.CharField(
        _('Popup Flag'),
        max_length=1,
        choices=POPUPYN_CHOICES,
        null=True,
        blank=True,
        help_text=_("Flag to indicate if popup is used (Y/N).")
    )
    return_url = models.URLField(
        _('Return URL'),
        max_length=200,
        null=True,
        blank=True,
        help_text=_("URL to return to after authentication.")
    )
    redirect_url = models.URLField(
        _('Redirect URL'),
        max_length=200,
        null=True,
        blank=True,
        help_text=_("URL to redirect to after authentication.")
    )
    is_verified = models.BooleanField(default=False, help_text=_("Verification status"))

    class Meta:
        verbose_name = _('Nice Auth Request')
        verbose_name_plural = _('Nice Auth Requests')
        ordering = ['-created_at']

# NiceAuthResult Model
class NiceAuthResult(BaseModel):  # 상속받도록 수정
    request = models.OneToOneField(
        NiceAuthRequest,
        on_delete=models.CASCADE,
        verbose_name=_('Related Request'),
        help_text=_("Reference to the related NiceAuthRequest.")
    )
    result = models.JSONField(
        _('Result'),
        help_text=_("Result of the authentication request in JSON format.")
    )
    request_no = models.UUIDField(
        _('Request Number'),
        help_text=_("Unique request number for the authentication request."),
        default=uuid.uuid4  # 기본값 추가
    )
    enc_data = models.TextField(
        _('Encrypted Data'),
        help_text=_("Encrypted data for the request."),
        default=''  # 기본값 추가
    )
    is_verified = models.BooleanField(
        default=False,
        help_text=_("Verification status")
    )
    birthdate = models.CharField(
        _('Birthdate'),
        max_length=8,
        blank=True,
        null=True,
        help_text=_('Birthdate of the user in YYYYMMDD format.')
    )
    gender = models.CharField(
        _('Gender'),
        max_length=1,
        blank=True,
        null=True,
        help_text=_('Gender of the user. 1 for male, 2 for female.')
    )
    di = models.CharField(
        _('DI'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('DI (Duplication Information) value.')
    )
    mobileco = models.CharField(
        _('Mobile Carrier'),
        max_length=1,
        blank=True,
        null=True,
        help_text=_('Mobile carrier code.')
    )
    receivedata = models.TextField(
        _('Receive Data'),
        blank=True,
        null=True,
        help_text=_('Additional data received from the authentication.')
    )
    mobileno = models.CharField(
        _('Mobile Number'),
        max_length=11,
        blank=True,
        null=True,
        help_text=_('Mobile number of the user.')
    )
    nationalinfo = models.CharField(
        _('National Info'),
        max_length=1,
        blank=True,
        null=True,
        help_text=_('National information code.')
    )
    authtype = models.CharField(
        _('Authentication Type'),
        max_length=1,
        blank=True,
        null=True,
        help_text=_('Type of authentication performed.')
    )
    sitecode = models.CharField(
        _('Site Code'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Site code where the authentication was performed.')
    )
    utf8_name = models.CharField(
        _('UTF8 Name'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('UTF8 encoded name of the user.')
    )
    enctime = models.CharField(
        _('Encryption Time'),
        max_length=14,
        blank=True,
        null=True,
        help_text=_('Time when the data was encrypted in YYYYMMDDHHMMSS format.')
    )
    name = models.CharField(
        _('Name'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Name of the user.')
    )
    resultcode = models.CharField(
        _('Result Code'),
        max_length=4,
        blank=True,
        null=True,
        help_text=_('Result code of the authentication.')
    )
    responseno = models.CharField(
        _('Response Number'),
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Response number from the authentication service.')
    )
    redirect_url = models.URLField(
        _('Redirect URL'),
        max_length=200,
        null=True,
        blank=True,
        help_text=_("URL to redirect to after authentication.")
    )

    class Meta:
        verbose_name = _('Nice Auth Result')
        verbose_name_plural = _('Nice Auth Results')
        ordering = ['-created_at']
