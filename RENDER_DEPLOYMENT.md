# 🚀 Guía de Despliegue en Render

Este documento guía paso a paso cómo desplegar tu aplicación Django en Render.

## Prerequisitos

1. Cuenta en **Render.com** (https://render.com)
2. Repositorio en **GitHub** con tu código
3. Base de datos PostgreSQL (usaremos Supabase)
4. Credenciales de Pusher para WebSockets

---

## 📋 Paso 1: Preparar tu Repositorio

Sube los siguientes archivos a tu repositorio (ya están creados):
- ✅ `Procfile` - Indica a Render cómo ejecutar tu app
- ✅ `runtime.txt` - Especifica la versión de Python
- ✅ `render.yaml` - Configuración de Render (opcional pero recomendado)
- ✅ `.env.example` - Template de variables de entorno

Todos estos archivos ya están listos. Solo debes hacer commit y push:

```bash
git add Procfile runtime.txt render.yaml .env.example
git commit -m "feat: Add Render deployment configuration"
git push origin main
```

---

## 🔐 Paso 2: Obtener las Credenciales Necesarias

### Base de datos (Supabase)
1. Ve a tu proyecto en Supabase
2. Copia la **Connection String** de PostgreSQL
3. Debe verse así: `postgresql://user:password@host:5432/postgres`

### Pusher (WebSockets en tiempo real)
1. Crea una cuenta en Pusher.com
2. Obtén:
   - `PUSHER_APP_ID`
   - `PUSHER_KEY`
   - `PUSHER_SECRET`
   - `PUSHER_CLUSTER`

### Secret Key de Django
Genera una nueva clave segura:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🌐 Paso 3: Crear el Servicio Web en Render

1. **Inicia sesión** en https://render.com
2. Haz clic en **"+ New"** → **"Web Service"**
3. **Conecta tu repositorio GitHub**
4. Configura:
   - **Name**: `abbarestaurante` (o el que prefieras)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --no-input`
   - **Start Command**: `gunicorn AbbaRestaurante.wsgi:application`
   - **Region**: `Oregon` (elige la más cercana)
   - **Plan**: `Free` (o el que prefieras)

5. **Haz clic en "Create Web Service"**

---

## 🔧 Paso 4: Configurar Variables de Entorno

En el dashboard de Render, ve a tu servicio y selecciona **"Environment"**:

Añade las siguientes variables:

| Variable | Valor |
|----------|-------|
| `DEBUG` | `False` |
| `SECRET_KEY` | [Tu clave secreta de Django] |
| `DATABASE_URL` | [Tu URL de Supabase PostgreSQL] |
| `PUSHER_APP_ID` | [Tu App ID de Pusher] |
| `PUSHER_KEY` | [Tu Key de Pusher] |
| `PUSHER_SECRET` | [Tu Secret de Pusher] |
| `PUSHER_CLUSTER` | [Tu Cluster de Pusher] |
| `RENDER_EXTERNAL_HOSTNAME` | [Tu dominio de Render] |

**Nota**: Render te asignará un dominio automáticamente, algo como `abbarestaurante.onrender.com`

---

## ✅ Paso 5: Ejecutar Migraciones (Importante)

Después de desplegar:

1. Abre la terminal de Render (en el dashboard del servicio)
2. Ejecuta:
   ```bash
   python manage.py migrate
   python manage.py crear_usuarios
   ```

O simplemente haz un nuevo push a tu repositorio (Render redesplegará automáticamente).

---

## 🌍 Paso 6: Verificar el Despliegue

1. Ve a tu aplicación en el dominio asignado
2. Verifica que todo funcione correctamente
3. Checa los logs en Render si hay errores

---

## 📱 Paso 7: Configurar Dominio Personalizado (Opcional)

Si quieres usar tu propio dominio (ej: `app.tudominio.com`):

1. En Render, ve a **Settings** → **Custom Domain**
2. Sigue las instrucciones para apuntar tu DNS

---

## 🐛 Solución de Problemas

### Error: "DATABASE_URL not configured"
- Verifica que la variable de entorno está configurada en Render

### Error: "Secret key not configured"
- Asegúrate de haber añadido `SECRET_KEY` en Environment Variables

### WebSockets no funcionan
- Verifica que tus credenciales de Pusher sean correctas
- Render soporta WebSockets nativamente

### Archivos estáticos no se ven (CSS, JS)
- El `Procfile` incluye `python manage.py collectstatic --no-input`
- Si aún no funciona, ejecuta manualmente desde la terminal de Render

---

## 📊 Monitoreo

En Render, puedes ver:
- **Logs**: Errores y mensajes de tu aplicación
- **Metrics**: CPU, memoria, etc.
- **Events**: Despliegues y cambios

---

## 💡 Tips

- Usa `DEBUG=False` en producción (ya está configurado)
- Mantén tus secretos seguros en Environment Variables
- Haz backups regulares de tu base de datos Supabase
- Monitorea los logs regularmente

---

¡Tu app está lista para Render! 🎉
