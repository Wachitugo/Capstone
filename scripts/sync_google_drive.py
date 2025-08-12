#!/usr/bin/env python3
"""
Script para sincronizar archivos de Google Drive con el repositorio de GitHub
"""

import os
import io
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


class GoogleDriveSync:
    def __init__(self, credentials_path: str, folder_id: str):
        """
        Inicializar el sincronizador de Google Drive
        
        Args:
            credentials_path: Ruta al archivo JSON de credenciales
            folder_id: ID de la carpeta de Google Drive a sincronizar
        """
        self.credentials_path = credentials_path
        self.folder_id = folder_id
        self.service = self._authenticate()
        self.sync_folder = Path("google-drive-sync")
        self.sync_folder.mkdir(exist_ok=True)
        
        # Archivo para rastrear el estado de sincronización
        self.sync_state_file = Path("scripts/sync_state.json")
        self.sync_state = self._load_sync_state()
        
    def _authenticate(self):
        """Autenticar con Google Drive API"""
        scopes = ['https://www.googleapis.com/auth/drive.readonly']
        
        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=scopes
            )
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            print(f"❌ Error de autenticación: {e}")
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
                fields="files(id, name, mimeType, modifiedTime, md5Checksum, size)"
            ).execute()
            
            items = results.get('files', [])
            
            for item in items:
                item_path = folder_path / item['name']
                
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    # Es una carpeta, listar recursivamente
                    print(f"📁 Explorando carpeta: {item['name']}")
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
            request = self.service.files().get_media(fileId=file_info['id'])
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                
            # Guardar archivo
            with open(file_info['path'], 'wb') as f:
                f.write(file_content.getvalue())
                
            print(f"✅ Descargado: {file_info['name']} ({file_info['size']} bytes)")
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
            return True
            
        # Si no tenemos información previa del archivo, descargarlo
        if file_id not in self.sync_state['files']:
            return True
            
        # Comparar checksums si están disponibles
        if file_info['md5_checksum']:
            stored_checksum = self.sync_state['files'][file_id].get('md5_checksum', '')
            if stored_checksum != file_info['md5_checksum']:
                return True
                
        # Comparar fechas de modificación
        stored_modified = self.sync_state['files'][file_id].get('modified_time', '')
        if stored_modified != file_info['modified_time']:
            return True
            
        return False
    
    def sync(self) -> Dict:
        """
        Sincronizar archivos de Google Drive
        
        Returns:
            Estadísticas de la sincronización
        """
        print(f"🔄 Iniciando sincronización desde Google Drive...")
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
        
        # Procesar cada archivo
        for file_info in drive_files:
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
                print(f"⏭️  Sin cambios: {file_info['name']}")
        
        # Guardar estado de sincronización
        self._save_sync_state()
        
        # Crear archivo de resumen
        self._create_sync_summary(stats)
        
        print(f"\n📊 Sincronización completada:")
        print(f"   📁 Total de archivos: {stats['total_files']}")
        print(f"   ⬇️  Descargados: {stats['downloaded']}")
        print(f"   ⏭️  Sin cambios: {stats['skipped']}")
        print(f"   ❌ Errores: {stats['errors']}")
        
        return stats
    
    def _create_sync_summary(self, stats: Dict):
        """Crear archivo de resumen de la sincronización"""
        summary_file = self.sync_folder / "SYNC_SUMMARY.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# 📋 Resumen de Sincronización\n\n")
            f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
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
            
            f.write(f"---\n")
            f.write(f"*Generado automáticamente por GitHub Actions*\n")


def main():
    """Función principal"""
    print("🚀 Iniciando sincronización con Google Drive...")
    
    # Obtener variables de entorno
    credentials_path = "credentials.json"
    folder_id = os.environ.get('GOOGLE_DRIVE_FOLDER_ID')
    
    if not folder_id:
        print("❌ Error: GOOGLE_DRIVE_FOLDER_ID no está configurado")
        return 1
        
    if not os.path.exists(credentials_path):
        print("❌ Error: Archivo de credenciales no encontrado")
        return 1
    
    try:
        # Inicializar sincronizador
        sync = GoogleDriveSync(credentials_path, folder_id)
        
        # Ejecutar sincronización
        stats = sync.sync()
        
        # Si hay cambios, salir con código 0 para que GitHub Actions haga commit
        if stats['downloaded'] > 0:
            print("✅ Sincronización completada con cambios")
            return 0
        else:
            print("✅ Sincronización completada sin cambios")
            return 0
            
    except Exception as e:
        print(f"❌ Error durante la sincronización: {e}")
        return 1


if __name__ == "__main__":
    exit(main())