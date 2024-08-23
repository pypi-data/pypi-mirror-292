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
# Date:         22/04/22 2:20 PM
# Project:      djangoPlugin
# Module Name:  widgets
# ****************************************************************
from django.forms.widgets import Textarea
from django.core.exceptions import ValidationError
from django.core import validators

MULTI_EMAIL_FIELD_EMPTY_VALUES = validators.EMPTY_VALUES + ('[]', )

try:
    from django.utils import six

    string_types = six.string_types
except ImportError:
    string_types = str


class MultiEmailWidget(Textarea):
    is_hidden = False

    def prep_value(self, value):
        """ Prepare value before effectively render widget """
        if value in MULTI_EMAIL_FIELD_EMPTY_VALUES:
            return ""
        elif isinstance(value, string_types):
            return value
        elif isinstance(value, list):
            return "\n".join(value)
        raise ValidationError('Invalid format.')

    def render(self, name, value, **kwargs):
        value = self.prep_value(value)
        return super(MultiEmailWidget, self).render(name, value, **kwargs)