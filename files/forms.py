# files/forms.py
from django import forms
from .models import File

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file', 'description', 'tags', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows':2, 'class':'form-control', 'placeholder':'Short description...'}),
            'tags': forms.TextInput(attrs={'class':'form-control', 'placeholder':'comma, separated'}),
        }

class FileEditForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['filename', 'description', 'tags', 'is_public']
        widgets = {
            'filename': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'rows':2, 'class':'form-control'}),
            'tags': forms.TextInput(attrs={'class':'form-control'}),
        }
