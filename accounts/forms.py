from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Project, Task, Comment
from django.contrib.auth.password_validation import validate_password

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Username',
            'class': 'form-control'
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Email',
            'class': 'form-control'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Password',
            'class': 'form-control'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm Password',
            'class': 'form-control'
        })

    def clean_password2(self):
        # No custom password constraints
        return self.cleaned_data.get("password2")

    def clean_username(self):
        # No custom username constraints
        return self.cleaned_data.get("username")

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("username", "email", "role")

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'team']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'due_date', 'priority', 'status']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

