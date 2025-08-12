# 🆓 Guía GRATUITA - GitHub Actions + Google Drive Sync

**¡MÉTODO 100% GRATUITO!** Sin necesidad de Google Cloud Console ni costos.

## ✨ Ventajas del Método Gratuito

- ✅ **Sin costos** de Google Cloud
- ✅ **Configuración simple** con OAuth2
- ✅ **Sin límites de facturación**
- ✅ **Acceso completo** a Google Drive
- ✅ **Sin necesidad** de cuenta de servicio

---

## 🚀 Configuración en 3 Pasos Simples

### 📦 Paso 1: Configurar OAuth2 (Local)

1. **Instala las dependencias**:
   ```bash
   pip install -r scripts/requirements-free.txt
   ```

2. **Ejecuta el configurador gratuito**:
   ```bash
   python scripts/setup_oauth_free.py
   ```

3. **Sigue las instrucciones**:
   - Se abrirá tu navegador automáticamente
   - Inicia sesión en Google
   - Autoriza el acceso a Google Drive
   - Copia la URL de redirección completa
   - Pégala en la terminal

4. **Resultado**: Se crearán estos archivos:
   - `oauth_credentials.json` - Credenciales OAuth2
   - `refresh_token.txt` - Token de actualización
   - `github_secrets_template.txt` - Plantilla para GitHub

### 🔐 Paso 2: Configurar GitHub Secrets

1. **Ve a tu repositorio** en GitHub
2. **Navega a** Settings > Secrets and variables > Actions
3. **Agrega estos 3 secrets**:

#### Secret 1: GOOGLE_OAUTH_CREDENTIALS
```json
# Contenido de tu archivo JSON descargado de Google Developers Console
# Ver SETUP_OAUTH_GUIDE.md para crear tus propias credenciales
```

#### Secret 2: GOOGLE_REFRESH_TOKEN
```
# Copia el contenido de refresh_token.txt
tu_refresh_token_aqui
```

#### Secret 3: GOOGLE_DRIVE_FOLDER_ID
```
# El ID de tu carpeta de Google Drive
# https://drive.google.com/drive/folders/[ESTE_ES_EL_ID]
1a2b3c4d5e6f7g8h9i0j
```

### 🎯 Paso 3: Obtener ID de Carpeta

1. **Abre Google Drive** en tu navegador
2. **Navega a la carpeta** que quieres sincronizar
3. **Copia el ID** desde la URL:
   ```
   https://drive.google.com/drive/folders/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74mMQ
                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                          ESTE ES TU FOLDER_ID
   ```
4. **Pégalo** en el secret `GOOGLE_DRIVE_FOLDER_ID`

---

## 🔄 Funcionamiento Automático

### ⏰ Sincronización Programada
- **Frecuencia**: Cada 30 minutos automáticamente
- **Triggers**: Push a main, ejecución manual
- **Detección**: Solo descarga archivos nuevos/modificados

### 📁 Estructura de Archivos
```
tu-repositorio/
├── google-drive-sync/              # 📁 Archivos sincronizados
│   ├── documento1.pdf              # 📄 Tus archivos
│   ├── imagen.jpg                  # 🖼️ Imágenes
│   ├── carpeta1/                   # 📂 Subcarpetas
│   │   └── archivo.txt             # 📄 Archivos anidados
│   └── SYNC_SUMMARY_FREE.md        # 📊 Resumen de sync
└── scripts/
    └── sync_state_free.json        # 💾 Estado de sincronización
```

### 📊 Monitoreo
- **Logs detallados** en GitHub Actions
- **Archivo de resumen** generado en cada sync
- **Estado persistente** para optimizar sincronizaciones

---

## 🧪 Prueba Local (Opcional)

Para probar antes de usar GitHub Actions:

```bash
# 1. Configurar variables de entorno
export GOOGLE_DRIVE_FOLDER_ID="tu_folder_id_aqui"

# 2. Asegurar archivos de configuración
ls oauth_credentials.json refresh_token.txt

# 3. Ejecutar sincronización
python scripts/sync_google_drive_free.py
```

---

## ⚙️ GitHub Workflows Incluidos

### 🔄 Sincronización Principal
**Archivo**: `.github/workflows/google-drive-sync.yml`
- Ejecuta cada 30 minutos
- Trigger manual disponible
- Commits automáticos cuando hay cambios

### 🔔 Webhook (Opcional)
**Archivo**: `.github/workflows/google-drive-webhook.yml`  
- Para notificaciones instantáneas
- Requiere configuración adicional de webhook

---

## 🔍 Resolución de Problemas

### ❌ Error: "Invalid refresh token"
**Solución**: Ejecuta nuevamente `setup_oauth_free.py`

### ❌ Error: "Folder not found"
**Solución**: Verifica el ID de carpeta en la URL de Google Drive

### ❌ Error: "Permission denied"
**Solución**: Asegúrate de que tu cuenta tenga acceso a la carpeta

### ❌ Sync muy lenta
**Solución**: Normal en primera ejecución. Posteriores son incrementales.

### ❌ Error: "No changes to commit"
**Solución**: Normal si no hay archivos nuevos. Verifica que los archivos se descarguen.

---

## 🆚 Comparación: Gratuito vs Google Cloud

| Característica | Método Gratuito | Google Cloud |
|----------------|-----------------|--------------|
| **Costo** | 🆓 $0 | 💰 $0.50+/mes |
| **Configuración** | ✅ Simple | 🔧 Compleja |
| **Límites** | ✅ Sin límites de facturación | ❌ Límites de API |
| **Mantenimiento** | ✅ Mínimo | 🔧 Requiere gestión |
| **Funcionalidad** | ✅ Completa | ✅ Completa |

---

## 🔐 Seguridad

### ✅ Buenas Prácticas
- 🔒 Tokens almacenados como GitHub Secrets
- 🔒 Credenciales eliminadas después de cada ejecución
- 🔒 Acceso solo de lectura a Google Drive
- 🔒 Sin exposición de datos sensibles

### ⚠️ Consideraciones
- 🔐 **Nunca** commits archivos de credenciales
- 🔐 Revisa regularmente los archivos sincronizados
- 🔐 Usa `.gitignore` para archivos sensibles
- 🔐 Considera permisos de carpeta en Google Drive

---

## 📈 Optimizaciones

### 🚀 Rendimiento
- **Sincronización incremental**: Solo archivos modificados
- **Checksums MD5**: Detección precisa de cambios
- **Estado persistente**: Evita descargas innecesarias
- **Paralelización**: GitHub Actions optimizado

### 📊 Monitoreo
- **Logs detallados**: En cada ejecución
- **Resúmenes automáticos**: Con estadísticas
- **Notificaciones**: Por email si configuras GitHub

---

## 🎉 ¡Listo!

Una vez configurado, tu repositorio se sincronizará automáticamente con Google Drive cada 30 minutos.

### 🔗 Enlaces Útiles
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Drive API Reference](https://developers.google.com/drive/api/v3/reference)
- [OAuth2 Flow Documentation](https://developers.google.com/identity/protocols/oauth2)

---

**✨ ¡Disfruta de tu sincronización GRATUITA con Google Drive!**

*Método probado y optimizado - Sin costos ocultos ni sorpresas*