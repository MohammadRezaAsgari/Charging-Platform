import factory
from django.contrib.auth import get_user_model
from faker import Faker


User = get_user_model()
fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker("user_name")
    password = factory.PostGenerationMethodCall("set_password", "dolphins")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    class Meta:
        model = User
        django_get_or_create = ("username",)
