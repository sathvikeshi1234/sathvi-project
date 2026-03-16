from rest_framework import serializers
from .models import Ticket, TicketComment

class RecentTicketSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(source="created_by.username")
    subject = serializers.CharField(source="title")

    class Meta:
        model = Ticket
        fields = ["ticket_id", "customer", "subject", "status", "priority"]


class DashboardStatsSerializer(serializers.Serializer):
    total_tickets = serializers.IntegerField()
    open_tickets = serializers.IntegerField()
    resolved_today = serializers.IntegerField()
    avg_rating = serializers.FloatField()
    distribution = serializers.DictField()


class TicketSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)
    created_by_id = serializers.IntegerField(source="created_by.id", read_only=True)
    assigned_to_full_name = serializers.SerializerMethodField(read_only=True)
    assigned_to_username = serializers.CharField(source="assigned_to.username", read_only=True, allow_null=True)
    assigned_to_id = serializers.IntegerField(source="assigned_to.id", read_only=True, allow_null=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_id",
            "title",
            "description",
            "status",
            "priority",
            "category",
            "created_at",
            "updated_at",
            "created_by_username",
            "created_by_id",
            "assigned_to_full_name",
            "assigned_to_username",
            "assigned_to_id",
        ]
        read_only_fields = [
            "id",
            "ticket_id",
            "created_at",
            "updated_at",
            "created_by_username",
            "created_by_id",
            "assigned_to_full_name",
            "assigned_to_username",
            "assigned_to_id",
        ]

    def create(self, validated_data):
        # created_by will be injected from the view via serializer.save(created_by=...)
        return Ticket.objects.create(**validated_data)

    def get_assigned_to_full_name(self, obj):
        user = getattr(obj, "assigned_to", None)
        if not user:
            return None
        full_name = user.get_full_name()
        return full_name or None


class TicketCommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    author_full_name = serializers.SerializerMethodField(read_only=True)
    can_edit = serializers.BooleanField(read_only=True)

    class Meta:
        model = TicketComment
        fields = [
            "id",
            "content",
            "created_at",
            "updated_at",
            "is_internal",
            "author_username",
            "author_full_name",
            "can_edit",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "author_username",
            "author_full_name",
            "can_edit",
        ]

    def get_author_full_name(self, obj):
        return obj.author.get_full_name() or obj.author.username

    def create(self, validated_data):
        # author will be injected from view via serializer.save(author=...)
        return TicketComment.objects.create(**validated_data)