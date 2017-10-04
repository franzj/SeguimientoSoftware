from rest_framework import viewsets, mixins
from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import detail_route, api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE

# Models
from autentificacion.models import Usuario, Administrador
from seguimiento.models import (
    Proyecto,
    RequisitoUsuario,
    EquipoTrabajo,
    RequisitoSoftware,
    CruceMatriz,
    Tarea
)

# Serializers
from .serializers import (
    SuperAdminUsuarioUpdateSerializar,
    AdminUsuarioCreateSerializer,
    AdminUsuarioUpdateSerializar,
    UsuarioUpdateSerializer,
    ChangePasswordSerializer,
    ProyectoCreateSerializer,
    ProyectoUpdateSerializer,
    EquipoTrabajoSerializer,
    RequisitoUsuarioSerializer,
    RequisitoSoftwareSerializer,
    TareaSerializer,
    LogEntrySerializer
)
# Permisos
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .permissions import (
    IsAdminUser,
    IsSuperAdminOrIsSelfProfile,
    isAdminUserOrAnonymousUser
)

# Módulo de Autentificación

@receiver(post_save, sender=Usuario)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

@api_view()
@permission_classes([IsAuthenticated])
def profile(request):
    return Response(
        UsuarioUpdateSerializer(
            request.user,
            context={'request': request}
        ).data
    )
    
# Paginación

class CustomPagination(PageNumberPagination):
    page_size = 20


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = Administrador.objects.order_by('-is_active')
    serializer_class = AdminUsuarioUpdateSerializar
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_fields = ('username', 'email',)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'POST':
            serializer_class = AdminUsuarioCreateSerializer
        elif self.request.user.is_superuser:
            serializer_class = SuperAdminUsuarioUpdateSerializar
        return serializer_class

    @detail_route(
        methods=['POST'],
        permission_classes=[IsAuthenticated, IsSuperAdminOrIsSelfProfile],
        url_path='change-password'
    )
    def set_password(self, request, pk=None):
        try:
            admin = Administrador.objects.get(pk=pk)
            serializer = ChangePasswordSerializer(admin, data=request.data)
        except Administrador.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            admin.set_password(serializer.data['password2'])
            admin.save()
            return Response({'message': 'Se cambió la contraseña con éxito'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Usuario.objects.order_by('-is_active')
    serializer_class = UsuarioUpdateSerializer
    filter_fields = ('username', 'email',)
    pagination_class = CustomPagination
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]
    
    @detail_route(
        methods=['POST'],
        permission_classes=[IsAuthenticated, IsSuperAdminOrIsSelfProfile],
        url_path='change-password'
    )
    def set_password(self, request, pk=None):
        try:
            user = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.data['password2'])
            user.save()
            return Response({'message': 'Se cambió la contraseña con éxito'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Módulo de RU y RS

class EquipoTrabajoViewSet(viewsets.ModelViewSet):
    queryset = EquipoTrabajo.objects.order_by('id')
    serializer_class = EquipoTrabajoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    #filter_fields = ('usuario', 'proyecto',)


class ProyectoViewSet(viewsets.ModelViewSet):
    queryset = Proyecto.objects.order_by('terminado')
    serializer_class = ProyectoUpdateSerializer
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend,)
    filter_fields = ('equipo_trabajo',)
    search_fields = ('nombre',)
    pagination_class = CustomPagination
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'POST':
            serializer_class = ProyectoCreateSerializer
        return serializer_class
    
    def list(self, request, *args, **kwargs):
        if ('equipo_trabajo' in request.query_params):
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'results': serializer.data
            })
            
        return super(ProyectoViewSet, self).list(request, *args, **kwargs)
    
    @detail_route(
        methods=['GET', 'POST', 'DELETE'],
        permission_classes=[IsAuthenticatedOrReadOnly],
        url_path='equipo-trabajo'
    )
    def equipo_trabajo(self, request, pk=None):
        if request.method == 'DELETE':
            query = EquipoTrabajo.objects.filter(
                proyecto__pk=pk, usuario__pk=request.query_params["usuario"]
            )
            query.delete()
    
        if request.method == 'POST':
            usuario = Usuario.objects.filter(username=request.data["username"]).first()
            if not usuario:
                return Response(status=status.HTTP_404_NOT_FOUND)
                
            query = EquipoTrabajo.objects.filter(
                proyecto__pk=pk, usuario__pk=request.data["id"]
            )
            eliminar = []
            for equipo_trabajo in query:
                try:
                    if not any(roles["id"] == equipo_trabajo.id for roles in request.data["roles"]):
                        eliminar.append(equipo_trabajo)
                except KeyError:
                    pass

            for item in eliminar:
                item.delete()
            
            for item in request.data["roles"]:
                if not 'id' in item.keys():
                    EquipoTrabajo.objects.create(
                        proyecto=Proyecto.objects.get(pk=pk),
                        usuario=usuario,
                        tipo=item["rol"]
                    )
        try:
            query = EquipoTrabajo.objects.filter(proyecto__pk=pk)
            serializer = EquipoTrabajoSerializer(
                query, 
                many=True, 
                context={'request': request}
            )
            return Response({ 'results': serializer.data })
        except RequisitoUsuario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    @detail_route(
        methods=['GET', 'POST'],
        permission_classes=[IsAuthenticatedOrReadOnly],
        url_path='requisito-usuario'
    )
    def requisito_usuario(self, request, pk=None):
        if request.method == 'POST':
            request.data['proyecto'] = int(pk)
            serializer = RequisitoUsuarioSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(instance).pk,
                    object_id=instance.id,
                    object_repr=instance.nombre,
                    action_flag=ADDITION
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        try:
            query = RequisitoUsuario.objects.filter(proyecto__pk=pk)
            serializer = RequisitoUsuarioSerializer(query, many=True)
            return Response({ 'results': serializer.data })
        except RequisitoUsuario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
    @detail_route(
        methods=['GET', 'POST'],
        permission_classes=[IsAuthenticatedOrReadOnly],
        url_path='requisito-software'
    )
    def requisito_software(self, request, pk=None):
        if request.method == 'POST':
            request.data['proyecto'] = int(pk)
            serializer = RequisitoSoftwareSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(instance).pk,
                    object_id=instance.id,
                    object_repr=instance.nombre,
                    action_flag=ADDITION
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        try:
            query = RequisitoSoftware.objects.filter(proyecto__pk=pk)
            serializer = RequisitoSoftwareSerializer(query, many=True)
            return Response({ 'results': serializer.data })
        except RequisitoSoftware.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @detail_route(
        methods=['GET'],
        permission_classes=[IsAuthenticated],
        url_path='tareas'
    )
    def tareas(self, request, pk=None):
        query = Tarea.objects.filter(cruce_matriz__from_requisito__proyecto__pk=pk).all()
        serializer = TareaSerializer(query, many=True)
        return Response({ 'results': serializer.data })

