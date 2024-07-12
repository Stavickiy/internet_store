from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags, format_html

from internet_store import settings
from preorders.models import PreOrder


@receiver(pre_save, sender=PreOrder)
def preorder_status_changed(sender, instance, **kwargs):
    if instance.pk:
        prev_instance = sender.objects.get(pk=instance.pk)

        email_from = settings.EMAIL_HOST_USER

        if instance.status != prev_instance.status:
            # Статус заказа изменился
            order_link = format_html('<a href="{}">#{}<a/>', instance.get_absolute_url(), instance.pk)
            status_message = instance.get_status_display()
            message = format_html('Статус вашего предзаказа {} изменился на "{}"', order_link, status_message)

            subject = f'Изменение статуса предзаказа #{instance.pk}'
            html_message = render_to_string('email_template.html', {'message': message})
            plain_message = strip_tags(html_message)
            recipient_list = [instance.email, settings.MY_EMAIL]
            send_mail(subject, plain_message, email_from, recipient_list, html_message=html_message)

        elif instance.payment_status != prev_instance.payment_status:
            # Статус оплаты изменился
            order_link = format_html('<a href="{}">#{}<a/>', instance.get_absolute_url(), instance.pk)
            payment_status_message = instance.get_payment_status_display()
            message = format_html('Статус оплаты вашего предзаказа {} изменился на "{}"', order_link,
                                  payment_status_message)

            subject = f'Изменение статуса оплаты предзаказа #{instance.pk}'
            html_message = render_to_string('email_template.html', {'message': message})
            plain_message = strip_tags(html_message)
            recipient_list = [instance.email, settings.MY_EMAIL]
            send_mail(subject, plain_message, email_from, recipient_list, html_message=html_message)