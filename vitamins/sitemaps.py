from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from vitamins.models import Vitamin, Brand, Category


class VitaminSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Vitamin.objects.all()

    def lastmod(self, obj):
        return obj.time_update


class BrandFilterSitemap(Sitemap):
    changefreq = 'weekly'  # Можно настроить в соответствии с частотой обновления ваших брендов
    priority = 0.9  # Настроить приоритет в соответствии с вашими предпочтениями SEO

    def items(self):
        # Возвращаем все объекты брендов
        return Brand.objects.all()

    def location(self, obj):
        # Возвращаем URL для фильтрации магазина по бренду
        # Предполагается, что у вас есть URL-конфигурация для магазина, которая принимает параметр бренда
        return reverse('shop') + f'?brand={obj.slug}'


class CategoryFilterSitemap(Sitemap):
    changefreq = 'weekly'  # Можно настроить в соответствии с частотой обновления ваших брендов
    priority = 0.9  # Настроить приоритет в соответствии с вашими предпочтениями SEO

    def items(self):
        # Возвращаем все объекты брендов
        return Category.objects.all()

    def location(self, obj):
        # Возвращаем URL для фильтрации магазина по бренду
        # Предполагается, что у вас есть URL-конфигурация для магазина, которая принимает параметр бренда
        return reverse('shop') + f'?category={obj.slug}'


class HomePageSitemap(Sitemap):
    changefreq = 'daily'
    priority = 1.0

    def items(self):
        return ['home']  # Предположим, что у вас есть URL с именем 'home' для вашей главной страницы

    def location(self, item):
        return reverse(item)

class ContactPageSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        return ['contacts']  # Предположим, что у вас есть URL с именем 'contact' для вашей страницы контактов

    def location(self, item):
        return reverse(item)
