from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Tutor, Materia, Tutoria, Disponibilidad, Resena
from .serializers import (
    TutorSerializer, TutorListSerializer, MateriaSerializer,
    TutoriaSerializer, UserSerializer, DisponibilidadSerializer,
    ResenaSerializer, AdminUserSerializer
)
from .permissions import IsAdminOrReadOnly

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'detail': 'Se requiere usuario y contraseña'}, status=status.HTTP_400_BAD_REQUEST)

        # Soporte para login por email
        if '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                return Response({'detail': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            })
        return Response({'detail': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=request.data.get('username'),
                email=request.data.get('email'),
                password=request.data.get('password'),
                first_name=request.data.get('first_name', ''),
                last_name=request.data.get('last_name', '')
            )
            
            # Crear perfil de tutor si se solicita
            if request.data.get('role') == 'tutor':
                Tutor.objects.create(
                    usuario=user,
                    especialidad=request.data.get('especialidad', 'General')
                )
                
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Se requiere refresh token'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        except Exception:
            return Response({'detail': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)


class MateriaViewSet(viewsets.ModelViewSet):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'creado_en']
    ordering = ['nombre']
    
    @action(detail=True, methods=['get'])
    def tutorias(self, request, pk=None):
        """Obtener todas las tutorías de una materia"""
        materia = self.get_object()
        tutorias = materia.tutorias.all()
        serializer = TutoriaSerializer(tutorias, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def tutores(self, request, pk=None):
        """Obtener todos los tutores de una materia"""
        materia = self.get_object()
        tutores = materia.tutores.filter(disponible=True)
        serializer = TutorListSerializer(tutores, many=True)
        return Response(serializer.data)


class TutorViewSet(viewsets.ModelViewSet):
    queryset = Tutor.objects.select_related('usuario').prefetch_related('materias')
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nivel_experiencia', 'disponible', 'materias']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'especialidad']
    ordering_fields = ['calificacion', 'tarifa_por_hora', 'creado_en']
    ordering = ['-calificacion']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TutorListSerializer
        return TutorSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mi_perfil(self, request):
        """Obtener el perfil de tutor del usuario autenticado"""
        try:
            tutor = Tutor.objects.get(usuario=request.user)
            serializer = self.get_serializer(tutor)
            return Response(serializer.data)
        except Tutor.DoesNotExist:
            return Response(
                {'error': 'No tienes un perfil de tutor'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def tutorias(self, request, pk=None):
        """Obtener todas las tutorías de un tutor"""
        tutor = self.get_object()
        tutorias = tutor.tutorias.all()
        estado = request.query_params.get('estado')
        
        if estado:
            tutorias = tutorias.filter(estado=estado)
        
        serializer = TutoriaSerializer(tutorias, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def estadisticas(self, request, pk=None):
        """Obtener estadísticas de un tutor"""
        tutor = self.get_object()
        tutorias_totales = tutor.tutorias.count()
        tutorias_completadas = tutor.tutorias.filter(estado='completada').count()
        tutorias_pendientes = tutor.tutorias.filter(estado='pendiente').count()
        
        return Response({
            'tutorias_totales': tutorias_totales,
            'tutorias_completadas': tutorias_completadas,
            'tutorias_pendientes': tutorias_pendientes,
            'calificacion_promedio': tutor.calificacion,
            'tarifa_por_hora': str(tutor.tarifa_por_hora),
            'materias': tutor.materias.count(),
        })
    
    @action(detail=True, methods=['post'])
    def marcar_disponible(self, request, pk=None):
        """Marcar tutor como disponible"""
        tutor = self.get_object()
        tutor.disponible = True
        tutor.save()
        return Response({'status': 'Tutor marcado como disponible'})
    
    @action(detail=True, methods=['post'])
    def marcar_no_disponible(self, request, pk=None):
        """Marcar tutor como no disponible"""
        tutor = self.get_object()
        tutor.disponible = False
        tutor.save()
        return Response({'status': 'Tutor marcado como no disponible'})


class TutoriaViewSet(viewsets.ModelViewSet):
    queryset = Tutoria.objects.select_related('tutor', 'estudiante', 'materia').all()
    serializer_class = TutoriaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'tutor', 'estudiante', 'materia']
    search_fields = ['estudiante__username', 'tutor__usuario__username', 'materia__nombre']
    ordering_fields = ['fecha_inicio', 'creado_en', 'estado']
    ordering = ['-fecha_inicio']
    
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return qs
        if hasattr(user, 'perfil_tutor'):
            return qs.filter(tutor=user.perfil_tutor)
        return qs.filter(estudiante=user)

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'detail': 'Solo un administrador puede editar tutorias.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'detail': 'Solo un administrador puede editar tutorias.'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'detail': 'Solo un administrador puede eliminar tutorias.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Al crear una tutoría, calcular la tarifa y asignar estudiante"""
        # El estudiante autenticado puede registrar su propia tutoría.
        # Si quien crea es admin, puede asignar explícitamente otro estudiante.
        if self.request.user.is_staff and serializer.validated_data.get('estudiante'):
            tutoria = serializer.save()
        else:
            tutoria = serializer.save(estudiante=self.request.user)
        if not tutoria.tarifa and tutoria.tutor.tarifa_por_hora:
            duracion_horas = tutoria.duracion_minutos / 60
            tutoria.tarifa = tutoria.tutor.tarifa_por_hora * duracion_horas
            tutoria.save()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mis_tutorias(self, request):
        """Obtener las tutorías del usuario actual"""
        tutorias = Tutoria.objects.filter(estudiante=request.user)
        estado = request.query_params.get('estado')
        
        if estado:
            tutorias = tutorias.filter(estado=estado)
        
        serializer = self.get_serializer(tutorias, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mis_tutorias_como_tutor(self, request):
        """Obtener las tutorías del tutor actual (si lo es)"""
        try:
            tutor = Tutor.objects.get(usuario=request.user)
            tutorias = Tutoria.objects.filter(tutor=tutor)
            estado = request.query_params.get('estado')
            if estado:
                tutorias = tutorias.filter(estado=estado)
            serializer = self.get_serializer(tutorias, many=True)
            return Response(serializer.data)
        except Tutor.DoesNotExist:
            return Response({'error': 'No eres un tutor'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """Confirmar una tutoría"""
        tutoria = self.get_object()
        if tutoria.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden confirmar tutorías pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        tutoria.estado = 'confirmada'
        tutoria.save()
        serializer = self.get_serializer(tutoria)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        """Iniciar una tutoría"""
        tutoria = self.get_object()
        if tutoria.estado not in ['pendiente', 'confirmada']:
            return Response(
                {'error': 'La tutoría no puede ser iniciada en este estado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        tutoria.estado = 'en_progreso'
        tutoria.save()
        serializer = self.get_serializer(tutoria)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Completar una tutoría"""
        tutoria = self.get_object()
        if tutoria.estado != 'en_progreso':
            return Response(
                {'error': 'Solo se pueden completar tutorías en progreso'},
                status=status.HTTP_400_BAD_REQUEST
            )
        tutoria.estado = 'completada'
        tutoria.nota = request.data.get('nota', '')
        tutoria.save()
        serializer = self.get_serializer(tutoria)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancelar una tutoría"""
        tutoria = self.get_object()
        if tutoria.estado not in ['pendiente', 'confirmada', 'en_progreso']:
            return Response(
                {'error': 'La tutoría no puede ser cancelada en este estado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        tutoria.estado = 'cancelada'
        tutoria.save()
        serializer = self.get_serializer(tutoria)
        return Response(serializer.data)


class DisponibilidadViewSet(viewsets.ModelViewSet):
    queryset = Disponibilidad.objects.all()
    serializer_class = DisponibilidadSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tutor', 'dia_semana', 'activo']


class ResenaViewSet(viewsets.ModelViewSet):
    queryset = Resena.objects.all()
    serializer_class = ResenaSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tutor', 'estudiante', 'tutoria']
    ordering_fields = ['creado_en', 'calificacion']
    ordering = ['-creado_en']


class UserAdminViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la gestión de usuarios por parte de administradores.
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['id', 'username', 'date_joined']

    @action(detail=True, methods=['post'])
    def make_admin(self, request, pk=None):
        user = self.get_object()
        user.is_staff = True
        user.save()
        return Response({'status': f'Usuario {user.username} ahora es administrador'})

    @action(detail=True, methods=['post'])
    def remove_admin(self, request, pk=None):
        user = self.get_object()
        user.is_staff = False
        user.save()
        return Response({'status': f'Privilegios de administrador removidos para {user.username}'})