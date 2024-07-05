"""
URL configuration for herbdonbass project.

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
from django.conf import settings

from vitamins.sitemaps import VitaminSitemap, BrandFilterSitemap, CategoryFilterSitemap, HomePageSitemap, \
    ContactPageSitemap
from vitamins.views import custom_page_not_found_view

from django.contrib.sitemaps.views import sitemap

sitemaps = {
    'vitamins': VitaminSitemap,
    'vitamins_filter_by_brand': BrandFilterSitemap,
    'vitamins_filter_by_category': CategoryFilterSitemap,
    'home': HomePageSitemap,
    'contacts': ContactPageSitemap
}

handler404 = custom_page_not_found_view

urlpatterns = [
    path("__debug__/", include("debug_toolbar.urls")),
    path('captcha/', include('captcha.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('users/', include('users.urls', namespace='users')),
    path('preorders/', include('preorders.urls', namespace='preorders')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('', include('vitamins.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='from django.contrib.sitemaps.views import sitemap')
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
        path('users/', include('users.urls', namespace='users')),
        path('cart/', include('cart.urls', namespace='cart')),
        path('preorders/', include('preorders.urls', namespace='preorders')),
        path('admin/', admin.site.urls),
        path('api/', include('api.urls', namespace='api')),
        path('orders/', include('orders.urls', namespace='orders')),
        path('', include('vitamins.urls')),
        path('api/', include('api.urls', namespace='api')),
        path('social-auth/', include('social_django.urls', namespace='social')),
        path('captcha/', include('captcha.urls')),
        path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='from django.contrib.sitemaps.views import sitemap')

    ]