@api_view(['GET', 'PUT', 'DELETE'])
def requisito_usuario_detail(request, proyecto=None, requisito=None):
    try:
       requisito_usuario = RequisitoUsuario.objects.filter(pk=requisito, proyecto=proyecto).first()
    except RequisitoUsuario.DoesNotExist:
        return Response(status.HTTP_404_NOT_FOUND)
        
    if request.method == 'PUT':
        request.data['proyecto'] = proyecto
        serializer = RequisitoUsuarioSerializer(requisito_usuario, data=request.data)
        if serializer.is_valid():
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(requisito_usuario).pk,
                object_id=requisito_usuario.id,
                object_repr=requisito_usuario.nombre,
                action_flag=CHANGE
            )
            query = CruceMatriz.objects.filter(
                from_requisito__proyecto__pk=proyecto,
                from_requisito=requisito_usuario
            )
            eliminar = []
            cruce_matriz = request.data["cruce_matriz"]
            for requisito in query:
                if not requisito.id in cruce_matriz:
                    eliminar.append(requisito)

            for requisito_id in cruce_matriz:
                if not any(requisito.id == requisito_id for requisito in query):
                    CruceMatriz.objects.create(
                        from_requisito=requisito_usuario,
                        to_requisito=RequisitoSoftware.objects.get(pk=requisito_id)
                    )
            
            for item in eliminar:
                item.delete()
            
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        requisito_usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = RequisitoUsuarioSerializer(requisito_usuario)
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
def requisito_software_detail(request, proyecto=None, requisito=None):
    try:
       requisito_software = RequisitoSoftware.objects.filter(pk=requisito, proyecto=proyecto).first()
    except RequisitoSoftware.DoesNotExist:
        return Response(status.HTTP_404_NOT_FOUND)
        
    if request.method == 'PUT':
        request.data['proyecto'] = proyecto
        serializer = RequisitoSoftwareSerializer(requisito_software, data=request.data)
        if serializer.is_valid():
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(requisito_software).pk,
                object_id=requisito_software.id,
                object_repr=requisito_software.nombre,
                action_flag=CHANGE
            )
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        requisito_software.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = RequisitoSoftwareSerializer(requisito_software)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def tarea(request, proyecto=None, RU=None, RS=None):
    cruce_matriz = CruceMatriz.objects.filter(from_requisito__pk=RU, to_requisito__pk=RS).first()
    
    if request.method == 'POST':
        request.data['cruce_matriz'] = cruce_matriz.id
        serializer = TareaSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(instance).pk,
                object_id=instance.id,
                object_repr=instance.nombre,
                action_flag=ADDITION
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    try:
        query = Tarea.objects.filter(cruce_matriz=cruce_matriz)
        serializer = TareaSerializer(query, many=True)
        return Response({ 'results': serializer.data })
    except RequisitoSoftware.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'PUT', 'DELETE'])
def tarea_detail(request, proyecto=None, RU=None, RS=None, tarea=None):
    try:
        cruce_matriz = CruceMatriz.objects.filter(from_requisito__pk=RU, to_requisito__pk=RS).first()
        tarea = Tarea.objects.filter(pk=tarea, cruce_matriz=cruce_matriz).first()
    except Tarea.DoesNotExist:
        return Response(status.HTTP_404_NOT_FOUND)
        
    if request.method == 'PUT':
        request.data['cruce_matriz'] = cruce_matriz.id
        serializer = TareaSerializer(tarea, data=request.data)
        if serializer.is_valid():
            serializer.save()
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(tarea).pk,
                object_id=tarea.id,
                object_repr=tarea.nombre,
                action_flag=ADDITION,
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        tarea.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = TareaSerializer(tarea)
    return Response(serializer.data)


@api_view(['GET'])
def log_history_user(request):
    query = LogEntry.objects.filter(user__pk=request.user.id)
    serializer = LogEntrySerializer(query, many=True)
    return Response(serializer.data)

