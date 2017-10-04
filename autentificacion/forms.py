from django import forms
from .models import Administrador

class AdministradorCreationForm(forms.ModelForm):
    class Meta:
        model = Administrador
        fields = ('first_name', 'last_name', 'email',)
    
    def __init__(self, *args, **kwargs):
        super(AdministradorCreationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
    
    def save(self, commit=True):
        admin = super(AdministradorCreationForm, self).save(commit=False)
        if commit:
            admin.save()
        return admin
