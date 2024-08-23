# -*- coding: utf-8 -*-
#   Copyright (C)  2022. CQ Inversiones SAS.#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ****************************************************************
# IDE:          PyCharm
# Developed by: "Jhony Alexander Gonzalez Córdoba"
# Date:         15/08/2024 9:08 a. m.
# Project:      django_cms_plugins
# Module Name:  document_generator
# Description:  
# ****************************************************************
import os
import uuid
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa


class CertificateGenerator:
    """Class to generate a publication certificate"""

    def __init__(self):
        self.__template_dir = "djangocms_zb_filer/"
        self.__base_dir = "djangocms_zb_filer/certificates/"
        self.__certificate_template = "certificate.html"

    def __get_template(self, template: object):
        template = self.__template_dir + str(template) + "/" + self.__certificate_template
        return template

    def __get_filepath(self, category: str):
        file_name = uuid.uuid4().hex + ".pdf"
        file_path = os.path.join(settings.MEDIA_ROOT, self.__base_dir + str(category))
        return file_path, file_name

    def __get_url(self, category: str, file_name: str):
        return settings.MEDIA_URL + self.__base_dir + category + "/" + file_name

    def generate_from_template(self, template_name: str, folder: str, context: dict):
        try:
            # Se carga el template
            template = get_template(self.__get_template(template_name))
            html = template.render(context)
            # Se arma el nombre del path y el del archivo
            file_path, file_name = self.__get_filepath(folder)
            if not os.path.exists(file_path):
                os.makedirs(file_path)

            # Se arma la URL del archivo
            url_file = self.__get_url(folder, file_name)
            full_file_path = file_path + "/" + file_name
            write_to_file = open(full_file_path, "w+b")
            pisa.CreatePDF(html, dest=write_to_file)
            write_to_file.close()
        except Exception:
            raise
        else:
            return url_file
