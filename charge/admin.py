from django.contrib import admin

from charge.models import Charging

@admin.register(Charging)
class ChargingAdmin(admin.ModelAdmin): ...
