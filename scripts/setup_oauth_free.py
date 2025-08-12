#!/usr/bin/env python3
"""
Script para configurar OAuth2 de Google Drive - MÉTODO 100% GRATUITO
Sin necesidad de Google Cloud Console ni cargos
"""

import json
import os
import webbrowser
from pathlib import Path

from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request


def setup_free_oauth():
    """
    Configurar OAuth2 gratuito para Google Drive
    """
    print("🆓 CONFIGURACIÓN OAUTH2 GRATUITA")
    print("=" * 50)
    print("Primero necesitas crear tus credenciales OAuth2 gratuitas\n")
    
    print("📋 PASOS PARA CREAR CREDENCIALES GRATUITAS:")
    print("1. Ve a https://console.developers.google.com/")
    print("2. Crea un nuevo proyecto (o usa uno existente)")
    print("3. Habilita la Google Drive API")
    print("4. Ve a 'Credentials' > 'Create Credentials' > 'OAuth client ID'")
    print("5. Selecciona 'Desktop application'")
    print("6. Descarga el archivo JSON\n")
    
    # Solicitar archivo de credenciales
    while True:
        creds_path = input("📁 Arrastra aquí tu archivo JSON de credenciales (o escribe la ruta): ").strip().strip('"')
        
        if not creds_path:
            print("❌ Debes proporcionar la ruta del archivo")
            continue
            
        if not os.path.exists(creds_path):
            print(f"❌ Archivo no encontrado: {creds_path}")
            continue
            
        try:
            with open(creds_path, 'r') as f:
                oauth_config = json.load(f)
            print(f"✅ Credenciales cargadas correctamente")
            break
        except Exception as e:
            print(f"❌ Error leyendo archivo: {e}")
            continue
    
    print("📄 Creando archivo de credenciales OAuth2...")
    credentials_file = Path("oauth_credentials.json")
    with open(credentials_file, 'w') as f:
        json.dump(oauth_config, f, indent=2)
    
    print(f"✅ Archivo creado: {credentials_file}")
    
    # Configurar el flujo OAuth2
    scopes = ['https://www.googleapis.com/auth/drive.readonly']
    flow = Flow.from_client_secrets_file(
        str(credentials_file),
        scopes=scopes
    )
    flow.redirect_uri = 'http://localhost:8080/'
    
    # Generar URL de autorización
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'  # Forzar el consent para obtener refresh token
    )
    
    print("\n🔗 PASOS PARA AUTORIZACIÓN:")
    print("1. Se abrirá tu navegador automáticamente")
    print("2. Inicia sesión en tu cuenta de Google")
    print("3. Autoriza el acceso a Google Drive")
    print("4. Copia la URL de redirección completa")
    print("5. Pégala aquí cuando se te solicite")
    print()
    
    # Abrir navegador
    print("🌐 Abriendo navegador...")
    webbrowser.open(auth_url)
    
    print(f"\n📋 URL de autorización:")
    print(f"{auth_url}")
    print()
    
    # Solicitar código de autorización
    redirect_url = input("📥 Pega aquí la URL completa de redirección: ").strip()
    
    try:
        # Extraer el código de la URL
        flow.fetch_token(authorization_response=redirect_url)
        
        # Guardar refresh token
        credentials = flow.credentials
        refresh_token_file = Path("refresh_token.txt")
        with open(refresh_token_file, 'w') as f:
            f.write(credentials.refresh_token)
        
        print(f"\n✅ ¡Configuración completada exitosamente!")
        print(f"📄 Credenciales OAuth2: {credentials_file}")
        print(f"🔑 Refresh Token: {refresh_token_file}")
        
        # Crear archivo de configuración para GitHub Secrets
        create_github_secrets_template(oauth_config, credentials.refresh_token)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la autorización: {e}")
        print("💡 Asegúrate de copiar la URL completa de redirección")
        return False


def create_github_secrets_template(oauth_config, refresh_token):
    """Crear plantilla para GitHub Secrets"""
    template_file = Path("github_secrets_template.txt")
    
    with open(template_file, 'w') as f:
        f.write("# GITHUB SECRETS PARA MÉTODO GRATUITO\n")
        f.write("# Copia estos valores en tu repositorio\n")
        f.write("# Settings > Secrets and variables > Actions\n\n")
        
        f.write("# 1. GOOGLE_OAUTH_CREDENTIALS\n")
        f.write(json.dumps(oauth_config, indent=2))
        f.write("\n\n")
        
        f.write("# 2. GOOGLE_REFRESH_TOKEN\n")
        f.write(refresh_token)
        f.write("\n\n")
        
        f.write("# 3. GOOGLE_DRIVE_FOLDER_ID\n")
        f.write("# Obten el ID de tu carpeta desde la URL:\n")
        f.write("# https://drive.google.com/drive/folders/[ESTE_ES_EL_ID]\n")
        f.write("TU_FOLDER_ID_AQUI\n")
    
    print(f"📋 Plantilla creada: {template_file}")


def test_oauth_connection():
    """Probar la conexión OAuth2"""
    print("\n🔍 Probando conexión...")
    
    try:
        from scripts.sync_google_drive_free import GoogleDriveSyncFree
        
        # Intentar crear una instancia de prueba
        folder_id = "test"  # ID temporal para prueba
        sync = GoogleDriveSyncFree("oauth_credentials.json", "refresh_token.txt", folder_id)
        
        print("✅ Conexión OAuth2 exitosa!")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False


def main():
    """Función principal"""
    print("🆓 SETUP GRATUITO DE GOOGLE DRIVE SYNC")
    print("====================================")
    print("Este script configura OAuth2 sin costos de Google Cloud\n")
    
    # Verificar si ya existe configuración
    if Path("oauth_credentials.json").exists() and Path("refresh_token.txt").exists():
        print("⚠️  Ya existe una configuración OAuth2")
        choice = input("¿Quieres reconfigurar? (y/N): ").strip().lower()
        if choice != 'y':
            print("✅ Usando configuración existente")
            return test_oauth_connection()
    
    # Configurar OAuth2
    if setup_free_oauth():
        print("\n🎉 ¡Configuración completada!")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Revisa el archivo 'github_secrets_template.txt'")
        print("2. Copia los valores a tus GitHub Secrets")
        print("3. Ejecuta el workflow de GitHub Actions")
        print("4. ¡Disfruta de la sincronización gratuita!")
        
        # Probar conexión
        test_oauth_connection()
        
        return True
    else:
        print("\n❌ La configuración falló")
        print("💡 Intenta ejecutar el script nuevamente")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)