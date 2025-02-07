import factory

from wallet.models import Invoice


class InvoiceFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Invoice
