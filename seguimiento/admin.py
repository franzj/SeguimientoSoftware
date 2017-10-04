from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _
from .models import Proyecto


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('nombre',)}),
        ('Información Proyecto', {'fields': ('descripcion', 'terminado',)}),
        (_('Important dates'), {'fields': ('fecha_creacion', 'fecha_finalizacion')}),
    )
    list_display = ('nombre', 'fecha_creacion', 'fecha_finalizacion')
    list_filter = ('terminado',)
    readonly_fields = ('fecha_creacion', 'fecha_finalizacion',)
