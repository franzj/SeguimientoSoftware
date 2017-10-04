from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from drf_extra_fields.fields import Base64ImageField
from django.contrib.admin.models import LogEntry

# Modelos
from autentificacion.models import Usuario, Administrador
from seguimiento.models import (
    Proyecto,
    EquipoTrabajo,
    RequisitoUsuario,
    RequisitoSoftware,
    CruceMatriz,
    Tarea
)

class LogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        fields = '__all__'

# Módulo de Autentificación

class AdminUsuarioCreateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Administrador
        exclude = ('username', 'password', 'is_active', 'groups', 'user_permissions')
        read_only_fields = (
            'last_login',
            'date_joined',
            'is_superuser'
        )

class AdminUsuarioUpdateSerializar(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Administrador
        exclude = ('password', 'groups', 'user_permissions')
        read_only_fields = (
            'username',
            'last_login',
            'date_joined',
            'is_superuser'
        )

class SuperAdminUsuarioUpdateSerializar(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Administrador
        exclude = ('password', 'groups', 'user_permissions')
        read_only_fields = (
            'last_login',
            'date_joined'
        )

class UsuarioUpdateSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    avatar = Base64ImageField(required=False)
    
    class Meta:
        model = Usuario
        exclude = ('password', 'is_superuser', 'groups', 'user_permissions')
        read_only_fields = (
            'username',
            'last_login',
            'date_joined'
        )

class ChangePasswordSerializer(serializers.Serializer):
    password1 = serializers.CharField(max_length=128)
    password2 = serializers.CharField(max_length=128)

    def validate(self, data):
        """
        Verificamos que ambas contraseñas coinciden
        """
        password1 = data['password1']
        password2 = data['password2']
        if password1 and password2 and password1 != password2:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return data


# Módulo de Seguimiento de RU y RS

class EquipoTrabajoSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    usuario = serializers.SerializerMethodField('equipo_usuario')

    class Meta:
        model = EquipoTrabajo
        fields = ('id', 'usuario', 'tipo', 'proyecto')
        extra_kwargs = {'proyecto': {'write_only': True}}
    
    def equipo_usuario(self, equipo_trabajo):
        return {
            'id': equipo_trabajo.usuario.id,
            'username': equipo_trabajo.usuario.username
        }

    def create(self, validated_data):
        """
        Crear un equipo de trabajo, lanza un error si el proyecto ya tiene un
        Jefe de proyecto y se intenta asignar uno, lanza un error si el usuario
        no es de tipo Usuario,
        """
        usuario = self.context['request'].user

        query = EquipoTrabajo.objects.filter(
            proyecto=validated_data['proyecto'],
            tipo='J'
        ).first()

        if query and validated_data['tipo'] == 'J':
            # Ya existe el Jefe de proyecto
            raise serializers.ValidationError("Operación no permitida")
        if query and query.usuario != usuario:
            # El usuario no es el Jefe de proyecto
            raise serializers.ValidationError("Operación no permitida")

        return EquipoTrabajo.objects.create(
            usuario=validated_data['usuario'],
            proyecto=validated_data['proyecto'],
            tipo=validated_data['tipo']
        )


class ProyectoCreateSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    
    class Meta:
        model = Proyecto
        fields = ('id', 'nombre', 'descripcion',)

    def create(self, validated_data):
        """
        Crear un nuevo Proyecto, si el usuario está en sesión y este pertenece
        al grupo 'Usuarios comunes'
        """
        user = self.context['request'].user
        
        proyecto = Proyecto(
            nombre=validated_data['nombre'],
            descripcion=validated_data['descripcion']
        )
        proyecto.save()

        EquipoTrabajo.objects.create(
            usuario=user,
            proyecto=proyecto,
            tipo='J'
        )
        return proyecto


class ProyectoUpdateSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Proyecto
        exclude = ('equipo_trabajo',)
        read_only_fields = ('fecha_creacion', 'fecha_finalizacion',)


class RequisitoSoftwareSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    proyecto = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Proyecto.objects
    )
    
    class Meta:
        model = RequisitoSoftware
        exclude = ('cruce_matriz', 'tipo',)


class RequisitoUsuarioSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    proyecto = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Proyecto.objects
    )

    class Meta:
        model = RequisitoUsuario
        exclude = ('tipo',)


class TareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = '__all__'

