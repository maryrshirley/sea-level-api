from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver


@receiver(pre_save, sender=User)
def unique_email(sender, instance, **kwargs):
    email = instance.email
    if not len(email):
        return
    if sender.objects.filter(email=email).exclude(id=instance.id).count():
        raise ValidationError("Email {0} is already used".format(email))
