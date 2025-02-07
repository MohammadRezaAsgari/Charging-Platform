import factory

from charge.models import Charging


class ChargingFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Charging
