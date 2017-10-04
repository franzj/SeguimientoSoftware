from django import forms
from autentificacion.models import Usuario
from django.contrib.auth.forms import UserCreationForm, UsernameField


class UsuarioCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ("username", "email")
        field_classes = {'username': UsernameField}
