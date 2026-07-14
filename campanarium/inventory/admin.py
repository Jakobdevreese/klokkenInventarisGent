from django.contrib import admin
from .models import (
    Bell, Founder, Tower, Carillon, BellPartial, File,
    Bell_Tower, Carillon_Bell, Bell_Founder, Feedback,
)


class CreatedByAdminMixin:
    """Set created_by to the current user the first time an object is saved."""
    def save_model(self, request, obj, form, change):
        if not change and getattr(obj, 'created_by_id', None) is None:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if getattr(instance, 'created_by_id', None) is None:
                instance.created_by = request.user
            instance.save()
        formset.save_m2m()
        for obj in formset.deleted_objects:
            obj.delete()


# --- Inlines -----------------------------------------------------------------

class BellPartialInline(admin.TabularInline):
    model = BellPartial
    extra = 0


class BellTowerInline(admin.TabularInline):
    model = Bell_Tower
    extra = 0


class CarillonBellInline(admin.TabularInline):
    model = Carillon_Bell
    extra = 0


class BellFounderInline(admin.TabularInline):
    model = Bell_Founder
    extra = 0


# --- Core entities -----------------------------------------------------------

@admin.register(Bell)
class BellAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'year', 'pitch', 'weight', 'function')
    list_filter = ('function', 'year')
    search_fields = ('name', 'inscription', 'comments', 'pitch')
    inlines = [BellPartialInline, BellFounderInline, BellTowerInline, CarillonBellInline]


@admin.register(Founder)
class FounderAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ('primary_name', 'company_name', 'country', 'active_period')
    list_filter = ('country',)
    search_fields = ('primary_name', 'company_name', 'comments')


@admin.register(Tower)
class TowerAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'building', 'city', 'height')
    list_filter = ('city',)
    search_fields = ('name', 'building', 'full_address', 'comments')


@admin.register(Carillon)
class CarillonAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ('tower', 'established', 'number_of_bells', 'total_weight')
    list_filter = ('established',)
    search_fields = ('tower__name', 'comments')
    inlines = [CarillonBellInline]


@admin.register(BellPartial)
class BellPartialAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ('bell', 'partial', 'frequency', 'note', 'cents_deviation')
    list_filter = ('partial',)
    search_fields = ('bell__name', 'note')


@admin.register(File)
class FileAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'file_type', 'bell', 'carillon', 'founder', 'tower')
    list_filter = ('file_type',)
    search_fields = ('name', 'comments')


# --- Junction tables ---------------------------------------------------------

@admin.register(Bell_Tower)
class BellTowerAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ('bell', 'tower', 'is_current_location', 'start_date', 'end_date')
    list_filter = ('is_current_location',)
    search_fields = ('bell__name', 'tower__name')


@admin.register(Carillon_Bell)
class CarillonBellAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ('carillon', 'bell', 'relative_pitch', 'start_date', 'end_date')
    search_fields = ('bell__name', 'carillon__tower__name')


@admin.register(Bell_Founder)
class BellFounderAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ('bell', 'founder', 'type_of_work', 'date_of_work', 'is_primary_founder')
    list_filter = ('type_of_work', 'is_primary_founder')
    search_fields = ('bell__name', 'founder__primary_name')


# --- Tester feedback ---------------------------------------------------------

@admin.register(Feedback)
class FeedbackAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ('subject', 'content_object', 'is_resolved', 'created_by', 'created_at')
    list_filter = ('is_resolved',)
    search_fields = ('subject', 'message')
