import os
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.conf import settings

# Create your models here.
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]
    CATEGORY_CHOICES = [
        ('Technical', 'Technical'),
        ('Billing', 'Billing'),
        ('General', 'General'),
    ]
    ticket_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    category = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = 'TCKT-' + str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.title}"


class UserRating(models.Model):
    """Per-user rating used by the userdashboard ratings page."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_ratings")
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="received_ratings")
    ticket_reference = models.CharField(max_length=50, blank=True)
    rating = models.PositiveSmallIntegerField()  # 1-5 overall rating
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    recommend = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.rating}/5 by {self.user} for {self.ticket_reference or 'N/A'}"


class ChatMessage(models.Model):
    """Simple direct message between two users (used for user/admin chat)."""

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    ticket_id = models.CharField(max_length=50, blank=True, null=True)
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.text[:30]}"


class MutedChat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="muted_chats")  # the muter
    contact = models.ForeignKey(User, on_delete=models.CASCADE, related_name="muted_by")  # the one muted
    muted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "contact")

    def __str__(self):
        return f"{self.user} muted {self.contact}"


class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='ticket_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ChatMessageAttachment(models.Model):
    """File attachments for chat messages"""
    message = models.ForeignKey(
        'ChatMessage', 
        on_delete=models.CASCADE, 
        related_name='attachments'
    )
    file = models.FileField(upload_to='chat_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f"Attachment for message {self.message.id}"
    
    @property
    def filename(self):
        return os.path.basename(self.file.name)
    
    @property
    def filesize(self):
        try:
            return self.file.size
        except (ValueError, OSError):
            return 0





class TicketStatusHistory(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="status_history"
    )
    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]


class TicketComment(models.Model):
    """Comments for tickets"""
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ticket_comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_internal = models.BooleanField(
        default=False,
        help_text="Internal comments are only visible to staff/admin users"
    )
    
    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["ticket", "created_at"]),
            models.Index(fields=["author", "created_at"]),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.ticket.ticket_id}"
    
    @property
    def can_edit(self):
        """Check if comment can be edited (within 5 minutes of creation)"""
        from django.utils import timezone
        return (timezone.now() - self.created_at).total_seconds() < 300
