"""
URL configuration for express_delivery project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

from core.views import set_language_custom

urlpatterns = [
    path('i18n/setlang/', set_language_custom, name='set_language'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', lambda request: redirect(f'/{settings.LANGUAGE_CODE}/')),
]

from django.shortcuts import redirect

from django.conf import settings

# Manual i18n patterns to workaround i18n_patterns issue
for lang_code, lang_name in settings.LANGUAGES:
    urlpatterns += [
        path(f'{lang_code}/', include('core.urls')),
        path(f'{lang_code}/admin/', admin.site.urls),
    ]
