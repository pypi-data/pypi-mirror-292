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
import os
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
from zibanu.django.utils import Email

from .lib.choices import TypeGenerateSendCertificate
from .lib.utils import CertificateGenerator
from .models import Publication, Certificate


# Create your views here.


class GeneratePdf(View):
    """
    Clase que genera un PDF a partir de un template HTML
    """

    def get(self, request, *args, **kwargs):
        """
        Responde a la petición GET vía HTTP
        :param request: request recibido vía HTTP
        :param args: args de la petición
        :param kwargs: conjunto de argumentos en formato dict de la petición
        :return: redirect
        """
        try:
            if request.user.is_authenticated and request.user.is_staff:
                pk = kwargs.get('id')
                domain = "{0}://{1}".format(request.scheme, request.get_host())
                query = get_object_or_404(Publication, id=pk)
                date_now = timezone.now()
                context = {
                    'publication': query,
                    'date_now': date_now,
                    'domain': domain
                }
                certificate = CertificateGenerator()
                url_file = certificate.generate_from_template(template_name=query.category.certificate.template,
                                                              folder=query.category.name, context=context)
                Certificate.objects.create(created_at=date_now, file_path=url_file, publication_id=pk)
            else:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except Exception:
            raise
        else:
            messages.success(request, _("Certificate generate successfully."))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class SendCertificate(View):
    """View that performs the process of sending a certificate to the email."""

    def get(self, request, *args, **kwargs):
        """
        Responde a la petición GET vía HTTP
        :param request: request recibido vía HTTP
        :param args: args de la petición
        :param kwargs: conjunto de argumentos en formato dict de la petición
        :return: redirect
        """
        try:
            if request.user.is_authenticated and request.user.is_staff:
                pk = kwargs.get('id')
                certificate = get_object_or_404(Certificate, id=pk)
                # Set mail context
                path_filename = os.path.join(settings.BASE_DIR, certificate.file_path[1:])
                if not os.path.exists(path_filename):
                    raise ObjectDoesNotExist(_("Document file does not exist."))
                email_context = {
                    "publication_title": certificate.publication.title,
                    "description": certificate.publication.description,
                    "created_at": certificate.created_at
                }
                email = Email(
                    subject=_("Certificate of publication %(title)s") % {"title": certificate.publication.title},
                    to=certificate.publication.notification)
                email.set_text_template("djangocms_zb_filer/mail/send_certificate.txt", context=email_context)
                email.attach_file(path_filename)
                email.send()
                certificate.type_send = TypeGenerateSendCertificate.MANUAL
                certificate.save()
            else:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except Exception:
            raise
        else:
            messages.success(request, _("Certificate sent successfully."))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
