from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from django.db import models
from django.utils.translation import ugettext as _

from api.libs.view_helpers import now_rounded


@receiver(pre_save, sender=User)
def unique_email(sender, instance, **kwargs):
    email = instance.email
    if not len(email):
        return
    if sender.objects.filter(email=email).exclude(id=instance.id).count():
        raise ValidationError("Email {0} is already used".format(email))

STATUS_CHOICES = (
    ('success', _('Success')),
)


class LoginCodeExpiredManager(models.Manager):
    @staticmethod
    def expire(login_code, status='success'):
        LoginCodeExpired.objects.create(datetime=now_rounded(),
                                        status=status,
                                        code=login_code.code,
                                        user=login_code.user)
        login_code.delete()


class LoginCodeExpired(models.Model):
    datetime = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    code = models.CharField(max_length=20, editable=False, unique=True)
    user = models.ForeignKey('auth.User', related_name='+', editable=False)

    objects = LoginCodeExpiredManager()
