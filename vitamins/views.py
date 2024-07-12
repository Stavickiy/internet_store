from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.http import HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from django.views.generic import ListView, DetailView, CreateView, TemplateView

from internet_store import settings
from .forms import SearchForm, RequestForDeliveryForm
from .models import Category, Vitamin, Brand, Tag, ExchangeRate, DeliveryCost, VitaminImage, Percent, DeliveryRequest


def calculate_price(vitamins):
    """
    Gets vitamin object or queryset

    Calculate final price and sale price if vitamin has discount
    Returns vitamin object or vitamins queryset
    """
    percent = Percent.objects.all().first().percent
    exchange_rate = ExchangeRate.objects.all().first().rate
    delivery_cost = DeliveryCost.objects.all().first().cost_per_kg

    if isinstance(vitamins, Vitamin):
        vitamins.final_price = round((vitamins.price * exchange_rate) * (1 + max(percent, vitamins.percent) / 100) +
                                     (vitamins.weight * delivery_cost))
        if vitamins.discount:
            vitamins.sale_price = round(vitamins.final_price * (1 - (vitamins.discount / 100)))
    else:
        for vitamin in vitamins:
            vitamin.final_price = round((vitamin.price * exchange_rate) * (1 + max(percent, vitamin.percent) / 100) +
                                        (vitamin.weight * delivery_cost))
            if vitamin.discount:
                vitamin.sale_price = round(vitamin.final_price * (1 - (vitamin.discount / 100)))
    return vitamins


class VitaminHome(ListView):
    """
    A ListView subclass to display a list of vitamins on the home page.
    """
    model = Vitamin
    template_name = 'new/index.html'
    context_object_name = 'vitamins'

    def get_queryset(self):
        """
        Returns a queryset of vitamins ordered by the total_sold field.

        Retrieves vitamins from the database where the count is greater than 0, orders them
        by the total_sold field in descending order, and prefetches related brand and main image data.
        Calculates the price for each vitamin and returns the queryset.

        Returns:
            Queryset: A queryset of vitamins with calculated prices.
        """
        vitamins = Vitamin.objects \
                       .filter(count__gt=0) \
                       .order_by('-total_sold') \
                       .select_related('brand') \
                       .prefetch_related(
            Prefetch('images', queryset=VitaminImage.objects.filter(is_main=True)[:1], to_attr='main_image')
        )[:8]
        return calculate_price(vitamins)


def custom_page_not_found_view(request, exception):
    return render(request, '404.html', {'title': 'Страница не найдена'}, status=404)


