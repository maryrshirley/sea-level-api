from django.core.validators import (MinLengthValidator, MinValueValidator,
                                    MaxLengthValidator, RegexValidator)
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _


class Vessel(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    imo = models.CharField(
        max_length=7, unique=True,
        validators=[MinLengthValidator(7),
                    MaxLengthValidator(7),
                    RegexValidator(regex="^\d+$", code='invalid_imo',
                                   message=_("Must be numbers only"))])
    draft = models.FloatField(validators=[MinValueValidator(0)])

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Vessel, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
