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

from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class DjangocmsZbFilerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djangocms_zb_filer'
    verbose_name = _('Django cms Zb Filer Extension')

    def ready(self):
        settings.DOMAIN = getattr(settings, "DOMAIN", "/")
