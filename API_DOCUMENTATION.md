# Documentación de la API de Tutorías

## Descripción General
API RESTful para gestionar un sistema de tutorías online. Permite a tutores registrarse, buscar materias, agendar sesiones y a estudiantes encontrar tutores calificados.

## Base URL
```
http://localhost:8000/api/
```

## Documentación Interactiva
- **Swagger UI**: http://localhost:8000/swagger/

## Endpoints Disponibles

### Materias

#### Listar todas las materias
```
GET /api/materias/
```
**Parámetros de búsqueda:**
- `search`: Buscar por nombre o descripción
- `ordering`: Ordenar por `nombre` o `creado_en`

**Ejemplo:**
```
GET /api/materias/?search=matemática&ordering=nombre
```

#### Crear una materia
```
POST /api/materias/
```
**Body:**
```json
{
  "nombre": "Matemática Avanzada",
  "descripcion": "Cálculo, álgebra lineal y ecuaciones diferenciales"
}
```

#### Obtener tutores de una materia
```
GET /api/materias/{id}/tutores/
```

#### Obtener tutorías de una materia
```
GET /api/materias/{id}/tutorias/
```

---

### Tutores

#### Listar todos los tutores
```
GET /api/tutores/
```
**Parámetros:**
- `nivel_experiencia`: `principiante`, `intermedio`, `avanzado`, `experto`
- `disponible`: `true` o `false`
- `search`: Buscar por nombre, username o especialidad
- `ordering`: Ordenar por `calificacion`, `tarifa_por_hora`, `creado_en`

**Ejemplo:**
```
GET /api/tutores/?disponible=true&nivel_experiencia=avanzado&ordering=-calificacion
```

#### Registrar un nuevo tutor
```
POST /api/tutores/
```
**Body:**
```json
{
  "usuario_id": 1,
  "especialidad": "Matemática",
  "nivel_experiencia": "avanzado",
  "bio": "Profesor de matemática con 10 años de experiencia",
  "tarifa_por_hora": "50.00",
  "teléfono": "555-1234",
  "foto": "https://ejemplo.com/foto.jpg",
  "disponible": true,
  "materias_ids": [1, 2, 3]
}
```

#### Mi perfil de tutor
```
GET /api/tutores/mi_perfil/
```
*Requiere autenticación*

#### Obtener tutorías de un tutor
```
GET /api/tutores/{id}/tutorias/
```
**Parámetros:**
- `estado`: Filtrar por estado

#### Estadísticas de un tutor
```
GET /api/tutores/{id}/estadisticas/
```

#### Marcar tutor como disponible
```
POST /api/tutores/{id}/marcar_disponible/
```

#### Marcar tutor como no disponible
```
POST /api/tutores/{id}/marcar_no_disponible/
```

---

### Tutorías

#### Listar todas las tutorías
```
GET /api/tutorias/
```
**Parámetros:**
- `estado`: `pendiente`, `confirmada`, `en_progreso`, `completada`, `cancelada`
- `tutor`: ID del tutor
- `estudiante`: ID del estudiante
- `materia`: ID de la materia
- `search`: Buscar por nombre de usuario o materia
- `ordering`: Ordenar por `fecha_inicio`, `creado_en`, `estado`

**Ejemplo:**
```
GET /api/tutorias/?estado=confirmada&ordering=-fecha_inicio
```

#### Crear una tutoría
```
POST /api/tutorias/
```
**Body:**
```json
{
  "tutor": 1,
  "estudiante": 2,
  "materia": 1,
  "fecha_inicio": "2024-03-10T14:00:00Z",
  "duracion_minutos": 60,
  "lugar": "Online - Zoom",
  "descripcion": "Sesión de repaso para examen final"
}
```

#### Mis tutorías
```
GET /api/tutorias/mis_tutorias/
```
*Requiere autenticación*
**Parámetros:**
- `estado`: Filtrar por estado

#### Confirmar una tutoría
```
POST /api/tutorias/{id}/confirmar/
```

#### Iniciar una tutoría
```
POST /api/tutorias/{id}/iniciar/
```

#### Completar una tutoría
```
POST /api/tutorias/{id}/completar/
```
**Body:**
```json
{
  "nota": "Excelente sesión, el estudiante aprendió rápido"
}
```

#### Cancelar una tutoría
```
POST /api/tutorias/{id}/cancelar/
```

---

## Estados de una Tutoría

| Estado | Descripción |
|--------|-------------|
| `pendiente` | Tutoría recién creada, esperando confirmación |
| `confirmada` | Ambas partes aceptaron la sesión |
| `en_progreso` | La sesión está en desarrollo |
| `completada` | La sesión finalizó correctamente |
| `cancelada` | La sesión fue cancelada |

---

## Niveles de Experiencia

| Nivel | Descripción |
|-------|-------------|
| `principiante` | 1-2 años de experiencia |
| `intermedio` | 2-5 años de experiencia |
| `avanzado` | 5-10 años de experiencia |
| `experto` | 10+ años de experiencia |

---

## Ejemplos de Flujo Completo

### 1. Tutor se registra
```
1. POST /api/tutores/ → Crear perfil de tutor
2. POST /api/tutores/{id}/materias/ → Agregar materias
3. POST /api/tutores/{id}/marcar_disponible/ → Marcar disponible
```

### 2. Estudiante busca tutor
```
1. GET /api/materias/ → Ver materias disponibles
2. GET /api/tutores/?search=matemática → Buscar tutores
3. GET /api/tutores/{id}/ → Ver detalles del tutor
```

### 3. Agendar una tutoría
```
1. POST /api/tutorias/ → Crear tutoría (estado: pendiente)
2. POST /api/tutorias/{id}/confirmar/ → Confirmar (estado: confirmada)
3. POST /api/tutorias/{id}/iniciar/ → Iniciar sesión (estado: en_progreso)
4. POST /api/tutorias/{id}/completar/ → Finalizar (estado: completada)
```

---

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| `200` | OK |
| `201` | Creado correctamente |
| `400` | Solicitud inválida |
| `401` | Autenticación requerida |
| `403` | Permiso denegado |
| `404` | No encontrado |
| `500` | Error del servidor |

---

## Autenticación

Para endpoints protegidos, usa Token Authentication:

```
Header: Authorization: Token {tu_token}
```

Para obtener tu token:
```
POST /api-token-auth/
```
*Nota: Este endpoint requiere instalación de `djangorestframework.authtoken`*

---

## CORS

La API está configurada para aceptar solicitudes desde:
- `http://localhost:3000`
- `http://localhost:8000`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:8000`

Para agregar más orígenes, edita `CORS_ALLOWED_ORIGINS` en `settings.py`.

---

## Notas

- Todas las tutorías se crean con la tarifa calculada automáticamente basada en la tarifa por hora del tutor
- La duración en minutos se calcula automáticamente si se proporciona `fecha_fin`
- Los campos de fecha deben estar en formato ISO 8601: `YYYY-MM-DDTHH:MM:SSZ`
