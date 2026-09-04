from .base_storage import BaseStorage
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from typing import List, Optional

class GoogleDriveStorage(BaseStorage):
    """Conector para Google Drive"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.service = None
        self.credentials_path = config.get('credentials_path', 'credentials.json')
        self.token_path = config.get('token_path', 'token.pickle')
    
    def connect(self) -> bool:
        """Establecer conexión con Google Drive"""
        try:
            creds = None
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.service = build('drive', 'v3', credentials=creds)
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Error conectando a Google Drive: {e}")
            return False
    
    def upload_file(self, local_path: str, remote_path: str) -> str:
        """Subir archivo a Google Drive"""
        if not self.is_connected:
            self.connect()
        
        try:
            file_metadata = {'name': os.path.basename(remote_path)}
            media = MediaFileUpload(local_path, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
        except Exception as e:
            print(f"Error subiendo archivo: {e}")
            return ""
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Descargar archivo de Google Drive"""
        if not self.is_connected:
            self.connect()
        
        try:
            request = self.service.files().get_media(fileId=remote_path)
            with open(local_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
            return True
        except Exception as e:
            print(f"Error descargando archivo: {e}")
            return False
    
    def delete_file(self, remote_path: str) -> bool:
        """Eliminar archivo de Google Drive"""
        if not self.is_connected:
            self.connect()
        
        try:
            self.service.files().delete(fileId=remote_path).execute()
            return True
        except Exception as e:
            print(f"Error eliminando archivo: {e}")
            return False
    
    def list_files(self, folder_path: str = "") -> List[str]:
        """Listar archivos en Google Drive"""
        if not self.is_connected:
            self.connect()
        
        try:
            results = self.service.files().list(
                pageSize=10, fields="nextPageToken, files(id, name)"
            ).execute()
            items = results.get('files', [])
            return [item['id'] for item in items]
        except Exception as e:
            print(f"Error listando archivos: {e}")
            return []
    
    def search_files(self, query: str) -> List[str]:
        """Buscar archivos en Google Drive"""
        if not self.is_connected:
            self.connect()
        
        try:
            results = self.service.files().list(
                q=f"name contains '{query}'",
                pageSize=10, fields="nextPageToken, files(id, name)"
            ).execute()
            items = results.get('files', [])
            return [item['id'] for item in items]
        except Exception as e:
            print(f"Error buscando archivos: {e}")
            return []