from django.db import models
from django.db.utils import OperationalError
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group, GroupManager, UserManager
from django.utils import six, timezone

from PIL import Image
import random


class GrupoManager(GroupManager):
    use_in_migrations = False
    
    def get_grupo_SISRequisitos(self):
        """
        Busca el grupo con nombre "Usuarios comunes" si no crea el grupo
        """
        try:
            grupo = Grupo.objects.filter(name="Usuarios de SISRequisitos").first()
            if grupo:
                return grupo

            grupo = Grupo(name="Usuarios de SISRequisitos")
            grupo.save()
            return grupo
        except OperationalError:
            return None
    
    def get_grupo_admin(self):
        """
        Busca el grupo con nombre "Usuarios administradores" si no crea el grupo
        """
        try:
            grupo = Grupo.objects.filter(name="Usuarios administradores").first()
            if grupo:
                return grupo

            grupo = Grupo(name="Usuarios administradores")
            grupo.save()
            return grupo
        except Exception as e:
            return None


class Grupo(Group):
    objects = GrupoManager()

    class Meta:
        proxy = True
        verbose_name = _('group')
        verbose_name_plural = _('groups')


class UsuarioBase(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    avatar = models.ImageField("Foto de perfil", upload_to="avatar", blank=True)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def save(self, using=None, update_fields=None):
        super(UsuarioBase, self).save(using=using, update_fields=update_fields)
        #if self.avatar:
        #    image = Image.open(self.avatar)
        #    image = image.resize((120, 120), Image.ANTIALIAS)
        #    image.save(self.avatar.path, format='JPEG', quality=75)


class AdministradorManager(UserManager):
    def get_queryset(self):
        return super(AdministradorManager, self).get_queryset().filter(
            groups=Grupo.objects.get_grupo_admin()
        )
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)


class Administrador(UsuarioBase):
    objects = AdministradorManager()
    
    class Meta:
        proxy = True
        verbose_name = 'administrador'
        verbose_name_plural = 'administradores'
        
    def crear_usuario(self):
        username = self.email.split("@")[0]
        if Usuario.objects.filter(username=username).first():
            username = "%s%i" % (username, random.randint(0, 10))

        self.is_staff = True
        self.username = username
        
    def save(self, using=None, update_fields=None):
        if not self.pk:
            self.crear_usuario()
            super(Administrador, self).save(using=using, update_fields=update_fields)
            self.groups.add(Grupo.objects.get_grupo_admin())
        else:
            super(Administrador, self).save(using=using, update_fields=update_fields)


class UsuarioManager(UserManager):
    def get_queryset(self):
        return super(UsuarioManager, self).get_queryset().filter(
            groups=Grupo.objects.get_grupo_SISRequisitos()
        )


class Usuario(UsuarioBase):
    objects = UsuarioManager()
    
    class Meta:
        proxy = True
        verbose_name = _('user')
        verbose_name_plural = _('users')
        
    def save(self, using=None, update_fields=None):
        if not self.pk:
            super(Usuario, self).save(using=using, update_fields=update_fields)
            self.groups.add(Grupo.objects.get_grupo_SISRequisitos())
        else:
            super(Usuario, self).save(using=using, update_fields=update_fields)

