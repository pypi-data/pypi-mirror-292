#      Copyright (C)  2022. CQ Inversiones SAS.
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
from cms.models.pluginmodel import CMSPlugin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from filer.fields.file import FilerFileField
from filer.fields.image import FilerImageField

from djangocms_zb_filer.lib.choices import Choices, TypeGenerateSendCertificate
from djangocms_zb_filer.lib.fields import MultiEmailField


class CertificateConfigs(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    title = models.CharField(_("Title"), max_length=300)
    description = models.TextField(_("Description"), max_length=2000)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    header = FilerImageField(verbose_name=_("Header"), blank=True, null=True, on_delete=models.PROTECT,
                             related_name="zb_header_filer_image")
    sign = FilerImageField(verbose_name=_("Sign"), blank=True, null=True, on_delete=models.PROTECT,
                           related_name="zb_sign_filer_image")
    template = models.CharField(_("Template"), max_length=70,
                                choices=Choices.TEMPLATES_CHOICES,
                                default=Choices.TEMPLATES_CHOICES[0][0],
                                help_text=_("(HTML) Alternative template for the design of certificate."))

    class Meta:
        verbose_name_plural = _("Certificate Configs")

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Modelo que representa la entidad Category
    """
    name = models.CharField(null=False, blank=False, max_length=250, verbose_name=_("Name"))
    parent = models.ForeignKey("self", related_name="zb_subcategory", on_delete=models.CASCADE, blank=True, null=True,
                               verbose_name=_("parent category"))
    certificate = models.ForeignKey(CertificateConfigs, on_delete=models.PROTECT,
                                    verbose_name=_("Certificate"), blank=True, null=True,
                                    related_name="zb_category_certifies")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = _("Categories")

    @property
    def full_name(self):
        full_name_parent = "{parent}/{name}".format(parent=self.parent, name=self.name).replace("None/", "")
        return full_name_parent.strip()

    def __str__(self):
        return self.full_name


class Publication(models.Model):
    """
    Modelo que representa la entidad Publication
    """
    title = models.CharField(_("Title"), max_length=250, db_collation="utf8_general_ci")
    description = models.TextField(_("Description"), max_length=1000, null=True, blank=True,
                                   db_collation="utf8_general_ci")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name=_("Category"),
                                 related_name="zb_publication_category")
    author = models.ForeignKey(User, related_name="zb_publication_author", on_delete=models.PROTECT,
                               verbose_name=_("Author"))
    created_at = models.DateTimeField(_("Date Created"), auto_now_add=True)
    modified_at = models.DateTimeField(_("Date Modified"), auto_now=True)
    published_at = models.DateTimeField(_("Date Published"), blank=True, null=True)
    publish_end_at = models.DateTimeField(_("Date Published End"), null=True, blank=True)
    notification = MultiEmailField(_("Notification"), null=True, blank=True, help_text=_(
        "Specify the email addresses. These email addresses will be used when sending a certification."))
    auto_send = models.BooleanField(_("Auto-Send"), null=False, blank=False, default=False,
                                    help_text=_("Generate and send certificate when publication is complete."))
    certificate_sent_auto = models.BooleanField(_("Certificate sent automatically"), null=False, blank=False,
                                                default=False,
                                                help_text=_("Certificate generated and sent automatically."))
    icon_class = models.CharField(_("Icon"), choices=Choices.ICON_CHOICES, max_length=30,
                                  default="fa-light fa-file")
    file = FilerFileField(null=True, blank=True, on_delete=models.PROTECT, verbose_name=_("File"),
                          related_name="zb_publication_file")

    class Meta:
        verbose_name_plural = _("Publications")

    def __str__(self):
        return self.title

    def clean(self):
        if self.publish_end_at is not None and self.publish_end_at < self.published_at:
            raise ValidationError(
                _("The end date must be greater than the start date of the publication."))
        if self.auto_send:
            if self.category.certificate is None:
                raise ValidationError(
                    _("The auto-send option cannot be enabled because the category does not have a certificate"
                      " selected."))
            elif len(self.notification) <= 0:
                raise ValidationError(
                    _("The auto-send option cannot be enabled because it does not have notification emails."))
            elif self.publish_end_at is None:
                raise ValidationError(_("The auto-send option cannot be enabled because the post has no end date."))

    def save(self, *args, **kwargs):
        """
        Handle some auto configuration during save
        """
        if self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class Certificate(models.Model):
    """
    Modelo que representa la entidad Certificate.
    """
    created_at = models.DateTimeField(_("Date Created"))
    file_path = models.CharField(_("File Path"), max_length=250)
    type_generate = models.IntegerField(_("Certificate Creation Type"), choices=TypeGenerateSendCertificate.choices,
                                        default=TypeGenerateSendCertificate.MANUAL)
    type_send = models.IntegerField(_("Type of email delivery"), choices=TypeGenerateSendCertificate.choices,
                                    default=TypeGenerateSendCertificate.NOT_SENT)
    publication = models.ForeignKey(Publication, on_delete=models.PROTECT, verbose_name=_("Publication"),
                                    related_name="zb_certifies_publication")

    class Meta:
        verbose_name_plural = _("Certificates")

    def __str__(self):
        return self.file_path


class FilerPluginModel(CMSPlugin):
    """
    Model que representa la entidad Filer dentro del Plugin.
    """
    order = models.CharField(_("Order By"), max_length=15, choices=Choices.ORDER_CHOICES,
                             default=Choices.PUBLISHED_AT_DESC)
    pagination = models.IntegerField(_("Pagination"), help_text=_("Result by page"), default=10)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name=_("Filter by category"),
                                 related_name="zb_plugins_category")
    template = models.CharField(_("Template"), max_length=70, choices=Choices.TEMPLATES_CHOICES,
                                default=Choices.TEMPLATES_CHOICES[0][0],
                                help_text=_("(HTML) Alternative template for the design of list publications.")
                                )
    target = models.CharField(_("Link Target"), max_length=7, null=True, blank=True,
                              choices=Choices.TARGET)
