from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.template.response import TemplateResponse
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.contrib.admin.utils import unquote
from django.utils.html import escape
from django.http import Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from .models import Usuario, Administrador, UsuarioBase
from .forms import AdministradorCreationForm

csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


@admin.register(Administrador)
class AdministradorAdmin(UserAdmin):
    add_form_template = 'admin/user/admin_add_form.html'
    admin_creation_detail = 'admin/user/admin_creation_detail.html'
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'groups')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email'),
        }),
    )
    list_filter = ('is_staff', 'is_active',)
    readonly_fields = ('date_joined', 'last_login', 'groups', 'email',)
    add_form = AdministradorCreationForm
    
    def get_urls(self):
        return [
            url(
                r'^(.+)/creation-detail/$',
                self.admin_site.admin_view(self.user_creation_detail),
                name='auth_user_creation_detail',
            ),
        ] + super(AdministradorAdmin, self).get_urls()
    
    @sensitive_post_parameters_m
    def user_creation_detail(self, request, id):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = self.get_object(request, unquote(id))
        if user is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': force_text(self.model._meta.verbose_name),
                'key': escape(id),
            })
        if user.password != "":
            raise Http404("No encontrado")
        
        user.temp_password = UsuarioBase.objects.make_random_password()
        user.set_password(user.temp_password)
        user.save()
            
        context = {
            'title': 'Informe Usuario: %s' % escape(user.get_username()),
            'is_popup': False,
            'add': False,
            'change': False,
            'opts': self.model._meta,
            'original': user
        }
        context.update(self.admin_site.each_context(request))

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.admin_creation_detail,
            context,
        )
    
    def response_add(self, request, obj, post_url_continue=None):
        post_url_continue = '../{pk}/creation-detail/'.format(pk=obj.pk)
        return super(AdministradorAdmin, self).response_add(request, obj,
                                                   post_url_continue)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'groups')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    list_filter = ('is_active',)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active')
    readonly_fields = ('date_joined', 'last_login', 'groups', 'email', 'username',)

