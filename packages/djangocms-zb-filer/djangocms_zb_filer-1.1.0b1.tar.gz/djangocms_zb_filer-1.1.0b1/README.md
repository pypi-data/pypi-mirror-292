Django CMS Zibanu Filer Extension
-----------

Django CMS Zibanu Filer Extension es un complemento para django CMS que le permite agregar publicaciones a su sitio, con
archivos, fecha de publicación, fecha de despublicación, icono, etc.
Al agregar en su sitio puede elegir mostrar una categoría.

![](preview.png)

Utiliza archivos administrados por Django Filer .

Utiliza PDF generados por xhtml2pdf .


Documentación
-----------

Ver requerimientos en el archivo setup.cfg para dependencias adicionales:

python 3.9+ < 4.0 - django 3.2.11 - django CMS 3.9.0 - django-filer 2.1.2 - xhtml2pdf 0.2.7

Asegúrese de que django-filer esté instalado y configurado correctamente.

Instalación
-----------

1. Correr pip install djangocms-zb-filer
2. Añadir 'djangocms_zb_filer' a su INSTALLED_APPS
3. Correr "python manage.py migrate"
4. Incluya en urls.py de su proyecto la URLconf de Django CMS Zibanu Filer Extension antes de la de cms.urls así:    

    
    urlpatterns = [
       path('admin/', admin.site.urls),
       path('djangocms_zb_filer/', include('djangocms_zb_filer.urls')),
       path('', include('cms.urls')),
    ]

5. Inicie el servidor de desarrollo y visite http://su_servidor/admin/
    para crear una publicación (Necesitará que la aplicación Admin esté habilitada).

![](panel_admin.png)

Configuración
------
Tenga en cuenta que las plantillas proporcionadas son mínimas por diseño. 
Los puede adaptar y anular según los requisitos de su proyecto.

Este complemento proporciona una plantilla default para todas las instancias. Puede proporcionar opciones de plantilla 
adicionales agregando la constante DJANGOCMS_ZB_FILER_TEMPLATES en su settings.py:

    DJANGOCMS_ZB_FILER_TEMPLATES = [
        ('template_mejorado', _('Template Mejorado')),
    ]

Tendrá que crear la carpeta template_mejorado dentro de templates/djangocms_zb_filer/ de lo contrario, obtendrá un error de 
plantilla que no existe. Puede hacer esto copiando la carpeta default dentro de ese directorio y renombrándola a
template_mejorado.
