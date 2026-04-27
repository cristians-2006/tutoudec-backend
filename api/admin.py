from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType

from .models import Disponibilidad, Materia, Resena, Tutor, Tutoria


def _ensure_tutores_group() -> Group:
    """
    Grupo "Tutores" con permisos de modelo típicos.
    Nota: Django no trae permisos por-objeto por defecto; esto es a nivel modelo.
    """
    group, _ = Group.objects.get_or_create(name="Tutores")

    models_to_grant = [Tutor, Materia, Disponibilidad, Tutoria, Resena]
    perms: list[Permission] = []
    for model in models_to_grant:
        ct = ContentType.objects.get_for_model(model)
        perms.extend(Permission.objects.filter(content_type=ct))

    if perms:
        group.permissions.set(perms)

    return group


class TutorInline(admin.StackedInline):
    model = Tutor
    extra = 0
    fk_name = "usuario"
    filter_horizontal = ("materias",)


@admin.action(description="Marcar usuarios como tutores (crear perfil + grupo Tutores)")
def make_users_tutors(modeladmin, request, queryset):
    group = _ensure_tutores_group()
    for user in queryset:
        Tutor.objects.get_or_create(
            usuario=user,
            defaults={"especialidad": "Sin especificar"},
        )
        user.groups.add(group)


@admin.action(description="Quitar rol de tutor (eliminar perfil Tutor)")
def remove_users_tutors(modeladmin, request, queryset):
    for user in queryset:
        Tutor.objects.filter(usuario=user).delete()


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'creado_en')
    search_fields = ('nombre',)
    list_filter = ('creado_en',)


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'especialidad', 'nivel_experiencia', 'calificacion', 'tarifa_por_hora', 'disponible')
    list_filter = ('nivel_experiencia', 'disponible', 'calificacion')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'especialidad')
    filter_horizontal = ('materias',)
    readonly_fields = ('creado_en', 'actualizado_en')
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('usuario', 'foto', 'teléfono')
        }),
        ('Experiencia', {
            'fields': ('especialidad', 'nivel_experiencia', 'bio', 'materias')
        }),
        ('Detalles', {
            'fields': ('tarifa_por_hora', 'calificacion', 'disponible')
        }),
        ('Fechas', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Tutoria)
class TutoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'estudiante', 'tutor', 'materia', 'estado', 'fecha_inicio', 'duracion_minutos', 'tarifa')
    list_filter = ('estado', 'fecha_inicio', 'materia')
    search_fields = ('estudiante__username', 'tutor__usuario__username', 'materia__nombre')
    readonly_fields = ('creado_en', 'actualizado_en', 'duracion_minutos')
    fieldsets = (
        ('Participantes', {
            'fields': ('tutor', 'estudiante', 'materia')
        }),
        ('Horario', {
            'fields': ('fecha_inicio', 'fecha_fin', 'duracion_minutos', 'lugar')
        }),
        ('Detalles', {
            'fields': ('estado', 'descripcion', 'nota', 'tarifa')
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return self.readonly_fields + ('tutor', 'estudiante')
        return self.readonly_fields


@admin.register(Disponibilidad)
class DisponibilidadAdmin(admin.ModelAdmin):
    list_display = ("tutor", "dia_semana", "hora_inicio", "hora_fin", "activo")
    list_filter = ("activo", "dia_semana")
    search_fields = ("tutor__usuario__username", "tutor__usuario__first_name", "tutor__usuario__last_name")


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ("tutor", "estudiante", "calificacion", "creado_en")
    list_filter = ("calificacion", "creado_en")
    search_fields = ("tutor__usuario__username", "estudiante__username", "comentario")
    readonly_fields = ("creado_en",)


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    actions = [make_users_tutors, remove_users_tutors]
    inlines = [TutorInline]
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")