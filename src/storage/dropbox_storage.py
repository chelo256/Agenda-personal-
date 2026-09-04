from .base_storage import BaseStorage
import dropbox
from dropbox.exceptions import AuthError
import os
from typing import List

class DropboxStorage(BaseStorage):
    """Conector para Dropbox"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.dbx = None
        self.access_token = config.get('access_token', '')
    
    def connect(self) -> bool:
        """Establecer conexión con Dropbox"""
        try:
            self.dbx = dropbox.Dropbox(self.access_token)
            self.dbx.users_get_current_account()
            self.is_connected = True
            return True
        except AuthError as e:
            print(f"Error de autenticación Dropbox: {e}")
            return False
        except Exception as e:
            print(f"Error conectando a Dropbox: {e}")
            return False
    
    def upload_file(self, local_path: str, remote_path: str) -> str:
        """Subir archivo a Dropbox"""
        if not self.is_connected:
            self.connect()
        
        try:
            with open(local_path, 'rb') as f:
                self.dbx.files_upload(f.read(), remote_path)
            return remote_path
        except Exception as e:
            print(f"Error subiendo archivo: {e}")
            return ""
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Descargar archivo de Dropbox"""
        if not self.is_connected:
            self.connect()
        
        try:
            self.dbx.files_download_to_file(local_path, remote_path)
            return True
        except Exception as e:
            print(f"Error descargando archivo: {e}")
            return False
    
    def delete_file(self, remote_path: str) -> bool:
        """Eliminar archivo de Dropbox"""
        if not self.is_connected:
            self.connect()
        
        try:
            self.dbx.files_delete(remote_path)
            return True
        except Exception as e:
            print(f"Error eliminando archivo: {e}")
            return False
    
    def list_files(self, folder_path: str = "") -> List[str]:
        """Listar archivos en Dropbox"""
        if not self.is_connected:
            self.connect()
        
        try:
            files = self.dbx.files_list_folder(folder_path).entries
            return [file.name for file in files]
        except Exception as e:
            print(f"Error listando archivos: {e}")
            return []
    
    def search_files(self, query: str) -> List[str]:
        """Buscar archivos en Dropbox"""
        if not self.is_connected:
            self.connect()
        
        try:
            results = self.dbx.files_search(query).matches
            return [match.metadata.path_display for match in results]
        except Exception as e:
            print(f"Error buscando archivos: {e}")
            return []