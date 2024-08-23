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
# Date:         22/04/22 10:21 AM
# Project:      djangoPlugin
# Module Name:  cms_plugins
# ****************************************************************
import os
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.http import Http404
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from .models import FilerPluginModel, Publication


@plugin_pool.register_plugin
class DjangocmsZbFilerPlugin(CMSPluginBase):
    name = _("Zibanu Filer Extension")
    module = "Zibanu"
    cache = False
    model = FilerPluginModel
    autocomplete_fields = ["category"]
    fieldsets = (
        (_("Main Options"), {
            'fields': ('order', ('pagination', 'category'))
        }),
        (_('Advance Options'), {
            'classes': ('collapse',),
            'fields': (('template', 'target'),),
        }),
    )

    def _get_render_template(self, context, instance, placeholder):
        """
        Private method to replace default template in CMS
        :param context: Context CMS Var
        :param instance: Model instance
        :param placeholder: Placeholder
        :return: str: Name of new template
        """
        base_dir = f"djangocms_zb_filer/default/"
        base_template = "filer_list.html"
        if instance.template:
            base_dir = f"djangocms_zb_filer/{instance.template}/"

        return os.path.join(base_dir, base_template)

    def get_render_template(self, context, instance, placeholder):
        return self._get_render_template(context, instance, placeholder)

    def render(self, context, instance, placeholder):
        """
        Override method to render template
        :param context: Context CMS Var
        :param instance: Model instance
        :param placeholder: Placeholder
        :return: context
        """

        info = Publication.objects.filter(
            Q(published_at__isnull=False) & Q(published_at__lte=timezone.now()),
            Q(publish_end_at__isnull=True) | Q(publish_end_at__gte=timezone.now())).\
            filter(category_id=instance.category.id).order_by(instance.order)

        queryset = context['request'].GET.get('search')
        if queryset:
            for word in queryset.split(' '):
                info = Publication.objects.filter(
                    Q(published_at__isnull=False) & Q(published_at__lte=timezone.now()),
                    Q(publish_end_at__isnull=True) | Q(publish_end_at__gte=timezone.now()),
                    Q(title__icontains=word) | Q(description__icontains=word),
                    Q(category_id=instance.category.id)). \
                    distinct().order_by(instance.order)

        page = context['request'].GET.get('page') or 1
        try:
            paginator = Paginator(info, instance.pagination)
            info = paginator.page(page)
        except:
            raise Http404

        context = super().render(context, instance, placeholder)
        context.update({
            "info_publications": info,
            "paginator": paginator
        })
        return context
