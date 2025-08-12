#!/usr/bin/env python3
"""
Script GRATUITO para sincronizar archivos de Google Drive con GitHub
Usa OAuth2 sin necesidad de Google Cloud Console (método 100% gratuito)
"""

import os
import io
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Permitir HTTP para desarrollo local (solo para testing)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


class GoogleDriveSyncFree:
    def __init__(self, oauth_credentials_path: str, refresh_token_path: str, folder_id: str):
        """
        Inicializar el sincronizador GRATUITO de Google Drive
        
        Args:
            oauth_credentials_path: Ruta al archivo JSON de OAuth2
            refresh_token_path: Ruta al archivo con el refresh token
            folder_id: ID de la carpeta de Google Drive a sincronizar
        """
        self.oauth_credentials_path = oauth_credentials_path
        self.refresh_token_path = refresh_token_path
        self.folder_id = folder_id
        self.service = self._authenticate()
        self.sync_folder = Path("Archivos")
        self.sync_folder.mkdir(exist_ok=True)
        
        # Archivo para rastrear el estado de sincronización
        self.sync_state_file = Path("scripts/sync_state_free.json")
        self.sync_state = self._load_sync_state()
        
    def _authenticate(self):
        """Autenticar usando OAuth2 (método gratuito)"""
        try:
            # Cargar credenciales OAuth2
            with open(self.oauth_credentials_path, 'r') as f:
                oauth_data = json.load(f)
            
            # Cargar refresh token
            with open(self.refresh_token_path, 'r') as f:
                refresh_token = f.read().strip()
            
            # Crear credenciales
            credentials = Credentials(
                token=None,  # Access token será generado automáticamente
                refresh_token=refresh_token,
                token_uri=oauth_data['installed']['token_uri'],
                client_id=oauth_data['installed']['client_id'],
                client_secret=oauth_data['installed']['client_secret'],
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            
            # Refrescar el token si es necesario
            if not credentials.valid:
                print("🔄 Refrescando token de acceso...")
                credentials.refresh(Request())
                print("✅ Token refrescado exitosamente")
            
            # Crear servicio de Google Drive
            service = build('drive', 'v3', credentials=credentials)
            
            # Verificar conectividad
            print("🔗 Verificando conexión con Google Drive...")
            service.about().get(fields="user").execute()
            print("✅ Conectado exitosamente a Google Drive")
            
            return service
            
        except Exception as e:
            print(f"❌ Error de autenticación: {e}")
            print("💡 Verifica tus credenciales OAuth2 y refresh token")
            raise
            
    def _load_sync_state(self) -> Dict:
        """Cargar el estado de sincronización anterior"""
        if self.sync_state_file.exists():
            try:
                with open(self.sync_state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error cargando estado de sync: {e}")
        
        return {"files": {}, "last_sync": None}
    
    def _save_sync_state(self):
        """Guardar el estado de sincronización"""
        self.sync_state["last_sync"] = datetime.now().isoformat()
        
        # Crear directorio si no existe
        self.sync_state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.sync_state_file, 'w', encoding='utf-8') as f:
            json.dump(self.sync_state, f, indent=2, ensure_ascii=False)
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Calcular hash MD5 de un archivo"""
        if not file_path.exists():
            return ""
        
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    def _list_drive_files(self, folder_id: str, folder_path: Path = None) -> List[Dict]:
        """
        Listar archivos en Google Drive recursivamente
        
        Args:
            folder_id: ID de la carpeta de Google Drive
            folder_path: Ruta local correspondiente
            
        Returns:
            Lista de archivos encontrados
        """
        if folder_path is None:
            folder_path = self.sync_folder
            
        files = []
        
        try:
            # Obtener archivos y carpetas de la carpeta actual
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="files(id, name, mimeType, modifiedTime, md5Checksum, size)",
                pageSize=1000  # Máximo por página
            ).execute()
            
            items = results.get('files', [])
            print(f"📁 Encontrados {len(items)} elementos en carpeta")
            
            for item in items:
                item_path = folder_path / item['name']
                
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    # Es una carpeta, listar recursivamente
                    print(f"📂 Explorando subcarpeta: {item['name']}")
                    subfolder_files = self._list_drive_files(item['id'], item_path)
                    files.extend(subfolder_files)
                else:
                    # Es un archivo
                    files.append({
                        'id': item['id'],
                        'name': item['name'],
                        'path': item_path,
                        'modified_time': item['modifiedTime'],
                        'md5_checksum': item.get('md5Checksum', ''),
                        'size': int(item.get('size', 0)),
                        'mime_type': item['mimeType']
                    })
                    
        except Exception as e:
            print(f"❌ Error listando archivos: {e}")
            
        return files
    
    def _download_file(self, file_info: Dict) -> bool:
        """
        Descargar un archivo de Google Drive
        
        Args:
            file_info: Información del archivo
            
        Returns:
            True si se descargó exitosamente
        """
        try:
            # Crear directorio padre si no existe
            file_info['path'].parent.mkdir(parents=True, exist_ok=True)
            
            # Skip Google Workspace files (Docs, Sheets, Slides, etc.)
            if file_info['mime_type'].startswith('application/vnd.google-apps.'):
                print(f"⏭️  Saltando archivo de Google Workspace: {file_info['name']}")
                return False
            
            # Descargar archivo
            print(f"⬇️  Descargando: {file_info['name']} ({file_info['size']} bytes)")
            
            request = self.service.files().get_media(fileId=file_info['id'])
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"📊 Progreso: {progress}%", end='\r')
            print()  # Nueva línea después del progreso
                
            # Guardar archivo
            with open(file_info['path'], 'wb') as f:
                f.write(file_content.getvalue())
                
            print(f"✅ Descargado exitosamente: {file_info['name']}")
            return True
            
        except Exception as e:
            print(f"❌ Error descargando {file_info['name']}: {e}")
            return False
    
    def _should_download_file(self, file_info: Dict) -> bool:
        """
        Determinar si un archivo debe ser descargado
        
        Args:
            file_info: Información del archivo
            
        Returns:
            True si el archivo debe descargarse
        """
        file_id = file_info['id']
        local_path = file_info['path']
        
        # Si el archivo no existe localmente, descargarlo
        if not local_path.exists():
            print(f"📄 Archivo nuevo: {file_info['name']}")
            return True
            
        # Si no tenemos información previa del archivo, descargarlo
        if file_id not in self.sync_state['files']:
            print(f"🆕 Archivo sin estado previo: {file_info['name']}")
            return True
            
        # Comparar checksums si están disponibles
        if file_info['md5_checksum']:
            stored_checksum = self.sync_state['files'][file_id].get('md5_checksum', '')
            if stored_checksum != file_info['md5_checksum']:
                print(f"🔄 Archivo modificado (checksum): {file_info['name']}")
                return True
                
        # Comparar fechas de modificación
        stored_modified = self.sync_state['files'][file_id].get('modified_time', '')
        if stored_modified != file_info['modified_time']:
            print(f"🔄 Archivo modificado (fecha): {file_info['name']}")
            return True
            
        return False
    
    def sync(self) -> Dict:
        """
        Sincronizar archivos de Google Drive (método gratuito)
        
        Returns:
            Estadísticas de la sincronización
        """
        print(f"🆓 Iniciando sincronización GRATUITA desde Google Drive...")
        print(f"📁 Carpeta de destino: {self.sync_folder}")
        
        # Obtener lista de archivos en Google Drive
        print(f"📋 Listando archivos en Google Drive...")
        drive_files = self._list_drive_files(self.folder_id)
        
        stats = {
            'total_files': len(drive_files),
            'downloaded': 0,
            'skipped': 0,
            'errors': 0,
            'updated_files': []
        }
        
        print(f"📊 Total de archivos encontrados: {stats['total_files']}")
        
        # Procesar cada archivo
        for i, file_info in enumerate(drive_files, 1):
            print(f"\n[{i}/{stats['total_files']}] Procesando: {file_info['name']}")
            
            if self._should_download_file(file_info):
                if self._download_file(file_info):
                    stats['downloaded'] += 1
                    stats['updated_files'].append(str(file_info['path']))
                    
                    # Actualizar estado de sincronización
                    self.sync_state['files'][file_info['id']] = {
                        'name': file_info['name'],
                        'path': str(file_info['path']),
                        'modified_time': file_info['modified_time'],
                        'md5_checksum': file_info['md5_checksum'],
                        'size': file_info['size']
                    }
                else:
                    stats['errors'] += 1
            else:
                stats['skipped'] += 1
                print(f"✅ Sin cambios: {file_info['name']}")
        
        # Guardar estado de sincronización
        self._save_sync_state()
        
        # Crear archivo de resumen
        self._create_sync_summary(stats)
        
        print(f"\n🎉 Sincronización GRATUITA completada:")
        print(f"   📁 Total de archivos: {stats['total_files']}")
        print(f"   ⬇️  Descargados: {stats['downloaded']}")
        print(f"   ⏭️  Sin cambios: {stats['skipped']}")
        print(f"   ❌ Errores: {stats['errors']}")
        
        return stats
    
    def _create_sync_summary(self, stats: Dict):
        """Crear archivo de resumen de la sincronización"""
        summary_file = self.sync_folder / "SYNC_SUMMARY_FREE.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# 🆓 Resumen de Sincronización GRATUITA\n\n")
            f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Método:** OAuth2 (100% Gratuito)\n\n")
            f.write(f"## 📊 Estadísticas\n\n")
            f.write(f"- **Total de archivos:** {stats['total_files']}\n")
            f.write(f"- **Descargados/Actualizados:** {stats['downloaded']}\n")
            f.write(f"- **Sin cambios:** {stats['skipped']}\n")
            f.write(f"- **Errores:** {stats['errors']}\n\n")
            
            if stats['updated_files']:
                f.write(f"## 📥 Archivos Actualizados\n\n")
                for file_path in stats['updated_files']:
                    f.write(f"- `{file_path}`\n")
                f.write("\n")
            
            f.write(f"## 💡 Ventajas del Método Gratuito\n\n")
            f.write(f"- ✅ **Sin costos** de Google Cloud\n")
            f.write(f"- ✅ **Fácil configuración** OAuth2\n")
            f.write(f"- ✅ **Sin límites de facturación**\n")
            f.write(f"- ✅ **Acceso completo** a Google Drive\n\n")
            
            f.write(f"---\n")
            f.write(f"*Generado automáticamente por GitHub Actions (Método Gratuito)*\n")


def main():
    """Función principal"""
    print("🚀 Iniciando sincronización GRATUITA con Google Drive...")
    
    # Obtener variables de entorno y archivos
    oauth_credentials_path = "oauth_credentials.json"
    refresh_token_path = "refresh_token.txt"
    folder_id = os.environ.get('GOOGLE_DRIVE_FOLDER_ID')
    
    if not folder_id:
        print("❌ Error: GOOGLE_DRIVE_FOLDER_ID no está configurado")
        return 1
        
    if not os.path.exists(oauth_credentials_path):
        print("❌ Error: Archivo de credenciales OAuth2 no encontrado")
        print("💡 Ejecuta el script de configuración primero")
        return 1
        
    if not os.path.exists(refresh_token_path):
        print("❌ Error: Archivo de refresh token no encontrado")
        print("💡 Ejecuta el script de configuración primero")
        return 1
    
    try:
        # Inicializar sincronizador gratuito
        sync = GoogleDriveSyncFree(oauth_credentials_path, refresh_token_path, folder_id)
        
        # Ejecutar sincronización
        stats = sync.sync()
        
        # Resultado
        if stats['downloaded'] > 0:
            print("✅ Sincronización GRATUITA completada con cambios")
            return 0
        else:
            print("✅ Sincronización GRATUITA completada sin cambios")
            return 0
            
    except Exception as e:
        print(f"❌ Error durante la sincronización: {e}")
        return 1


if __name__ == "__main__":
    exit(main())