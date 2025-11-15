# 🆓 Guía para Render Plan Free

Render ofrece un plan **completamente gratuito**, pero con algunas limitaciones. Esta guía te ayuda a deployar tu app aprovechando al máximo el plan free.

## ✅ Lo que SÍ funciona en Plan Free

- ✅ Hosting web (1 instancia)
- ✅ Base de datos PostgreSQL (gratuita, 90 días gratis)
- ✅ Dominio `.onrender.com` gratuito
- ✅ HTTPS/SSL gratuito
- ✅ Despliegue automático desde GitHub
- ✅ Variables de entorno
- ✅ Logs
- ✅ WebSockets (Pusher)

## ❌ Lo que NO funciona en Plan Free

- ❌ **Acceso a terminal/shell** (no puedes ejecutar comandos manualmente)
- ❌ Múltiples instancias
- ❌ Servicio entra en "sleep" después de 15 min sin tráfico
- ❌ Solo 0.5 GB de RAM

---

## 🚀 Cómo Desplegar Sin Terminal

### Problema: No puedo ejecutar `python manage.py migrate`

**Solución:** Las migraciones se ejecutan automáticamente en el **Build Step**.

### ¿Cómo?

Render ejecuta en este orden:

1. **Build Step** (automático, sin terminal)
   ```bash
   pip install -r requirements.txt
   python manage.py collectstatic --no-input
   python manage.py migrate          # ← AQUÍ
   python manage.py crear_usuarios   # ← AQUÍ
   ```

2. **Start Step** (tu app inicia)
   ```bash
   gunicorn AbbaRestaurante.wsgi:application
   ```

---

## 📋 Pasos Exactos para Desplegar

### 1. Prepara tu repositorio
```bash
git add .
git commit -m "feat: Configuración para Render plan free"
git push origin main
```

### 2. Ve a render.com

### 3. Crea nuevo Web Service
- Haz clic en **"+ New"** → **"Web Service"**
- Selecciona tu repositorio `AbbarestauranteOficial`
- Configura:

| Campo | Valor |
|-------|-------|
| **Name** | `abbarestaurante` |
| **Environment** | `Python 3` |
| **Region** | `Oregon` (o la más cercana) |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python manage.py crear_usuarios` |
| **Start Command** | `gunicorn AbbaRestaurante.wsgi:application` |
| **Plan** | `Free` |

### 4. Haz clic en **"Create Web Service"**

### 5. Espera a que termine el Build
- Ve a **Logs** para ver el progreso
- Si hay errores, búscalos en los logs

---

## 🔐 Variables de Entorno (Importante)

Después de crear el servicio, ve a **Environment** y añade:

```
DEBUG=False
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=tu-url-de-supabase
PUSHER_APP_ID=tu-app-id
PUSHER_KEY=tu-key
PUSHER_SECRET=tu-secret
PUSHER_CLUSTER=tu-cluster
RENDER_EXTERNAL_HOSTNAME=abbarestaurante.onrender.com
```

---

## 🐛 Troubleshooting Plan Free

### "Mi app entró en sleep después de 15 minutos"

**Causa:** Render duerme apps inactivas en plan free

**Soluciones:**
1. Usa un servicio como **Koyeb Monitor** (gratuito)
2. Upgrade a plan pagado
3. Es normal, cuando alguien accede, se despierta

### "Los archivos estáticos no se ven"

**Solución:**
- Asegúrate de que `python manage.py collectstatic --no-input` está en el Build Command
- Ya está incluido en la configuración

### "Error en migraciones durante el build"

**Qué hacer:**
1. Revisa los **Logs** en Render
2. Busca el error específico
3. Verifica que `DATABASE_URL` es correcto
4. Vuelve a desplegar

---

## 💡 Tips para Plan Free

1. **Usa Supabase para la BD** (gratuito y confiable)
2. **Monitorea los logs** regularmente
3. **Haz backups** de tu base de datos
4. **Ten un plan B** (puedes cambiar a Koyeb o PythonAnywhere fácilmente)
5. **Lee los términos de Render** sobre plan free

---

## 📊 Limitaciones que Debes Conocer

| Aspecto | Plan Free | Plan Pagado |
|--------|-----------|------------|
| **Instancias** | 1 | Múltiples |
| **RAM** | 0.5 GB | 1+ GB |
| **Sleep timeout** | 15 min | Nunca |
| **Base de datos** | Gratis (90 días) | Gratis después |
| **Dominio** | `.onrender.com` | Personalizado |
| **Costo** | $0 | $10+/mes |

---

## 🚀 Cuando Necesites Upgrade

Si tu app crece y necesitas:
- Más potencia
- Evitar "sleep"
- Múltiples instancias
- Dominio personalizado

Upgrade a plan pagado en Render o mígrate a otra plataforma.

---

**¡Tu app está lista para Render Free!** 🎉
