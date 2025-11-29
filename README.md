# Sistema de Gestión para Restaurante - AbbaHotel

Este es un sistema de gestión para restaurantes desarrollado con Django, diseñado para manejar pedidos, personal, imágenes de menú y reportes, con actualizaciones en tiempo real mediante Pusher (WebSockets).

## ✨ Características Principales

*   **Roles de Usuario:** Administrador, Recepcionista, Garzón y Cocinero con permisos específicos.
*   **Dashboards Personalizados:** Vistas optimizadas para las tareas de cada rol (Admin, Recepcionista, Garzón, Cocinero).
*   **Gestión de Pedidos en Tiempo Real:** Creación, actualización y seguimiento de pedidos que se reflejan instantáneamente en las pantallas correspondientes (cocina, garzones) mediante Pusher.
*   **🖼️ Gestión de Imágenes de Menú:** Carga de imágenes de platos con almacenamiento persistente en **Cloudinary**.
*   **Panel de Cocina Interactivo:** Visualización de pedidos pendientes y en preparación, con cambio de estado en tiempo real.
*   **Gestión Completa de Menú:** Panel de administración para gestionar platos, precios, descripciones e imágenes.
*   **🔍 Filtros Avanzados de Órdenes:** Búsqueda, filtrado por estado, rango de fechas y ordenamiento personalizado.
*   **📊 Reportes y Exportación:** Generación de reportes de ventas y exportación a Excel.
*   **🔔 Notificaciones Toast:** Notificaciones visuales elegantes para acciones del usuario.
*   **📱 Interfaz Responsiva:** Diseño adaptable a dispositivos móviles y de escritorio.

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

