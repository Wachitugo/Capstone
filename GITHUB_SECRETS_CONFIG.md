# GitHub Secrets Configuration

Configura estos 3 secrets en tu repositorio de GitHub:
**Settings > Secrets and variables > Actions > New repository secret**

## 1. GOOGLE_OAUTH_CREDENTIALS
**Nombre:** `GOOGLE_OAUTH_CREDENTIALS`  
**Valor:** Contenido completo del archivo `oauth_credentials.json` que descargaste de Google Developers Console

Formato esperado:
```json
{
  "installed": {
    "client_id": "TU_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "tu-proyecto-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "TU_CLIENT_SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
```

## 2. GOOGLE_REFRESH_TOKEN
**Nombre:** `GOOGLE_REFRESH_TOKEN`  
**Valor:** Contenido del archivo `refresh_token.txt` generado localmente

Formato: Una cadena larga que comienza con `1//`

## 3. GOOGLE_DRIVE_FOLDER_ID
**Nombre:** `GOOGLE_DRIVE_FOLDER_ID`  
**Valor:** ID de tu carpeta de Google Drive

### Como obtener el FOLDER_ID:
1. Abre Google Drive en tu navegador
2. Navega a la carpeta que quieres sincronizar
3. Copia el ID desde la URL:
   ```
   https://drive.google.com/drive/folders/[ESTE_ES_EL_ID]
   ```

## ⚠️ Importante:
- Los archivos `oauth_credentials.json` y `refresh_token.txt` NO deben subirse a GitHub
- Solo usa sus contenidos como GitHub Secrets
- Mantén estos archivos seguros en tu máquina local

## Siguiente paso:
Una vez configurados los 3 secrets, tu GitHub Action se ejecutará automáticamente cada 30 minutos y sincronizará los archivos de tu carpeta de Google Drive.