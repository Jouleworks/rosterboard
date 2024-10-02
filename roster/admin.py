from django.contrib import admin

from roster.models import Call, Duty, Event, Member, Rank, Status, VolumeRole, AccessRight, ServiceKiosk, Badge, History


# Register your models here.
@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    pass


@admin.register(Duty)
class DutyAdmin(admin.ModelAdmin):
    pass


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    pass


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    pass


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'key', 'event', 'sortOrder', 'hideFromColumns']


@admin.register(VolumeRole)
class VolumeRoleAdmin(admin.ModelAdmin):
    pass


@admin.register(AccessRight)
class AccessRightAdmin(admin.ModelAdmin):
    pass

@admin.register(ServiceKiosk)
class ServiceKioskAdmin(admin.ModelAdmin):
    pass

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    pass

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    pass