*   [Python](https://www.python.org/downloads/) (versión 3.8 o superior - recomendado 3.11+)
*   [MySQL Server](https://dev.mysql.com/downloads/mysql/)
*   [Git](https://git-scm.com/downloads/)
*   Cuenta en [Cloudinary](https://cloudinary.com/) (gratuita) para almacenamiento de imágenes
*   Cuenta en [Pusher](https://pusher.com/) (gratuita) para WebSockets en tiempo real

## ⚙️ Guía de Instalación Completa

### 1️⃣ Clonar el Repositorio

```bash
git clone https://github.com/Shilee-aafk/AbbarestauranteOficial.git
cd AbbarestauranteOficial
```

### 2️⃣ Crear y Activar Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Django
SECRET_KEY=tu-clave-secreta-super-segura-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# MySQL Database
DATABASE_USER=root
DATABASE_PASSWORD=root
DATABASE_NAME=abbarestaurante_db
DATABASE_HOST=localhost
DATABASE_PORT=3306

# Cloudinary (para imágenes de menú)
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=tu-api-key
CLOUDINARY_API_SECRET=tu-api-secret

# Pusher (para actualizaciones en tiempo real)
PUSHER_APP_ID=tu-pusher-app-id
PUSHER_KEY=tu-pusher-key
PUSHER_SECRET=tu-pusher-secret
PUSHER_CLUSTER=tu-pusher-cluster
```

**Cómo obtener las credenciales:**

**Cloudinary:**
1. Ve a https://cloudinary.com/ y registrate (gratuito)
2. En el dashboard, encontrarás Cloud Name, API Key y API Secret
3. Cópialos a tu archivo `.env`

**Pusher:**
1. Ve a https://pusher.com/ y registrate (plan gratuito disponible)
2. Crea un nuevo app/cluster
3. Obtén las credenciales del dashboard

### 5️⃣ Configurar Base de Datos MySQL

Abre MySQL y ejecuta:

```sql
CREATE DATABASE abbarestaurante_db;
```

### 6️⃣ Aplicar Migraciones

```bash
python manage.py migrate
```

### 7️⃣ Crear Datos de Prueba

```bash
python manage.py crear_usuarios
```

Este comando crea automáticamente:
- ✅ Todos los roles (Administrador, Recepcionista, Garzón, Cocinero)
- ✅ Usuarios de prueba para cada rol
- ✅ Permisos correctos para cada rol
- ✅ Menú inicial con platos de ejemplo

### 8️⃣ Ejecutar el Servidor

```bash
python manage.py runserver
```

Abre http://127.0.0.1:8000/ en tu navegador. Serás redirigido automáticamente al login.

---

## 🔑 Credenciales de Prueba

Todos los usuarios tienen contraseña: `password123`

| Rol               | Usuario          |
|-------------------|------------------|
| Administrador     | `admin_user`     |
| Recepcionista     | `recepcion_user` |
| Garzón            | `garzon_user`    |
| Cocinero          | `cocinero_user`  |

---

## 📁 Estructura del Proyecto

```
AbbarestauranteOficial/
├── AbbaRestaurante/
│   ├── settings.py              # Configuración principal
│   ├── urls.py                  # URLs del proyecto
│   ├── wsgi.py / asgi.py        # Configuración de servidor
│   └── context_processors.py    # Procesadores de contexto
│
├── restaurant/
│   ├── models.py                # MenuItem, Order, OrderItem, User, Group
│   ├── views.py                 # Vistas y APIs
│   ├── urls.py                  # URLs de la app
│   ├── admin.py                 # Configuración de admin
│   ├── signals.py               # Señales (Pusher updates)
│   ├── forms.py                 # Formularios Django
│   │
│   ├── templates/
│   │   ├── admin_dashboard.html          # Panel administrador
│   │   ├── waiter_dashboard.html         # Panel garzón
│   │   ├── cook_dashboard.html           # Panel cocinero
│   │   ├── receptionist_dashboard.html   # Panel recepcionista
│   │   ├── public_menu.html              # Menú público (con imágenes)
│   │   ├── base.html                     # Plantilla base
│   │   ├── registration/
│   │   │   ├── login.html
│   │   │   ├── signup.html
│   │   │   └── logged_out.html
│   │   └── partials/
│   │       └── cook_order_card.html
│   │
│   ├── static/
│   │   ├── restaurant/
│   │   │   ├── css/components.css
│   │   │   ├── images/
│   │   │   └── sounds/
│   │   └── admin/              # Archivos estáticos del admin
│   │
│   ├── management/commands/
│   │   ├── crear_usuarios.py   # Comando de setup
│   │   └── setup_permissions.py
│   │
│   └── migrations/             # Migraciones de BD
│
├── staticfiles/                # Archivos estáticos compilados
├── manage.py
├── requirements.txt
├── runtime.txt                 # Versión de Python
├── render.yaml                 # Configuración Render
└── README.md
```

---

## 🎨 Funcionalidades por Dashboard

### 👨‍💼 Dashboard Administrador
- ✅ Gestión completa del menú (crear, editar, eliminar platos)
- ✅ **Carga de imágenes** con almacenamiento en Cloudinary
- ✅ Vista de pedidos recientes con **filtros avanzados**
- ✅ Búsqueda por: N° de pedido, cliente, habitación
- ✅ Filtro por estado de pedido
- ✅ Filtro por rango de fechas
- ✅ Ordenar por: reciente, antiguo, mayor/menor monto
- ✅ Gestión de usuarios y permisos
- ✅ Generación de reportes
- ✅ Exportación a Excel

### 👨‍💻 Dashboard Recepcionista
- ✅ Crear nuevos pedidos
- ✅ Asignar número de habitación o identificador de cliente
- ✅ Ver menú completo con imágenes
- ✅ Vista en tiempo real de pedidos
- ✅ Cambiar estado de pedidos

### 🍽️ Dashboard Garzón
- ✅ Ver sus órdenes asignadas
- ✅ Actualizar estado de pedidos
- ✅ Recibir notificaciones cuando están listos
- ✅ Sonido de alerta para nuevos pedidos

### 👨‍🍳 Dashboard Cocinero
- ✅ Vista clara de pedidos pendientes
- ✅ Cambiar estado (Pendiente → En preparación → Listo)
- ✅ Actualizaciones en tiempo real
- ✅ Sonido de notificación para nuevas órdenes
- ✅ Visualización clara de ingredientes/notas

---

## 🖼️ Sistema de Imágenes (Cloudinary)

### ¿Cómo funciona?

1. **Administrador sube imagen** desde el dashboard
2. **Se envía a Cloudinary** (almacenamiento en la nube)
3. **Se genera URL automáticamente** y se guarda en BD
4. **Imagen aparece en menú público** con alta calidad

### Ventajas

- 📷 **Imágenes de alta calidad** con redimensionamiento automático
- 🚀 **Carga rápida** mediante CDN de Cloudinary
- 💾 **Persistencia en la nube** - no se pierden al reiniciar
- 🔄 **Sincronización automática** entre todos los clientes
- ⚡ **Optimización automática** - Cloudinary optimiza para web

### Proceso Técnico

```
Usuario sube imagen
        ↓
Endpoint /api/menu-item/<id>/upload-image/
        ↓
cloudinary.uploader.upload() 
        ↓
Se guarda: "cloudinary:{public_id}"
        ↓
Property image_url convierte a: https://res.cloudinary.com/.../
        ↓
Se muestra en templates con image.url property
        ↓
Persiste en la nube ✅
```

---

## 🔄 Tiempo Real (Pusher WebSockets)

El sistema usa **Pusher** para actualizaciones instantáneas:

- ✅ Nuevos pedidos aparecen al instante en todos los dashboards
- ✅ Cambios de estado se sincronizan en tiempo real
- ✅ Nuevas imágenes de menú aparecen inmediatamente
- ✅ Múltiples usuarios pueden trabajar simultáneamente

**Cómo funciona:**
- Django signals disparan eventos Pusher
- Pusher WebSocket envía actualizaciones a clientes
- JavaScript recibe cambios y actualiza DOM sin refrescar

---

## 🚀 Despliegue en Render

### Pasos para Desplegar

1. **Push a GitHub:**
```bash
git add .
git commit -m "Actualización para despliegue en Render"
git push origin main
```

2. **En Render (https://render.com):**
   - Conecta tu repositorio GitHub
   - Crea nuevo Web Service
   - Selecciona rama `main`
   - Configurar build command: `pip install -r requirements.txt && python manage.py migrate`
   - Configurar start command: `gunicorn AbbaRestaurante.wsgi:application`

3. **Variables de Entorno en Render:**

```
SECRET_KEY=tu-clave-secreta
DATABASE_URL=mysql://user:password@host:port/database
DEBUG=False
ALLOWED_HOSTS=tu-app.onrender.com

CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=tu-api-key
CLOUDINARY_API_SECRET=tu-api-secret

PUSHER_APP_ID=tu-pusher-app-id
PUSHER_KEY=tu-pusher-key
PUSHER_SECRET=tu-pusher-secret
PUSHER_CLUSTER=tu-pusher-cluster
```

4. **Desplegar:**
   - Render redeploy automáticamente cuando hagas push

### ✅ Verificar Despliegue

- Las imágenes deben mostrarse correctamente
- Los pedidos deben actualizarse en tiempo real
- Los filtros deben funcionar

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Propósito |
|-----------|----------|
| Django 5.2.7 | Framework web principal |
| MySQL 8.0 | Base de datos relacional |
| Django REST Framework | APIs |
| Cloudinary 1.44.1 | Almacenamiento de imágenes |
| Pusher | WebSockets en tiempo real |
| Tailwind CSS | Estilos y responsive design |
| JavaScript (Vanilla) | Interactividad en cliente |
| Pillow 11.0.0 | Procesamiento de imágenes |
| openpyxl | Exportación a Excel |

---

## 📊 Bases de Datos

### Modelo de Datos

```
MenuItem
├── id (PK)
├── name (CharField)
├── description (TextField)
├── price (DecimalField)
├── category (CharField)
├── available (BooleanField)
└── image (ImageField) → Cloudinary

Order
├── id (PK)
├── user_id (FK → User)
├── room_number (CharField)
├── client_identifier (CharField)
├── items (M2M → MenuItem through OrderItem)
├── status (CharField: pending|preparing|ready|served|paid|charged_to_room|cancelled)
├── created_at (DateTime)
├── tip_amount (DecimalField)
└── total_amount (DecimalField)

OrderItem
├── id (PK)
├── order_id (FK → Order)
├── menu_item_id (FK → MenuItem)
├── quantity (IntegerField)
├── note (TextField)
└── is_prepared (BooleanField)

User (Django Auth)
├── id (PK)
├── username
├── email
├── password (hashed)
├── groups (M2M → Group)
└── permissions

Group (Roles)
├── Administrador
├── Recepcionista
├── Garzón
└── Cocinero
```

---

## 🐛 Troubleshooting

### Imágenes no se muestran
- ✅ Verifica que CLOUDINARY_* estén en `.env`
- ✅ Verifica credenciales en Cloudinary dashboard
- ✅ Revisa console (F12) para errores HTTP

### Tiempo real no funciona
- ✅ Verifica que PUSHER_* estén en `.env`
- ✅ Verifica credenciales en Pusher dashboard
- ✅ Abre DevTools → Network → busca conexión WebSocket

### Base de datos no conecta
- ✅ Verifica que MySQL esté corriendo
- ✅ Revisa credenciales en `.env`
- ✅ Ejecuta: `python manage.py dbshell`

### Puerto 8000 ya está en uso
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :8000
kill -9 <PID>
```

---

## 📝 Comandos Útiles

```bash
# Crear superusuario
python manage.py createsuperuser

# Crear datos de prueba
python manage.py crear_usuarios

# Migraciones
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --fake-initial

# Collectar archivos estáticos
python manage.py collectstatic --noinput

# Shell interactivo
python manage.py shell

# Ejecutar tests
python manage.py test

# Limpieza de caché
python manage.py clear_cache
```

---

## 📞 Soporte y Contacto

Para preguntas, sugerencias o problemas:
- 📧 Abre un issue en [GitHub](https://github.com/Shilee-aafk/AbbarestauranteOficial)
- 💬 Contacta al equipo de desarrollo

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 👥 Contribuidores

- **Desarrollador Principal:** Kamil
- **Equipo:** AbbaHotel

---

**Última actualización:** Noviembre 2025
