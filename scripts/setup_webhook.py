#!/usr/bin/env python3
"""
Script para configurar webhook de Google Drive
Este script ayuda a configurar notificaciones automáticas cuando cambien archivos en Google Drive
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def setup_drive_webhook():
    """
    Configurar webhook para notificaciones de Google Drive
    
    NOTA: Para que esto funcione completamente, necesitas:
    1. Un endpoint público (ej: ngrok, webhook.site)
    2. Verificación de dominio en Google Search Console
    3. Configurar el webhook endpoint para hacer llamadas a GitHub API
    """
    
    print("🔔 Configuración de Webhook de Google Drive")
    print("=" * 50)
    
    # Obtener variables de entorno
    credentials_path = "credentials.json"
    folder_id = os.environ.get('GOOGLE_DRIVE_FOLDER_ID')
    webhook_url = os.environ.get('WEBHOOK_URL')  # Tu endpoint público
    
    if not folder_id:
        print("❌ Error: GOOGLE_DRIVE_FOLDER_ID no está configurado")
        return False
        
    if not webhook_url:
        print("❌ Error: WEBHOOK_URL no está configurado")
        print("💡 Necesitas un endpoint público para recibir webhooks")
        return False
        
    if not os.path.exists(credentials_path):
        print("❌ Error: Archivo de credenciales no encontrado")
        return False
    
    try:
        # Autenticación
        scopes = ['https://www.googleapis.com/auth/drive']
        credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
        service = build('drive', 'v3', credentials=credentials)
        
        # Configurar el canal de notificación
        channel_body = {
            'id': f'github-sync-{folder_id}',  # ID único del canal
            'type': 'web_hook',
            'address': webhook_url,  # Tu endpoint público
            'params': {
                'ttl': str(3600 * 24 * 7)  # 7 días de duración
            }
        }
        
        # Crear el watch request
        watch_response = service.files().watch(
            fileId=folder_id,
            body=channel_body
        ).execute()
        
        print("✅ Webhook configurado exitosamente!")
        print(f"📍 Canal ID: {watch_response['id']}")
        print(f"🔗 Resource ID: {watch_response['resourceId']}")
        print(f"⏰ Expira: {watch_response.get('expiration', 'No especificado')}")
        
        # Guardar información del canal para poder cancelarlo después
        channel_info = {
            'channel_id': watch_response['id'],
            'resource_id': watch_response['resourceId'],
            'webhook_url': webhook_url,
            'folder_id': folder_id
        }
        
        with open('scripts/webhook_info.json', 'w') as f:
            json.dump(channel_info, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando webhook: {e}")
        return False

def cancel_webhook():
    """Cancelar webhook existente"""
    try:
        with open('scripts/webhook_info.json', 'r') as f:
            channel_info = json.load(f)
        
        # Autenticación
        credentials_path = "credentials.json"
        scopes = ['https://www.googleapis.com/auth/drive']
        credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
        service = build('drive', 'v3', credentials=credentials)
        
        # Cancelar el canal
        service.channels().stop(body={
            'id': channel_info['channel_id'],
            'resourceId': channel_info['resource_id']
        }).execute()
        
        print("✅ Webhook cancelado exitosamente")
        
        # Eliminar archivo de información
        os.remove('scripts/webhook_info.json')
        
    except Exception as e:
        print(f"❌ Error cancelando webhook: {e}")

def print_webhook_instructions():
    """Imprimir instrucciones para configurar webhook"""
    print("\n📋 INSTRUCCIONES PARA CONFIGURAR WEBHOOK")
    print("=" * 50)
    print("Para que las notificaciones automáticas funcionen, necesitas:")
    print()
    print("1. 🌐 Un endpoint público que pueda recibir webhooks")
    print("   - Usa ngrok: https://ngrok.com/")
    print("   - O webhook.site: https://webhook.site/")
    print("   - O despliega un servidor simple")
    print()
    print("2. ✅ Verificar tu dominio en Google Search Console")
    print("   - Ve a: https://search.google.com/search-console")
    print("   - Agrega y verifica tu dominio/URL")
    print()
    print("3. 🔧 Configurar tu endpoint para llamar GitHub API")
    print("   - Cuando reciba notificación de Google Drive")
    print("   - Debe hacer POST a GitHub repository_dispatch API")
    print("   - URL: https://api.github.com/repos/USUARIO/REPO/dispatches")
    print()
    print("4. 🔑 Configurar variables de entorno:")
    print("   - WEBHOOK_URL=https://tu-endpoint.com/webhook")
    print("   - GITHUB_TOKEN=tu-token-de-github")
    print()
    print("💡 Alternativamente, puedes usar solo el workflow programado (cada 30 min)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "cancel":
        cancel_webhook()
    elif len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_drive_webhook()
    else:
        print_webhook_instructions()