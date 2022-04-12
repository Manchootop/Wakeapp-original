from django.contrib import admin

# Register your models here.
from WakeApp.account.models import Profile, WakeAppUser


@admin.register(WakeAppUser)
class WakeAppUserAdmin(admin.ModelAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass
