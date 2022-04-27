from django.contrib import admin

from WakeApp.core.models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass