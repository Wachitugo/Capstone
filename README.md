# 🔄 Google Drive GitHub Sync (FREE)

Sincronización automática **100% GRATUITA** entre Google Drive y GitHub usando GitHub Actions.

## ✨ Características

- ✅ **Completamente gratuito** - Sin Google Cloud Console
- ✅ **Sincronización inteligente** - Solo archivos nuevos/modificados
- ✅ **Automático** - Cada 30 minutos
- ✅ **Sin configuración compleja** - Solo OAuth2

## 🚀 Configuración Rápida

### 1. Crear credenciales OAuth2 (5 minutos)

1. Ve a https://console.developers.google.com/
2. Crea un proyecto nuevo
3. Habilita **Google Drive API**
4. Crea **OAuth client ID** (Desktop application)
5. Descarga el archivo JSON

### 2. Configurar GitHub Secrets

Agrega estos 3 secrets en **Settings > Secrets and variables > Actions**:

- `GOOGLE_OAUTH_CREDENTIALS` - Contenido del archivo JSON
- `GOOGLE_REFRESH_TOKEN` - Tu refresh token
- `GOOGLE_DRIVE_FOLDER_ID` - ID de tu carpeta de Drive

Ver `GITHUB_SECRETS_CONFIG.md` para detalles.

### 3. ¡Listo!

GitHub Actions sincronizará automáticamente los archivos de tu carpeta de Google Drive cada 30 minutos.

## 📁 Estructura

```
├── .github/workflows/
│   └── google-drive-sync.yml    # GitHub Action
├── google-drive-sync/           # Archivos sincronizados (se crea automáticamente)
├── scripts/
│   ├── sync_google_drive_free.py # Script de sincronización
│   └── requirements-free.txt     # Dependencias
└── GITHUB_SECRETS_CONFIG.md     # Guía de configuración
```

## 🔧 Funcionamiento

- **Frecuencia**: Cada 30 minutos automáticamente
- **Detección**: MD5 checksums y fechas de modificación  
- **Commits**: Automáticos cuando hay cambios
- **Logs**: Detallados en GitHub Actions

## 💡 Obtener FOLDER_ID

1. Abre tu carpeta en Google Drive
2. Copia el ID desde la URL:
   ```
   https://drive.google.com/drive/folders/[ESTE_ES_EL_ID]
   ```

---

**🎉 Sincronización automática lista en minutos!**