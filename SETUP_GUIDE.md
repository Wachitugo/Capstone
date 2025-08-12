# 🚀 Guía de Configuración - GitHub Actions + Google Drive Sync

Esta guía te ayudará a configurar la sincronización automática entre Google Drive y tu repositorio de GitHub.

## 📋 Requisitos Previos

- ✅ Cuenta de Google con acceso a Google Drive
- ✅ Cuenta de GitHub con permisos de administrador en el repositorio
- ✅ Carpeta específica en Google Drive que quieres sincronizar

## 🔧 Paso 1: Configurar Google Drive API

### 1.1 Crear Proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. En el menú de navegación, ve a **"APIs & Services" > "Library"**
4. Busca y habilita **"Google Drive API"**

### 1.2 Crear Cuenta de Servicio

1. Ve a **"APIs & Services" > "Credentials"**
2. Haz clic en **"Create Credentials" > "Service Account"**
3. Completa la información:
   - **Name**: `github-drive-sync`
   - **Description**: `Servicio para sincronizar Google Drive con GitHub`
4. Haz clic en **"Create and Continue"**
5. En "Grant this service account access to project":
   - **Role**: `Editor` (o crea un rol personalizado con permisos mínimos)
6. Haz clic en **"Done"**

### 1.3 Generar Clave de Servicio

1. En la lista de cuentas de servicio, haz clic en la que acabas de crear
2. Ve a la pestaña **"Keys"**
3. Haz clic en **"Add Key" > "Create new key"**
4. Selecciona **JSON** y haz clic en **"Create"**
5. Se descargará un archivo JSON - **¡Guárdalo de forma segura!**

### 1.4 Compartir Carpeta con la Cuenta de Servicio

1. Abre Google Drive y navega a la carpeta que quieres sincronizar
2. Haz clic derecho en la carpeta > **"Share"**
3. Comparte con la dirección email de la cuenta de servicio (está en el archivo JSON como `client_email`)
4. Otorga permisos de **"Viewer"** o **"Editor"** según necesites
5. Copia el **ID de la carpeta** desde la URL: 
   ```
   https://drive.google.com/drive/folders/[ESTE_ES_EL_ID]
   ```

## 🔐 Paso 2: Configurar GitHub Secrets

1. Ve a tu repositorio en GitHub
2. Navega a **Settings > Secrets and variables > Actions**
3. Haz clic en **"New repository secret"**
4. Agrega los siguientes secrets:

### Secret 1: GOOGLE_DRIVE_CREDENTIALS
- **Name**: `GOOGLE_DRIVE_CREDENTIALS`
- **Value**: Todo el contenido del archivo JSON descargado (incluyendo las llaves `{}`)

### Secret 2: GOOGLE_DRIVE_FOLDER_ID
- **Name**: `GOOGLE_DRIVE_FOLDER_ID`
- **Value**: El ID de la carpeta copiado en el paso 1.4

## ✅ Paso 3: Verificar la Configuración

### 3.1 Ejecutar Manualmente

1. Ve a **Actions** en tu repositorio
2. Selecciona el workflow **"Google Drive Sync"**
3. Haz clic en **"Run workflow"**
4. Observa los logs para verificar que funciona correctamente

### 3.2 Verificar Archivos Descargados

Después de la primera ejecución exitosa, deberías ver:
- 📁 Carpeta `google-drive-sync/` con tus archivos
- 📄 Archivo `google-drive-sync/SYNC_SUMMARY.md` con estadísticas
- 📄 Archivo `scripts/sync_state.json` con el estado de sincronización

## ⚡ Funcionalidades

### 🕰️ Sincronización Automática
- **Frecuencia**: Cada 30 minutos
- **Triggers**: Push a branch main, ejecución manual
- **Detección**: Solo descarga archivos nuevos o modificados

### 📊 Monitoreo
- Logs detallados en GitHub Actions
- Archivo de resumen generado en cada sync
- Estado persistente para optimizar sincronizaciones

### 🔔 Notificaciones Webhook (Opcional)

Para recibir notificaciones instantáneas cuando cambien archivos en Google Drive:

1. **Configura un endpoint público** (ej: ngrok, webhook.site)
2. **Verifica tu dominio** en Google Search Console
3. **Ejecuta el script de configuración**:
   ```bash
   python scripts/setup_webhook.py setup
   ```

## 🛠️ Comandos Útiles

### Ejecutar Sincronización Local (Testing)
```bash
# Instalar dependencias
pip install -r scripts/requirements.txt

# Configurar variables de entorno
export GOOGLE_DRIVE_FOLDER_ID="tu_folder_id"

# Colocar archivo de credenciales
cp ruta/a/tu/archivo.json credentials.json

# Ejecutar sincronización
python scripts/sync_google_drive.py
```

### Cancelar Webhook
```bash
python scripts/setup_webhook.py cancel
```

### Ver Estado de Sincronización
```bash
cat scripts/sync_state.json
```

## 📁 Estructura de Archivos Generada

```
tu-repositorio/
├── .github/
│   └── workflows/
│       ├── google-drive-sync.yml       # Workflow principal
│       └── google-drive-webhook.yml    # Webhook trigger
├── google-drive-sync/                  # Archivos sincronizados
│   ├── archivo1.pdf
│   ├── archivo2.docx
│   ├── carpeta1/
│   │   └── archivo3.txt
│   └── SYNC_SUMMARY.md                 # Resumen de última sync
├── scripts/
│   ├── sync_google_drive.py            # Script principal
│   ├── setup_webhook.py                # Configurador de webhook
│   ├── requirements.txt                # Dependencias Python
│   └── sync_state.json                 # Estado de sincronización
└── SETUP_GUIDE.md                      # Esta guía
```

## 🔍 Resolución de Problemas

### Error: "File not accessible"
- ✅ Verifica que la carpeta esté compartida con la cuenta de servicio
- ✅ Confirma que el ID de carpeta es correcto

### Error: "Invalid credentials"
- ✅ Verifica que el JSON en GitHub Secrets esté completo
- ✅ Asegúrate de que la Google Drive API esté habilitada

### Error: "No changes to commit"
- ✅ Normal si no hay archivos nuevos/modificados
- ✅ Verifica que los archivos se descarguen en `google-drive-sync/`

### Sync muy lenta
- ✅ Normal en la primera ejecución (descarga todo)
- ✅ Ejecuciones posteriores son incrementales

## 🔒 Consideraciones de Seguridad

- 🔐 **Nunca** commits el archivo JSON de credenciales
- 🔐 Usa permisos mínimos en la cuenta de servicio
- 🔐 Revisa regularmente los archivos sincronizados
- 🔐 Considera usar `.gitignore` para archivos sensibles

## 📞 Soporte

Si tienes problemas:

1. 📋 Revisa los logs en GitHub Actions
2. 🔍 Verifica que todos los secrets estén configurados
3. ✅ Confirma que la carpeta esté compartida correctamente
4. 📖 Lee los mensajes de error en los logs

---

✅ **¡Tu sincronización automática está lista!**

Los archivos de tu carpeta de Google Drive se sincronizarán automáticamente cada 30 minutos y cuando hagas push al repositorio.