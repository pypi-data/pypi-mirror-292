from django.contrib import admin

from allianceauth.services.hooks import get_extension_logger

from .models import (
    Agent, LocateChar, LocateCharMsg, Note, Target, TargetAlt, TargetGroup,
)

logger = get_extension_logger(__name__)


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("character", "corporation", "division", "level")
    list_filter = ["corporation", "division", "level"]


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("target", "author", "created_at", "text")
    list_filter = ["target", "author"]


@admin.register(LocateChar)
class LocateCharAdmin(admin.ModelAdmin):
    list_display = ("character", "created_at", "cache_expiry")


@admin.register(LocateCharMsg)
class LocateCharMsgAdmin(admin.ModelAdmin):
    list_display = ("locate_character", "character", "timestamp")
    list_filter = ("locate_character", "character")


@admin.register(TargetAlt)
class TargetAltAdmin(admin.ModelAdmin):
    list_display = ("character", "hard_cyno", "beacon_cyno", "scout", "pilot")
    list_filter = ("hard_cyno", "beacon_cyno", "scout", "pilot")


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ("character", "ship", "last_ship_location")
    list_filter = ("ship", "last_ship_location")


@admin.register(TargetGroup)
class TargetGroupAdmin(admin.ModelAdmin):
    list_display = ('id', )
