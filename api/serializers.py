from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Tutor, Materia, Tutoria, Disponibilidad, Resena


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id']

    def get_role(self, obj):
        if obj.is_staff or obj.is_superuser:
            return 'admin'
        if hasattr(obj, 'perfil_tutor'):
            return 'tutor'
        return 'estudiante'


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Serializer para gestión de usuarios por administradores (API).
    Permite editar flags y asignar permisos/grupos.
    """

    role = serializers.SerializerMethodField(read_only=True)
    groups = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=User.groups.rel.model.objects.all())
    user_permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=False,
        queryset=User.user_permissions.rel.model.objects.all(),
        required=False,
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
            'role',
        ]
        read_only_fields = ['id', 'role']

    def get_role(self, obj):
        if obj.is_staff or obj.is_superuser:
            return 'admin'
        if hasattr(obj, 'perfil_tutor'):
            return 'tutor'
        return 'estudiante'


class MateriaSerializer(serializers.ModelSerializer):
    total_tutorias = serializers.SerializerMethodField()
    
    class Meta:
        model = Materia
        fields = ['id', 'nombre', 'descripcion', 'creado_en', 'total_tutorias']
        read_only_fields = ['id', 'creado_en']

    def to_internal_value(self, data):
        """
        Compatibilidad con clientes que envían claves distintas
        (por ejemplo `name` en lugar de `nombre`).
        """
        mutable_data = dict(data)
        if not mutable_data.get('nombre'):
            if mutable_data.get('name'):
                mutable_data['nombre'] = mutable_data.get('name')
            elif mutable_data.get('titulo'):
                mutable_data['nombre'] = mutable_data.get('titulo')
            elif mutable_data.get('materia'):
                mutable_data['nombre'] = mutable_data.get('materia')
        return super().to_internal_value(mutable_data)
    
    def get_total_tutorias(self, obj):
        return obj.tutorias.count()


class TutorSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)
    usuario_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='usuario',
        write_only=True
    )
    materias = MateriaSerializer(many=True, read_only=True)
    materias_ids = serializers.PrimaryKeyRelatedField(
        queryset=Materia.objects.all(),
        many=True,
        source='materias',
        write_only=True
    )
    total_tutorias = serializers.SerializerMethodField()
    promedio_calificacion = serializers.ReadOnlyField(source='calificacion')
    
    class Meta:
        model = Tutor
        fields = [
            'id', 'usuario', 'usuario_id', 'especialidad', 'nivel_experiencia',
            'bio', 'tarifa_por_hora', 'calificacion', 'foto', 'teléfono',
            'disponible', 'materias', 'materias_ids', 'total_tutorias',
            'promedio_calificacion', 'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']
    
    def get_total_tutorias(self, obj):
        return obj.tutorias.count()


class TutoriaSerializer(serializers.ModelSerializer):
    tutor_nombre = serializers.CharField(source='tutor.usuario.get_full_name', read_only=True)
    estudiante_nombre = serializers.CharField(source='estudiante.get_full_name', read_only=True)
    materia_nombre = serializers.CharField(source='materia.nombre', read_only=True)
    
    class Meta:
        model = Tutoria
        fields = [
            'id', 'tutor', 'tutor_nombre', 'estudiante', 'estudiante_nombre',
            'materia', 'materia_nombre', 'fecha_inicio', 'fecha_fin',
            'duracion_minutos', 'estado', 'descripcion', 'lugar', 'tarifa',
            'nota', 'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['id', 'duracion_minutos', 'creado_en', 'actualizado_en']


class TutorListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar tutores"""
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    total_tutorias = serializers.SerializerMethodField()
    
    class Meta:
        model = Tutor
        fields = [
            'id', 'usuario_nombre', 'especialidad', 'nivel_experiencia',
            'tarifa_por_hora', 'calificacion', 'disponible', 'total_tutorias'
        ]
    
    def get_total_tutorias(self, obj):
        return obj.tutorias.filter(estado='completada').count()


class DisponibilidadSerializer(serializers.ModelSerializer):
    tutor_nombre = serializers.CharField(source='tutor.usuario.username', read_only=True)
    dia_semana_display = serializers.CharField(source='get_dia_semana_display', read_only=True)

    class Meta:
        model = Disponibilidad
        fields = [
            'id', 'tutor', 'tutor_nombre', 'dia_semana', 'dia_semana_display',
            'hora_inicio', 'hora_fin', 'activo'
        ]
        read_only_fields = ['id']


class ResenaSerializer(serializers.ModelSerializer):
    tutor_nombre = serializers.CharField(source='tutor.usuario.username', read_only=True)
    estudiante_nombre = serializers.CharField(source='estudiante.username', read_only=True)

    class Meta:
        model = Resena
        fields = [
            'id', 'tutor', 'tutor_nombre', 'estudiante', 'estudiante_nombre',
            'tutoria', 'calificacion', 'comentario', 'creado_en'
        ]
        read_only_fields = ['id', 'creado_en']