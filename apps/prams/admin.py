from django.contrib import admin
from .models import PRAMSStudy, PRAMSSignup


@admin.register(PRAMSStudy)
class PRAMSStudyAdmin(admin.ModelAdmin):
    list_display = ('title', 'datetime', 'max_capacity', 'current_signups', 'available_slots_display', 'bookings_service_id')
    list_filter = ('datetime',)
    search_fields = ('title', 'description', 'bookings_service_id')

    def available_slots_display(self, obj):
        return obj.available_slots
    available_slots_display.short_description = 'Slots remaining'


@admin.register(PRAMSSignup)
class PRAMSSignupAdmin(admin.ModelAdmin):
    list_display = ('study', 'participant_secure_id_masked', 'cancellation_pin', 'created_at')
    list_filter = ('study', 'created_at')
    raw_id_fields = ('study',)

    def participant_secure_id_masked(self, obj):
        if not obj.participant_secure_id or len(obj.participant_secure_id) < 4:
            return '***'
        return obj.participant_secure_id[:2] + '***' + obj.participant_secure_id[-2:]
    participant_secure_id_masked.short_description = 'Participant ID (masked)'
