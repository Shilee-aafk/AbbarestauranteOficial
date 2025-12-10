# Verificación de Configuración de Cloudinary

Para asegurar que las imágenes se guarden correctamente en Render y no desaparezcan al reiniciar:

## Variables de Entorno Requeridas en Render:

En el panel de Render, en Settings → Environment, verifica que estén configuradas:

1. **CLOUDINARY_CLOUD_NAME** - Tu cloud name de Cloudinary
2. **CLOUDINARY_API_KEY** - Tu API Key
3. **CLOUDINARY_API_SECRET** - Tu API Secret

## Verificación:

Para verificar que está funcionando correctamente:

```bash
# En Django shell
python manage.py shell
```

```python
from django.conf import settings

# Verificar que Cloudinary está configurado
print(settings.CLOUDINARY_STORAGE)

# Debería mostrar algo como:
# {
#     'CLOUD_NAME': 'tu_cloud_name',
#     'API_KEY': 'xxxxx',
#     'API_SECRET': 'xxxxx'
# }

# Verificar que DEFAULT_FILE_STORAGE usa Cloudinary
print(settings.DEFAULT_FILE_STORAGE)
# Debería mostrar: cloudinary_storage.storage.MediaCloudinaryStorage
```

## Si las imágenes siguen desapareciendo:

1. Verifica que las variables de entorno estén configuradas en Render
2. Reinicia el servicio después de configurar las variables
3. Comprueba los logs de Render para errores de Cloudinary
4. Asegúrate de que la carpeta `/media` no esté en el `.gitignore` (no debería guardarse en git)

## Alternativa de Debug:

Si aún tienes problemas, puedes agregar esta línea a `settings.py` temporalmente:

```python
# DEBUG: Print storage configuration
import sys
if 'test' not in sys.argv:
    print(f"FILE STORAGE: {DEFAULT_FILE_STORAGE}")
    print(f"CLOUDINARY CONFIG: {CLOUDINARY_STORAGE}")
```

Luego revisa los logs cuando cargues una imagen.
