# Sistema de Gestión para Restaurante - AbbaHotel

Este es un sistema de gestión para restaurantes desarrollado con Django, diseñado para manejar pedidos, personal y reportes, con actualizaciones en tiempo real mediante WebSockets (Django Channels).

## Características Principales

*   **Roles de Usuario:** Administrador, Recepcionista, Garzón y Cocinero con permisos específicos.
*   **Dashboards Personalizados:** Vistas optimizadas para las tareas de cada rol.
*   **Gestión de Pedidos en Tiempo Real:** Creación, actualización y seguimiento de pedidos que se reflejan instantáneamente en las pantallas correspondientes (cocina, garzones).
*   **Panel de Cocina Interactivo:** Visualización de pedidos pendientes y en preparación, con la capacidad de cambiar su estado.
*   **Gestión de Menú y Usuarios:** Paneles de administración para gestionar platos, precios, usuarios y roles.
*   **Reportes y Exportación:** Generación de reportes de ventas y exportación a Excel.

## Prerrequisitos

Antes de comenzar, asegúrate de tener instalado el siguiente software en tu sistema:

*   [Python](https://www.python.org/downloads/) (versión 3.8 o superior)
*   [MySQL Server](https://dev.mysql.com/downloads/mysql/) (asegúrate de que el servicio esté corriendo)
*   [Git](https://git-scm.com/downloads/)

## ⚙️ Guía de Instalación

Sigue estos pasos para configurar el proyecto en tu máquina local.

### 1. Clonar el Repositorio

Abre tu terminal (CMD, PowerShell, o Terminal) y clona este repositorio:

```bash
git clone <URL_DEL_REPOSITORIO>
cd AbbarestauranteOficial
```

### 2. Crear y Activar un Entorno Virtual

Es una buena práctica aislar las dependencias del proyecto.

```bash
# Crear el entorno virtual
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en macOS/Linux
# source venv/bin/activate
```

### 3. Instalar Dependencias

Con el entorno virtual activado, instala todas las librerías necesarias listadas en `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 4. Configuración de la Base de Datos

El proyecto está configurado para usar MySQL.

1.  **Abre tu cliente de MySQL** (línea de comandos, MySQL Workbench, etc.) e inicia sesión.
2.  **Crea la base de datos** que usará el proyecto:

    ```sql
    CREATE DATABASE abbarestaurante_db;
    ```

3.  **Verifica la conexión:** El archivo `AbbaRestaurante/settings.py` está configurado para usar `USER: 'root'` y `PASSWORD: 'root'`. Si tu configuración de MySQL es diferente, por favor, actualiza esas credenciales en el archivo.

### 5. Configuración Inicial de Django

Estos comandos prepararán la base de datos y crearán los datos iniciales para que puedas probar la aplicación.

1.  **Aplicar las migraciones** para crear las tablas en la base de datos:

    ```bash
    python manage.py migrate
    ```

2.  **Crear usuarios, roles y datos de prueba**. Este comando personalizado configura todo lo necesario para empezar:

    ```bash
    python manage.py crear_usuarios
    ```
    *Este comando creará los roles, los usuarios de prueba, asignará los permisos correctos y poblará el menú con algunos platos iniciales.*

### 6. Ejecutar el Servidor

¡Ya está todo listo! Inicia el servidor de desarrollo de Django.

```bash
python manage.py runserver
```

Abre tu navegador y ve a **http://127.0.0.1:8000/**. Serás redirigido a la página de login.

### 7. Ejecutar con Daphne (Opcional, para WebSockets)

El comando `runserver` es suficiente para la mayoría de las tareas, pero para probar la funcionalidad completa de WebSockets de una manera que simule más de cerca el entorno de producción, puedes usar `daphne`, el servidor ASGI.

```bash
daphne AbbaRestaurante.asgi:application
```

El servidor también estará disponible en **http://127.0.0.1:8000/**.

## 🔑 Usuarios de Prueba

Puedes usar las siguientes credenciales para iniciar sesión y probar los diferentes roles. La contraseña para todos es `password123`.

| Rol             | Usuario          | Contraseña    |
|-----------------|------------------|---------------|
| **Administrador** | `admin_user`     | `password123` |
| **Recepcionista** | `recepcion_user` | `password123` |
| **Garzón**        | `garzon_user`    | `password123` |
| **Cocinero**      | `cocinero_user`  | `password123` |

---