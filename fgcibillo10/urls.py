"""fgcibillo10 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.utils.translation import ugettext as _, ugettext_lazy
from user.urls import profile_urls, other_urls
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static



admin.site.site_title = ugettext_lazy('fgcibillo10 admin')
admin.site.site_header = ugettext_lazy('fgcibillo10 administration')




urlpatterns = [
    path('admin/', admin.site.urls),
    #re_path(r'^user/', include(user_urls, namespace='dj-auth')),
    path('posts/', include('blog.urls.post_urls', namespace='blog_post_urls')),
    path('tags/', include('blog.urls.tag_urls', namespace='tag_urls')),
    path('', include('user.urls.other_urls', namespace='other_urls')), #include(other_urls, namespace='other_urls')),
    path('', include('user.urls.profile_urls', namespace='profile_urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
