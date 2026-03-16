from django.contrib import admin
from .models import Ticket, TicketAttachment, TicketStatusHistory, TicketComment

# Register your models here.
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("ticket_id", "title", "status", "priority", "created_by", "assigned_to", "created_at")
    list_filter = ("status", "priority", "created_at")
    search_fields = ("ticket_id", "title")
    list_editable = ('status', 'priority')
    ordering = ('-created_at',)


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ("ticket", "file", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("ticket__ticket_id", "ticket__title", "file")


@admin.register(TicketStatusHistory)
class TicketStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("ticket", "old_status", "new_status", "changed_by", "changed_at")
    list_filter = ("new_status", "old_status", "changed_at")
    search_fields = ("ticket__ticket_id", "ticket__title", "changed_by__username")
    ordering = ("-changed_at",)
    readonly_fields = ("ticket", "old_status", "new_status", "changed_by", "changed_at")


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ("ticket", "author", "content_preview", "created_at", "is_internal")
    list_filter = ("created_at", "is_internal", "ticket")
    search_fields = ("ticket__ticket_id", "ticket__title", "author__username", "content")
    ordering = ("-created_at",)
    readonly_fields = ("ticket", "author", "created_at", "updated_at")
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content