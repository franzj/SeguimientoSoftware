from django.conf import settings
from django.contrib import admin
from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework.authtoken import views

from weasyprint import HTML, CSS
from django.template.loader import get_template
from django.http import HttpResponse

""""
def generar_pdf(request):
    print("\n\n\n", request.POST, "\n\n\n")
    html_template = get_template(request.data)
    pdf_file = HTML(string=html_template).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="salida.pdf"'
    return response
"""

urlpatterns = [
    url(r'^', include('seguimiento.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^web-api/', include('web_api.urls')),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', views.obtain_auth_token),
    #url(r'^generar-pdf/', generar_pdf),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
