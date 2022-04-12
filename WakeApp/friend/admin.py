from django.contrib import admin

from WakeApp.account.models import FriendRequest
from WakeApp.friend.models import FriendList


@admin.register(FriendList)
class FriendListAdmin(admin.ModelAdmin):
    pass


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    pass












