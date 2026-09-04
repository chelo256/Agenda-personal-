from .base_storage import BaseStorage
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
import os
from typing import List

class GCSStorage(BaseStorage):
    """Conector para Google Cloud Storage"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.client = None
        self.bucket_name = config.get('bucket_name', '')
        self.credentials_path = config.get('credentials_path', 'service-account.json')
    
    def connect(self) -> bool:
        """Establecer conexión con Google Cloud Storage"""
        try:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
            self.client = storage.Client()
            self.bucket = self.client.bucket(self.bucket_name)
            self.is_connected = True
            return True
        except GoogleCloudError as e:
            print(f"Error conectando a Google Cloud Storage: {e}")
            return False
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False
    
    def upload_file(self, local_path: str, remote_path: str) -> str:
        """Subir archivo a Google Cloud Storage"""
        if not self.is_connected:
            self.connect()
        
        try:
            blob = self.bucket.blob(remote_path)
            blob.upload_from_filename(local_path)
            return f"gs://{self.bucket_name}/{remote_path}"
        except Exception as e:
            print(f"Error subiendo archivo: {e}")
            return ""
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Descargar archivo de Google Cloud Storage"""
        if not self.is_connected:
            self.connect()
        
        try:
            if remote_path.startswith('gs://'):
                remote_path = remote_path.replace(f'gs://{self.bucket_name}/', '')
            
            blob = self.bucket.blob(remote_path)
            blob.download_to_filename(local_path)
            return True
        except Exception as e:
            print(f"Error descargando archivo: {e}")
            return False
    
    def delete_file(self, remote_path: str) -> bool:
        """Eliminar archivo de Google Cloud Storage"""
        if not self.is_connected:
            self.connect()
        
        try:
            if remote_path.startswith('gs://'):
                remote_path = remote_path.replace(f'gs://{self.bucket_name}/', '')
            
            blob = self.bucket.blob(remote_path)
            blob.delete()
            return True
        except Exception as e:
            print(f"Error eliminando archivo: {e}")
            return False
    
    def list_files(self, folder_path: str = "") -> List[str]:
        """Listar archivos en Google Cloud Storage"""
        if not self.is_connected:
            self.connect()
        
        try:
            blobs = self.bucket.list_blobs(prefix=folder_path)
            return [blob.name for blob in blobs]
        except Exception as e:
            print(f"Error listando archivos: {e}")
            return []
    
    def search_files(self, query: str) -> List[str]:
        """Buscar archivos en Google Cloud Storage"""
        if not self.is_connected:
            self.connect()
        
        try:
            blobs = self.bucket.list_blobs()
            return [blob.name for blob in blobs 
                   if query.lower() in blob.name.lower()]
        except Exception as e:
            print(f"Error buscando archivos: {e}")
            return []