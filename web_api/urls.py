from django.conf.urls import url, include
from rest_framework import routers
# ViewSet
from .views import (
    AdminUserViewSet,
    UserViewSet,
    ProyectoViewSet,
    EquipoTrabajoViewSet,
    requisito_usuario_detail,
    requisito_software_detail,
    profile,
    tarea,
    tarea_detail,
    log_history_user
)

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'admins', AdminUserViewSet)
router.register(r'users', UserViewSet)
router.register(r'projects', ProyectoViewSet)
router.register(r'work_team', EquipoTrabajoViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^projects/(?P<proyecto>[^/.]+)/requisito-usuario/(?P<requisito>[^/.]+)/$',
        requisito_usuario_detail,
        name='requisito-usuario-detail'
    ),
    url(r'^projects/(?P<proyecto>[^/.]+)/requisito-usuario/(?P<RU>[^/.]+)/(?P<RS>[^/.]+)/tarea/$',
        tarea,
        name='tarea-list'
    ),
    url(r'^projects/(?P<proyecto>[^/.]+)/requisito-usuario/(?P<RU>[^/.]+)/(?P<RS>[^/.]+)/tarea/(?P<tarea>[^/.]+)/$',
        tarea_detail,
        name='tarea-detail'
    ),
    url(r'^projects/(?P<proyecto>[^/.]+)/requisito-software/(?P<requisito>[^/.]+)/$',
        requisito_software_detail,
        name='requisito-software-detail'
    ),
    url(r'^profile/', profile, name='profile'),
    url(r'^history/', log_history_user, name='history_user'),
]