class ShowVitamin(DetailView):
    """
    A DetailView subclass to display details of a specific vitamin.

    Retrieves the details of a specific vitamin from the database based on the provided slug,
    calculates prices for the vitamin and its analogs, and passes the data to the template for rendering.
    """
    model = Vitamin
    template_name = 'new/details.html'
    slug_url_kwarg = 'vit_slug'
    context_object_name = 'vitamin'

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Returns the context data to pass to the template.

        Retrieves the details of the current vitamin object and its analogs,
        calculates prices for the vitamin and its analogs, sorts analogs by priority,
        retrieves additional vitamins from the database, and passes all data to the template.

        Returns:
            dict: A dictionary containing the context data.
        """
        context = super().get_context_data(**kwargs)
        vitamin = context['vitamin']

        # Retrieve and calculate prices for analogs
        analogs = calculate_price(vitamin.analog.all().select_related('brand') or
                                  vitamin.analog_set.all().select_related('brand'))
        analogs_data = [{'vitamin': calculate_price(vitamin), 'priority': 1}] + \
                       [{'vitamin': v, 'priority': 0} for v in analogs]
        analogs_data.sort(key=lambda v: v['vitamin'].packaging)
        context['analogs'] = analogs_data

        # Retrieve additional vitamins from the database
        context['vitamins_cat'] = calculate_price(
            Vitamin.objects.filter(count__gt=0).order_by('?').select_related('brand').
            prefetch_related(Prefetch('images', queryset=VitaminImage.objects.
                                      filter(is_main=True)[:1], to_attr='main_image'))[8:12])

        # Pass the title of the vitamin to the context
        context['title'] = vitamin.title
        return context

    def get_object(self, queryset=None):
        """
        Returns the vitamin object based on the provided slug.

        Retrieves the vitamin object from the database based on the slug extracted from the URL.

        Returns:
            Model: The vitamin object.
        """
        prefetch = Prefetch('images', queryset=VitaminImage.objects.order_by('-is_main', 'image'))
        vitamin = Vitamin.objects.prefetch_related(prefetch).get(slug=self.kwargs['vit_slug'])
        return vitamin


class ShopVitamin(ListView):
    """
    A ListView subclass to display a list of vitamins in the shop.

    Retrieves a list of vitamins from the database based on applied filters,
    calculates prices for the vitamins, and passes the data to the template for rendering.
    """

    template_name = 'new/shop.html'
    context_object_name = 'vitamins'
    paginate_by = 6
    extra_context = {'title': 'Витамины и биодобавки из США'}

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Returns the context data to pass to the template.

        Retrieves additional context data such as tags, categories, pagination details, and current filters,
        and passes the data to the template.

        Returns:
            dict: A dictionary containing the context data.
        """
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        context['cats'] = Category.objects.all()
        context['page_range'] = context['paginator'].get_elided_page_range(
            context['page_obj'].number, on_each_side=2, on_ends=1
        )
        context['current_filters'] = {
            'brand': self.request.GET.get('brand', ''),
            'category': self.request.GET.get('category', ''),
            'tag': self.request.GET.get('tag', ''),
            'discount': self.request.GET.get('discount', ''),
            'query': self.request.GET.get('query', ''),
        }
        if self.request.GET.get('brand', ''):
            context['brand'] = get_object_or_404(Brand, slug=self.request.GET.get('brand', ''))
        return context

    def get_queryset(self):
        """
        Returns the queryset of vitamins based on applied filters.

        Retrieves a queryset of vitamins from the database based on applied filters such as brand, category, tag,
        discount, and search query. Calculates prices for the vitamins and returns the queryset.

        Returns:
            Queryset: A queryset of vitamins with calculated prices.
        """
        queryset = Vitamin.objects.select_related('brand').prefetch_related(
            Prefetch('images', queryset=VitaminImage.objects.filter(is_main=True), to_attr='main_images')
        )

        filters = {}
        brand_slug = self.request.GET.get('brand')
        cat_slug = self.request.GET.get('category')
        tag_slug = self.request.GET.get('tag')
        discount = self.request.GET.get('discount')
        query = self.request.GET.get('query')

        if brand_slug:
            filters['brand__slug'] = brand_slug
        if cat_slug:
            filters['cat__slug'] = cat_slug
        if tag_slug:
            filters['tags__slug__in'] = [tag_slug]
        if discount:
            filters['discount__gt'] = 0
            filters['count__gt'] = 0

        if filters:
            queryset = queryset.filter(**filters)

        if query:
            queryset = queryset.filter(Q(title__icontains=query) |
                                       Q(cat__name__icontains=query) |
                                       Q(brand__name__icontains=query) |
                                       Q(product_code__icontains=query) |
                                       Q(slug__icontains=query))

        return calculate_price(queryset)


class RequestForDelivery(LoginRequiredMixin, CreateView):
    """
    A CreateView subclass for handling requests for delivery.

    Allows authenticated users to submit delivery requests using a form.
    Upon successful submission, sends a confirmation email to the user and the admin.
    """
    model = DeliveryRequest
    form_class = RequestForDeliveryForm
    template_name = 'new/request_for_delivery.html'
    success_url = reverse_lazy('request_for_delivery')

    def form_valid(self, form):
        """
        Handles the valid form submission.

        Sets the requesting user, sends a confirmation email to the user and the admin,
        and displays a success message.

        Returns:
            HttpResponseRedirect: Redirects to the success URL.
        """
        form.instance.user = self.request.user  # Установка пользователя, который создает запрос
        response = super().form_valid(form)

        request_id = self.object.id
        messages.success(self.request, 'Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.')
        subject = f'Ваш заявка #{request_id} успешно оформлена'
        message = f'Ваш завка #{request_id} оформлена!!! В ближайшее время наш менеджер обработает ее и' \
                  f' свяжется с вами для подтверждения и уточнения деталей.'

        html_message = render_to_string('email_template.html', {'message': message})

        plain_message = strip_tags(html_message)
        email_from = settings.EMAIL_HOST_USER
        send_mail(subject, plain_message, email_from, [self.object.email, settings.MY_EMAIL], html_message=html_message)
        return response

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Retrieves additional context data to pass to the template.

        Adds the title to the context data.

        Returns:
            dict: A dictionary containing the context data.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Заявка на доставку под заказ'
        return context


class ContactView(TemplateView):
    """
    A TemplateView subclass for displaying contact information.

    Displays the contact information on the template specified by 'template_name'.
    Additional context data can be provided using 'extra_context'.
    """
    template_name = "new/contacts.html"
    extra_context = {'title': 'Наши Контакты'}
