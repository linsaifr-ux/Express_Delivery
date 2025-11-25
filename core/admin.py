from django.contrib import admin
from .models import User, CustomerProfile, ServiceType, Package, TrackingEvent, Invoice

admin.site.register(User)
admin.site.register(CustomerProfile)
admin.site.register(ServiceType)
admin.site.register(Package)
admin.site.register(TrackingEvent)
admin.site.register(Invoice)
