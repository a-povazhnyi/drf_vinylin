import os

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from email.mime.image import MIMEImage


class AddCartItemEmailMessage(EmailMultiAlternatives):
    def __init__(self, request, context, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = context
        self.content_subtype = 'html'
        self.mixed_subtype = 'related'

        self.product_title = context['item'].product.title
        self.subject = f'\"{self.product_title}\" has been added to cart!'
        self.body = render_to_string(
            'orders/add_to_cart_email.html',
            context=context,
            request=request,
        )
        self.to = [request.user.email]
        self._create_inline_image_attachment()

    def _create_inline_image_attachment(self):
        image = self.context['item'].product.images.first()
        name, subtype = os.path.splitext(image.image.file.name)

        mimei_image = MIMEImage(image.image.read(), _subtype=subtype)
        mimei_image.add_header('Content-ID', f'<{image.image.name}>')
        return self.attach(mimei_image)


class OrderEmailMessage(EmailMultiAlternatives):
    def __init__(self, request, context, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = context
        self.content_subtype = 'html'
        self.mixed_subtype = 'related'

        self.to = [request.user.email]

        self.subject = 'You have made an order!'
        self.body = render_to_string(
            'orders/order_email.html',
            context=context,
            request=request,
        )
        self._create_inline_image_attachments()

    def _get_images(self):
        order_items = self.context.get('order_items')
        return (item.product.images.first().image for item in order_items)

    def _create_inline_image_attachments(self):
        images = self._get_images()

        for image in images:
            image_name = image.file.name
            name, subtype = os.path.splitext(image_name)

            mimei_image = MIMEImage(image.read(), _subtype=subtype)
            mimei_image.add_header('Content-ID', f'<{image.name}>')
            self.attach(mimei_image)
