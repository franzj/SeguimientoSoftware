from rest_framework.authtoken.models import Token
from django.shortcuts import render
from .forms import UsuarioCreationForm
from django.middleware.csrf import get_token

def home(request):
    if request.user.is_authenticated:
        token = Token.objects.get(user=request.user)
        response = render(request, 'seguimiento/dashboard.html')
        response["Authorization"] = "Token %s" % token.key
        return response

    return render(request, 'seguimiento/index.html')


def registrar(request):
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'seguimiento/gracias.html')
    else:
        form = UsuarioCreationForm()
    return render(request, 'seguimiento/registrar.html', {'form': form})
