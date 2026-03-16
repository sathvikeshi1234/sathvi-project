from django import forms
from .models import Ticket
from django.contrib.auth import get_user_model

User = get_user_model()

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise forms.ValidationError("Ticket title is required.")
        if len(title) < 5:
            raise forms.ValidationError("Ticket title must be at least 5 characters.")
        if len(title) > 100:
            raise forms.ValidationError("Ticket title must be less than 100 characters.")
        return title
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description:
            raise forms.ValidationError("Description is required.")
        if len(description) < 10:
            raise forms.ValidationError("Description must be at least 10 characters.")
        return description

class AdminTicketForm(forms.ModelForm):
    """Form for admin ticket editing that includes assignment field"""
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'category', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter the assigned_to field to only show agents
        self.fields['assigned_to'].queryset = User.objects.filter(
            userprofile__role__name='Agent', 
            is_active=True
        ).order_by('username')
        self.fields['assigned_to'].required = False
        self.fields['assigned_to'].empty_label = "Unassigned"