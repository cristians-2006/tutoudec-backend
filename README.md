# Backend - TutoUdec

API REST del sistema de tutorías construida con Django REST Framework.

## Modelos de Datos

### Tutor
Representa un usuario tutor en el sistema.
```
- usuario: OneToOne con User de Django
- especialidad: CharField (máx. 100 caracteres)
- nivel_experiencia: ChoiceField (principiante, intermedio, avanzado, experto)
- bio: TextField (opcional)
- tarifa_por_hora: DecimalField
- teléfono: CharField (máx. 20 caracteres)
- foto: URLField (opcional)
- disponible: BooleanField (default=False)
- calificacion: DecimalField (solo lectura, calculada)
- materias: ManyToMany con Materia
- creado_en: DateTimeField (auto)
```

### Materia
Representa una materia o asignatura disponible para tutorías.
```
- nombre: CharField (máx. 100 caracteres, único)
- descripcion: TextField (opcional)
- creado_en: DateTimeField (auto)
```

### Tutoria
Representa una sesión de tutoría agendada.
```
- tutor: ForeignKey con Tutor
- estudiante: ForeignKey con User
- materia: ForeignKey con Materia
- fecha_inicio: DateTimeField
- duracion_minutos: IntegerField (default=60)
- lugar: CharField (máx. 200 caracteres)
- descripcion: TextField (opcional)
- estado: ChoiceField (pendiente, confirmada, en_progreso, completada, cancelada)
- nota: TextField (notas post-tutoría, opcional)
- tarifa: DecimalField (calculada automáticamente)
- creado_en: DateTimeField (auto)
```

### Disponibilidad
Define los horarios disponibles de un tutor.
```
- tutor: ForeignKey con Tutor
- dia: IntegerField (0=Lunes, 6=Domingo)
- hora_inicio: TimeField
- hora_fin: TimeField
```

### Resena
Reseña dejada por un estudiante sobre una tutoría.
```
- tutoria: OneToOne con Tutoria
- estudiante: ForeignKey con User
- tutor: ForeignKey con Tutor
- calificacion: IntegerField (1-5)
- comentario: TextField (opcional)
- creado_en: DateTimeField (auto)
```

---

## Vistas Principales (Viewsets)

### TutorViewSet
- `GET /api/tutores/` - Listar todos los tutores
- `POST /api/tutores/` - Crear perfil de tutor
- `GET /api/tutores/mi_perfil/` - Ver mi perfil (autenticado)
- `POST /api/tutores/{id}/marcar_disponible/` - Activar disponibilidad
- `POST /api/tutores/{id}/marcar_no_disponible/` - Desactivar disponibilidad
- `GET /api/tutores/{id}/estadisticas/` - Ver estadísticas

### MateriaViewSet
- `GET /api/materias/` - Listar materias
- `POST /api/materias/` - Crear materia (admin)
- `GET /api/materias/{id}/tutores/` - Tutores por materia

### TutoriaViewSet
- `GET /api/tutorias/` - Listar tutorías
- `POST /api/tutorias/` - Crear tutoría
- `GET /api/tutorias/mis_tutorias/` - Mis tutorías (autenticado)
- `POST /api/tutorias/{id}/confirmar/` - Confirmar
- `POST /api/tutorias/{id}/iniciar/` - Iniciar sesión
- `POST /api/tutorias/{id}/completar/` - Completar
- `POST /api/tutorias/{id}/cancelar/` - Cancelar

### DisponibilidadViewSet
- `GET /api/disponibilidades/` - Listar disponibilidades
- `POST /api/disponibilidades/` - Crear disponibilidad
- `DELETE /api/disponibilidades/{id}/` - Eliminar

### ResenaViewSet
- `GET /api/resenas/` - Listar reseñas
- `POST /api/resenas/` - Crear reseña

### AuthViewSet
- `POST /api/auth/login/` - Iniciar sesión
- `POST /api/auth/register/` - Registrarse
- `GET /api/auth/profile/` - Ver perfil (autenticado)

---

## Serializers

| Serializer | Modelo | Uso |
|------------|--------|-----|
| `TutorSerializer` | Tutor | Detalle completo |
| `TutorListSerializer` | Tutor | Lista resumida |
| `MateriaSerializer` | Materia | CRUD de materias |
| `TutoriaSerializer` | Tutoria | CRUD de tutorías |
| `UserSerializer` | User | Perfil de usuario |
| `DisponibilidadSerializer` | Disponibilidad | Gestión de horarios |
| `ResenaSerializer` | Resena | Reseñas |

---

## Permisos

- **Tutores**: Pueden ver y editar su propio perfil
- **Estudiantes**: Pueden crear tutorías y reseñas
- **Admin**: Acceso total a todos los recursos

---

## Configuración de Base de Datos

El proyecto usa **PostgreSQL** por defecto. Configurar en `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tutoudec_db',
        'USER': 'postgres',
        'PASSWORD': 'tu_contraseña',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## Comandos Útiles

```powershell
# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver 0.0.0.0:8000

# Reiniciar base de datos (¡CUIDADO!)
python manage.py flush
```
