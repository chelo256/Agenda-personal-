# Evidence Manager

Sistema de gestión de evidencias de problemas para trabajo. Permite cargar, organizar y buscar evidencias (imágenes + descripciones) con almacenamiento local y en la nube.

## Características

- **Carga de evidencias**: Sube imágenes con descripciones detalladas
- **Organización**: Clasifica por tipo de problema, proyecto, fecha y etiquetas
- **Búsqueda avanzada**: Busca por texto, tipo, proyecto, fecha y combinaciones
- **Múltiples interfaces**: GUI (tkinter) y Web (Flask)
- **Almacenamiento flexible**: Local y múltiples nubes (Google Drive, Dropbox, AWS S3, Google Cloud Storage)
- **Base de datos local**: SQLite para metadatos y búsqueda rápida

## Instalación

1. Clonar o descargar el proyecto
2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Uso

### Interfaz Gráfica (GUI)

```bash
python main.py
```

Selecciona la opción 1 para iniciar la interfaz gráfica.

### Interfaz Web

```bash
python main.py
```

Selecciona la opción 2 para iniciar la interfaz web, luego abre tu navegador en `http://localhost:5000`

## Configuración de Nube

### Google Drive
1. Crea un proyecto en Google Cloud Console
2. Habilita la API de Google Drive
3. Descarga el archivo `credentials.json`
4. Configura la ruta en la aplicación

### Dropbox
1. Crea una app en Dropbox Developers
2. Genera un access token
3. Configura el token en la aplicación

### AWS S3
1. Crea un bucket en AWS S3
2. Configura las credenciales AWS (Access Key, Secret Key)
3. Especifica el nombre del bucket y región

### Google Cloud Storage
1. Crea un bucket en GCS
2. Descarga el archivo de credenciales de service account
3. Configura la ruta y nombre del bucket

## Estructura del Proyecto

```
evidence_manager/
├── main.py                 # Punto de entrada principal
├── requirements.txt        # Dependencias
├── src/
│   ├── models/            # Modelos de datos
│   │   └── evidence.py    # Modelo de evidencia
│   ├── storage/           # Conectores de almacenamiento
│   │   ├── base_storage.py
│   │   ├── google_drive_storage.py
│   │   ├── dropbox_storage.py
│   │   ├── aws_s3_storage.py
│   │   ├── gcs_storage.py
│   │   └── database.py    # Base de datos local
│   ├── gui/               # Interfaz gráfica
│   │   └── main_window.py
│   ├── web/               # Interfaz web
│   │   └── app.py
│   └── utils/             # Utilidades
│       └── helpers.py
├── templates/             # Plantillas web
│   └── index.html
└── static/                # Archivos estáticos web
```

## Funcionalidades

### Carga de Evidencias
- Selección de imagen del sistema local
- Descripción detallada del problema
- Clasificación por tipo (Mecánico, Eléctrico, Estructural, Software, Otro)
- Asignación a proyecto
- Etiquetas personalizadas
- Redimensionamiento automático de imágenes

### Búsqueda
- Búsqueda por texto en descripciones
- Filtrado por tipo de problema
- Filtrado por proyecto
- Filtrado por rango de fechas
- Combinación de múltiples filtros

### Almacenamiento
- Base de datos local (SQLite) para metadatos
- Opcional: Sincronización con nube
- Soporte para múltiples proveedores de nube

## Desarrollo

El sistema está diseñado para ser extensible. Puedes agregar:

- Nuevos conectores de almacenamiento heredando de `BaseStorage`
- Nuevos tipos de problema en la interfaz
- Campos adicionales en el modelo de evidencia
- Funcionalidades de búsqueda personalizadas

## Seguridad

- Las credenciales de nube se almacenan localmente en la base de datos
- Se recomienda no compartir el archivo de base de datos
- Para producción, considera usar variables de entorno para credenciales

## Licencia

Este proyecto es de uso personal para gestión de evidencias en el trabajo.