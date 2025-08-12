# 🔐 Guía para Crear Credenciales OAuth2 GRATUITAS

Esta guía te ayuda a crear tus propias credenciales OAuth2 para Google Drive **sin costo alguno**.

## 🚀 Paso a Paso (5 minutos)

### 1️⃣ Ir a Google Developers Console

**🔗 Enlace:** https://console.developers.google.com/

### 2️⃣ Crear/Seleccionar Proyecto

1. **Si no tienes proyecto:**
   - Haz clic en **"Create Project"**
   - Nombre: `github-drive-sync` (o cualquier nombre)
   - Haz clic en **"Create"**

2. **Si ya tienes proyecto:**
   - Selecciónalo del dropdown superior

### 3️⃣ Habilitar Google Drive API

1. En el menú lateral, ve a **"APIs & Services"** > **"Library"**
2. Busca **"Google Drive API"**
3. Haz clic en **"Google Drive API"**
4. Presiona **"Enable"**

### 4️⃣ Configurar Pantalla de Consentimiento

1. Ve a **"APIs & Services"** > **"OAuth consent screen"**
2. Selecciona **"External"** (para uso personal)
3. Completa la información básica:
   - **App name**: `GitHub Drive Sync`
   - **User support email**: Tu email
   - **Developer contact**: Tu email
4. Haz clic en **"Save and Continue"**
5. En **"Scopes"**: Haz clic en **"Save and Continue"** (sin agregar scopes)
6. En **"Test users"**: Agrega tu propio email
7. Haz clic en **"Save and Continue"**

### 5️⃣ Crear Credenciales OAuth2

1. Ve a **"APIs & Services"** > **"Credentials"**
2. Haz clic en **"+ Create Credentials"**
3. Selecciona **"OAuth client ID"**
4. **Application type**: Selecciona **"Desktop application"**
5. **Name**: `GitHub Drive Sync Client`
6. Haz clic en **"Create"**

### 6️⃣ Descargar Credenciales

1. **Aparecerá una ventana** con el client ID y secret
2. Haz clic en **"Download JSON"**
3. **Guarda el archivo** (se llama algo como `client_secret_xxxxx.json`)
4. **¡No compartas este archivo!** - Contiene credenciales privadas

## ✅ Verificar Descarga

El archivo JSON debe tener esta estructura:
```json
{
  "installed": {
    "client_id": "tu-client-id.apps.googleusercontent.com",
    "project_id": "tu-proyecto-xxxxx",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "tu-client-secret",
    "redirect_uris": ["http://localhost"]
  }
}
```

## 🏃‍♂️ Siguiente Paso

Una vez que tengas el archivo JSON:

```bash
python scripts/setup_oauth_free.py
```

El script te pedirá la ruta del archivo JSON y configurará todo automáticamente.

## 🔒 Consideraciones de Seguridad

### ✅ Buenas Prácticas
- 🔐 **NUNCA** subas el archivo JSON a GitHub
- 🔐 Guarda el archivo en un lugar seguro
- 🔐 Solo comparte el contenido como GitHub Secret
- 🔐 El proyecto puede permanecer en "Testing" (sin publicar)

### ⚠️ Límites Gratuitos
- 📊 **100 requests/100 segundos** (más que suficiente para sincronización)
- 📊 **Sin límites de almacenamiento** en tu Google Drive
- 📊 **Sin costos ocultos** ni cargos por API

## 🆚 ¿Por qué este método es gratuito?

| Concepto | Google Cloud Console | Google Developers Console |
|----------|----------------------|----------------------------|
| **Costo** | 💰 Puede generar cargos | 🆓 Completamente gratis |
| **Límites** | ⚡ Más restrictivos | ⚡ Suficientes para uso personal |
| **Configuración** | 🔧 Compleja | ✅ Simple |
| **Mantenimiento** | 🔧 Requiere monitoreo | ✅ Sin mantenimiento |

## 🔍 Solución de Problemas

### ❌ Error: "This app isn't verified"
**Solución:** Es normal para apps en desarrollo. Haz clic en "Advanced" > "Go to app (unsafe)"

### ❌ Error: "Access blocked"
**Solución:** Asegúrate de haber agregado tu email en "Test users"

### ❌ Error: "Invalid client"
**Solución:** Verifica que hayas habilitado la Google Drive API

### ❌ No aparece botón de descarga
**Solución:** Ve a "Credentials", busca tu OAuth client y haz clic en el icono de descarga

## 📞 ¿Necesitas ayuda?

Si tienes problemas:

1. 📋 Verifica que hayas seguido todos los pasos
2. 🔍 Asegúrate de haber habilitado la Google Drive API
3. ✅ Confirma que agregaste tu email en "Test users"
4. 📖 Revisa la consola de desarrolladores para mensajes de error

---

**🎉 Una vez que tengas el archivo JSON, ¡el resto es automático!**

*Método probado - Sin costos ni sorpresas*