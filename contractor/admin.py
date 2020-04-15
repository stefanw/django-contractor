from django.contrib import admin
from django.utils import timezone

from .models import Contract


class ContractAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'created', 'updated',
        'created_by', 'updated_by', 'version'
    )
    readonly_fields = (
        'created', 'updated', 'created_by', 'updated_by',
        'version', 'webhook_log'
    )
    prepopulated_fields = {'slug': ('name',)}
    save_on_top = True
    ordering = ('-updated',)
    date_hierarchy = 'updated'
    actions = ['manual_update']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created = timezone.now()
            obj.created_by = request.user
        obj.updated = timezone.now()
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def manual_update(self, request, queryset):
        from .tasks import fetch_contract_result

        for contract in queryset:
            fetch_contract_result.delay(contract.pk)

        self.message_user(request, "Contract update triggered.")


admin.site.register(Contract, ContractAdmin)
