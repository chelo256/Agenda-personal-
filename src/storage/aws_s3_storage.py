from .base_storage import BaseStorage
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os
from typing import List

class AWSS3Storage(BaseStorage):
    """Conector para AWS S3"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.s3_client = None
        self.bucket_name = config.get('bucket_name', '')
        self.region = config.get('region', 'us-east-1')
        self.aws_access_key = config.get('aws_access_key', '')
        self.aws_secret_key = config.get('aws_secret_key', '')
    
    def connect(self) -> bool:
        """Establecer conexión con AWS S3"""
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key
            )
            # Verificar conexión listando buckets
            self.s3_client.list_buckets()
            self.is_connected = True
            return True
        except NoCredentialsError:
            print("Error: Credenciales de AWS no encontradas")
            return False
        except Exception as e:
            print(f"Error conectando a AWS S3: {e}")
            return False
    
    def upload_file(self, local_path: str, remote_path: str) -> str:
        """Subir archivo a AWS S3"""
        if not self.is_connected:
            self.connect()
        
        try:
            self.s3_client.upload_file(local_path, self.bucket_name, remote_path)
            return f"s3://{self.bucket_name}/{remote_path}"
        except Exception as e:
            print(f"Error subiendo archivo: {e}")
            return ""
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Descargar archivo de AWS S3"""
        if not self.is_connected:
            self.connect()
        
        try:
            # Extraer el path del archivo de la URL s3://
            if remote_path.startswith('s3://'):
                remote_path = remote_path.replace(f's3://{self.bucket_name}/', '')
            
            self.s3_client.download_file(self.bucket_name, remote_path, local_path)
            return True
        except Exception as e:
            print(f"Error descargando archivo: {e}")
            return False
    
    def delete_file(self, remote_path: str) -> bool:
        """Eliminar archivo de AWS S3"""
        if not self.is_connected:
            self.connect()
        
        try:
            if remote_path.startswith('s3://'):
                remote_path = remote_path.replace(f's3://{self.bucket_name}/', '')
            
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=remote_path)
            return True
        except Exception as e:
            print(f"Error eliminando archivo: {e}")
            return False
    
    def list_files(self, folder_path: str = "") -> List[str]:
        """Listar archivos en AWS S3"""
        if not self.is_connected:
            self.connect()
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=folder_path
            )
            
            if 'Contents' not in response:
                return []
            
            return [obj['Key'] for obj in response['Contents']]
        except Exception as e:
            print(f"Error listando archivos: {e}")
            return []
    
    def search_files(self, query: str) -> List[str]:
        """Buscar archivos en AWS S3"""
        if not self.is_connected:
            self.connect()
        
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            
            if 'Contents' not in response:
                return []
            
            return [obj['Key'] for obj in response['Contents'] 
                   if query.lower() in obj['Key'].lower()]
        except Exception as e:
            print(f"Error buscando archivos: {e}")
            return []