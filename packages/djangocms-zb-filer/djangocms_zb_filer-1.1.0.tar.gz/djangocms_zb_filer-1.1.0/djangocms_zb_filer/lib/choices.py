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

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Choices:
    ICON_CHOICES = (
        ("fa-light fa-file", _("Default")),
        ("fa-light fa-file-pdf", _("Pdf")),
        ("fa-light fa-file-word", _("Word")),
        ("fa-light fa-file-excel", _("Excel")),
        ("fa-light fa-file-powerpoint", _("Power Point")),
    )

    PUBLISHED_AT_ASC = "published_at"
    PUBLISHED_AT_DESC = "-published_at"
    TITLE_ASC = "title"
    TITLE_DESC = "-title"

    ORDER_CHOICES = (
        (PUBLISHED_AT_ASC, _("[Date Published] From the oldest to the most recent")),
        (PUBLISHED_AT_DESC, _("[Date Published] From the most recent to the oldest")),
        (TITLE_ASC, _("[Title] A-Z")),
        (TITLE_DESC, _("[Title] Z-A"))
    )

    TARGET = (
        ("_blank", "_blank"),
        ("_parent", "_parent"),
        ("_self", "_self"),
        ("_top", "_top"),
    )

    TEMPLATES_CHOICES = [
        ('default', _('Default')),
    ]
    TEMPLATES_CHOICES += getattr(
        settings,
        'DJANGOCMS_ZB_FILER_TEMPLATES',
        [],
    )


class TypeGenerateSendCertificate(models.IntegerChoices):
    MANUAL = 0, _("Manual Button")
    AUTOMATIC = 1, _("Automatic Task")
    NOT_SENT = 10, _("Not sent")
