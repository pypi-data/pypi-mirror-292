# -*- coding: utf-8 -*-

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

# ****************************************************************
# IDE:          PyCharm
# Developed by: JhonyAlexanderGonzal
# Date:         22/04/22 2:28 PM
# Project:      djangoPlugin
# Module Name:  fields
# ****************************************************************
from django.db import models
from djangocms_zb_filer.lib.forms import MultiEmailField as MultiEmailFormField

try:
    from django.utils import six

    string_types = six.string_types
except ImportError:
    string_types = str


class MultiEmailField(models.Field):
    description = "A multi e-mail field stored as a multi-lines text"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', [])
        super(MultiEmailField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {'form_class': MultiEmailFormField}
        defaults.update(kwargs)
        return super(MultiEmailField, self).formfield(**defaults)

    def from_db_value(self, value, expression, connection, context=None):
        if value is None:
            return []
        return value.splitlines()

    def get_db_prep_value(self, value, connection, prepared=False):
        if isinstance(value, string_types):
            return value
        elif isinstance(value, list):
            return "\n".join(value)

    def to_python(self, value):
        if not value:
            return []
        if isinstance(value, list):
            return value
        return value.splitlines()

    def get_internal_type(self):
        return 'TextField'
