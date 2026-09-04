import uuid
from datetime import datetime
from PIL import Image
import os
from typing import Tuple

def generate_id() -> str:
    """Generar un ID único para evidencias"""
    return str(uuid.uuid4())

def validate_image(image_path: str) -> Tuple[bool, str]:
    """Validar que un archivo es una imagen válida"""
    try:
        if not os.path.exists(image_path):
            return False, "El archivo no existe"
        
        with Image.open(image_path) as img:
            img.verify()
        
        # Verificar tamaño (máximo 10MB)
        file_size = os.path.getsize(image_path)
        if file_size > 10 * 1024 * 1024:
            return False, "La imagen excede el tamaño máximo de 10MB"
        
        return True, "Imagen válida"
    except Exception as e:
        return False, f"Error validando imagen: {str(e)}"

def resize_image(image_path: str, max_size: Tuple[int, int] = (1920, 1080)) -> str:
    """Redimensionar imagen si es muy grande"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(max_size, Image.LANCZOS)
            
            # Guardar con nuevo nombre
            base, ext = os.path.splitext(image_path)
            new_path = f"{base}_resized{ext}"
            img.save(new_path, quality=85)
            
            return new_path
    except Exception as e:
        print(f"Error redimensionando imagen: {e}")
        return image_path

def format_date(date: datetime) -> str:
    """Formatear fecha para mostrar"""
    return date.strftime("%Y-%m-%d %H:%M:%S")

def parse_date(date_string: str) -> datetime:
    """Parsear string de fecha a datetime"""
    try:
        return datetime.fromisoformat(date_string)
    except:
        return datetime.now()

def sanitize_filename(filename: str) -> str:
    """Sanitizar nombre de archivo para usar en nube"""
    # Remover caracteres problemáticos
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limitar longitud
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename