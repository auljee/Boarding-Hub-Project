from django.contrib import admin
from .models import HouseOwner, Room, Tenant, Payment

admin.site.register(HouseOwner)
admin.site.register(Room)
admin.site.register(Tenant)
admin.site.register(Payment)