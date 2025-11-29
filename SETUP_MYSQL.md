# Setup MySQL Desarrollo Local

## Paso 1: Instalar las dependencias necesarias

```bash
pip install mysqlclient python-dotenv
```

## Paso 2: Configurar variables de entorno

Edita el archivo `.env` en la raíz del proyecto con tus credenciales de MySQL:

```env
# Django Configuration
DEBUG=True
SECRET_KEY=django-insecure-9q340snr7*@mbs+7z06vv=pq0j#voi*%&+hvw1l+8wn!90$i@p

# MySQL Database Configuration (Development)
DB_NAME=abbarestaurante
DB_USER=root
DB_PASSWORD=tu_contraseña_mysql_aqui
DB_HOST=127.0.0.1
DB_PORT=3306

# Pusher Configuration (Optional)
PUSHER_APP_ID=
PUSHER_KEY=
PUSHER_SECRET=
PUSHER_CLUSTER=
```

**Nota:** Si tu contraseña de MySQL está vacía, déjalo en blanco.

## Paso 3: Crear la base de datos en MySQL

Abre MySQL y ejecuta:

```sql
CREATE DATABASE IF NOT EXISTS abbarestaurante CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## Paso 4: Ejecutar las migraciones

```bash
python manage.py migrate
```

## Paso 5: Crear un superusuario (admin)

```bash
python manage.py createsuperuser
```

Sigue las instrucciones para crear tu usuario admin.

## Paso 6: Cargar datos iniciales (Opcional)

Si tienes un script de setup:

```bash
python manage.py crear_usuarios
python manage.py setup_permissions
```

## Paso 7: Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

La aplicación estará disponible en: `http://127.0.0.1:8000`

## Solución de problemas

### Error: "column ... does not exist"
Ejecuta nuevamente las migraciones:
```bash
python manage.py migrate
```

### Error: "Access denied for user 'root'@'localhost'"
Verifica que:
1. MySQL está corriendo
2. El usuario y contraseña en `.env` son correctos
3. La contraseña no tiene caracteres especiales (o usa comillas)

### Error: "Can't connect to MySQL server"
Asegúrate que MySQL esté corriendo:
- Windows: `mysql -u root -p`
- Si sale error, inicia el servicio de MySQL

## Configuración para Producción

Para usar en Render, solo necesitas:
1. No crear archivo `.env` en producción
2. Configurar la variable `DATABASE_URL` en Render
3. Django automáticamente detectará que es producción y usará PostgreSQL
