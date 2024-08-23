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
import pytz
from django.contrib import admin
from django.utils import dateformat
from django.conf import settings
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .lib.choices import TypeGenerateSendCertificate
from .models import Category, Publication, Certificate, CertificateConfigs


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "certificate"]
    search_fields = ["name"]
    list_filter = ["parent"]
    autocomplete_fields = ["parent"]


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "published_at", "publish_end_at", "auto_send"]
    search_fields = ["title", "published_at"]
    list_filter = ["category", "author", "published_at"]
    date_hierarchy = "published_at"
    readonly_fields = ["created_at", "modified_at", "certificate_list"]
    ordering = ["-published_at"]
    autocomplete_fields = ["category"]
    fieldsets = (
        (_("Main Options"), {
            'fields': ('title', 'description', ('category', 'author'), 'file')
        }),
        (_('Date Options'), {
            'classes': ('collapse',),
            'fields': (('published_at', 'publish_end_at'),),
        }),
        (_('Advance Options'), {
            'classes': ('collapse',),
            'fields': ('notification', ('auto_send', 'icon_class')),
        }),
    )

    def certificate_list(self, obj):
        send = _("Send Certificate")
        publication = Publication.objects.get(id=obj.id)

        certificates_publications = publication.zb_certifies_publication.all().order_by("-created_at")
        certificates = []
        generate = _("Generate PDF certificate")
        action = format_html(
            f'<a href="/djangocms_zb_filer/generate-pdf/{obj.id}" '
            f'class="btn" style="padding:10px 20px !important; float:right; background:#6B9B33 !important; '
            f'color:#FFFFFF !important" target="_parent">{generate}</a>'
        )
        if not publication.category.certificate:
            action = _("A certificate cannot be generated because the category does not have a certificate selected.")
        elif publication.auto_send:
            action = _("The certificate is generated and sent when the publication is complete.")
        for cer in certificates_publications:
            time_zone = pytz.timezone(settings.TIME_ZONE)
            date_created = dateformat.format(cer.created_at.astimezone(time_zone), "d \d\e F \d\e Y H:i:s")
            see = _("See Certificate")
            row = (f'<tr><td><a href="{cer.file_path}" target="_blank" class="button">{see}</a></td>'
                   f'<td>{cer.get_type_generate_display()}</td>')
            if cer.type_generate == TypeGenerateSendCertificate.AUTOMATIC:
                row = row + (
                    f'<td></td><td>{cer.get_type_send_display()}</td>')
            else:
                row = row + (
                    f'<td><a href="/djangocms_zb_filer/send_certificate/{cer.id}" class="button">{send}</a></td>' if len(
                        publication.notification) > 0 else f'<td></td>')
            row = row + f'<td>{cer.get_type_send_display()}</td><td>{date_created}</td></tr>'
            certificates.append(row)
        html = format_html('<div style="margin-bottom:4rem">' + action + '</div>')
        if len(certificates) > 0:
            see = _("See")
            generated = _("Generated")
            send = _("Send")
            sent = _("Sent")
            date = _("Date")
            html += format_html('<div class="results" style="overflow-x: auto; width: 100%;"><table>'
                                f'<thead><tr><th>{see}</th><th>{generated}</th><th>{send}</th><th>{sent}</th><'
                                f'th>{date}</th></tr></thead><tbody>' +
                                str(certificates).translate(
                                    {ord("["): ord(" "), ord("'"): ord(" "), ord(","): ord(" "), ord("]"): ord(" ")}
                                )
                                + '</tbody></table></div>'
                                )
        else:
            html += format_html(_("No certificates have been generated"))
        return html

    certificate_list.short_description = _("Certificates")

    def get_fieldsets(self, request, obj=None):
        if obj:  # editing an existing object
            add = (
                [_('Additional Information'), {
                    'fields': ('created_at', 'modified_at')
                }],
                [_('List of Certificates'), {
                    'classes': ('collapse',),
                    'fields': ('certificate_list',)
                }],
            )
            return self.fieldsets + add
        return self.fieldsets


@admin.register(CertificateConfigs)
class CertificateConfigsAdmin(admin.ModelAdmin):
    list_display = ["name", "header", "sign"]
    search_fields = ["name", "title"]


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def certificate(self, obj):
        pk = obj.id
        certificate = Certificate.objects.get(id=pk)
        see = _("See Certificate")
        return format_html(
            f'<a href="{certificate.file_path}" target="_blank" class="button">{see}</a>'
        )

    certificate.short_description = _("Certificate")

    list_display = ["created_at", "publication", "certificate"]
    list_display_links = None
    search_fields = ["publication__title", "created_at", "file_path"]
    list_filter = ["created_at"]
    date_hierarchy = "created_at"
