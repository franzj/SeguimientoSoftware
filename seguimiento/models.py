from django.db import models
from django.utils import six, timezone
from django.http import request
from django.core.validators import MaxValueValidator, MinValueValidator


from autentificacion.models import Usuario


class Proyecto(models.Model):
    nombre = models.CharField(
        "Nombre del Proyecto",
        max_length=140,
    )
    descripcion = models.TextField("Descripción del Proyecto", null=True)
    fecha_creacion = models.DateField(
        "Fecha de Creación",
        default=timezone.now,
        help_text="Indica la fecha de creación del Proyecto"
    )
    fecha_finalizacion = models.DateField(
        "Fecha de Finalización",
        help_text="Indica la fecha de finalización del Proyecto",
        null=True
    )
    terminado = models.BooleanField("Terminado", default=False)
    # Llave foránea
    equipo_trabajo = models.ManyToManyField(
        Usuario,
        through='EquipoTrabajo'
    )

    def __str__(self):
        return self.nombre


ROLES_DE_TRABAJO = (
    ('J', 'Jefe de proyecto'),
    ('A', 'Analista'),
    ('D', 'Diseñador'),
    ('P', 'Programador'),
    ('T', 'Tester'),
)

class EquipoTrabajo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=1, choices=ROLES_DE_TRABAJO, default='P')

    def __str__(self):
        return "(Usuario: %s) (PyID: %i)" % (
            self.usuario.username, self.proyecto.id
        )


NECESIDAD = (
    ('O', 'Obligarorio'),
    ('N', 'No Obligarorio'),
)

NIVELES = (
    ('A', 'Alta'),
    ('M', 'Media'),
    ('B', 'Baja'),
)

TIPO = (
   ('U', 'Usuario'),
   ('S', 'Software'),
)

class RequisitoSoftwareManager(models.Manager):
    def get_queryset(self):
        return super(RequisitoSoftwareManager, self).get_queryset().filter(tipo='S')

class RequisitoUsuarioManager(models.Manager):
    def get_queryset(self):
        return super(RequisitoUsuarioManager, self).get_queryset().filter(tipo='U')


class Requisito(models.Model):
    nombre = models.CharField(max_length=140)
    descripcion = models.TextField(blank=True, default="")
    tipo = models.CharField(max_length=1, choices=TIPO, default="U")
    # Llaves foráneas
    proyecto = models.ForeignKey(Proyecto)
    cruce_matriz = models.ManyToManyField(
        "self", 
        through='CruceMatriz', 
        symmetrical=False,
        blank=True
    )

class RequisitoUsuario(Requisito):
    objects = RequisitoUsuarioManager()
    class Meta:
        proxy = True

class RequisitoSoftware(Requisito):
    objects = RequisitoSoftwareManager()
    class Meta:
        proxy = True
    
    def save(self, *args, **kwargs):
        self.tipo = 'S'
        super(RequisitoSoftware, self).save(*args, **kwargs)


class CruceMatriz(models.Model):
    from_requisito = models.ForeignKey(Requisito, related_name='from_requisito', on_delete=models.CASCADE)
    to_requisito = models.ForeignKey(Requisito, related_name='to_requisito', on_delete=models.CASCADE)
    
    class Meta:
        db_table = "cruce_matriz"


class Tarea(models.Model):
    nombre = models.CharField(max_length=140)
    avance = models.IntegerField(
        default=0,
        validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
    cruce_matriz = models.ForeignKey(CruceMatriz, on_delete=models.CASCADE)

