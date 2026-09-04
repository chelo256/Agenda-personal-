# Guía de Instalación - Evidence Manager

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- (Opcional) Cuentas en servicios de nube que desees usar

## Instalación Paso a Paso

### 1. Descargar el Proyecto

Si tienes el código fuente, navega al directorio del proyecto:

```bash
cd evidence_manager
```

### 2. Crear Entorno Virtual (Recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno (Opcional)

Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus configuraciones específicas, especialmente si vas a usar servicios de nube.

### 5. Ejecutar la Aplicación

```bash
python main.py
```

Selecciona el modo de ejecución:
- **Opción 1**: Interfaz Gráfica (GUI)
- **Opción 2**: Interfaz Web (abre en http://localhost:5000)

## Configuración de Servicios de Nube

### Google Drive

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto
3. Habilita la Google Drive API
4. Crea credenciales OAuth 2.0 (Desktop Application)
5. Descarga el archivo `credentials.json`
6. Colócalo en el directorio raíz del proyecto
7. La primera vez que uses Google Drive, se abrirá un navegador para autenticarte

### Dropbox

1. Ve a [Dropbox Developers](https://www.dropbox.com/developers)
2. Crea una nueva app
3. Genera un access token
4. Configura el token en el archivo `.env` o en la interfaz de configuración

### AWS S3

1. Crea una cuenta en [AWS](https://aws.amazon.com/)
2. Crea un bucket S3
3. Crea un usuario IAM con permisos S3
4. Obtén las credenciales (Access Key y Secret Key)
5. Configura las credenciales en el archivo `.env` o en la interfaz

### Google Cloud Storage

1. Crea un proyecto en [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un bucket en Cloud Storage
3. Crea una cuenta de servicio
4. Descarga el archivo JSON de credenciales
5. Configura la ruta en el archivo `.env` o en la interfaz

## Solución de Problemas

### Error: ModuleNotFoundError

Asegúrate de haber instalado todas las dependencias:

```bash
pip install -r requirements.txt
```

### Error de Autenticación en Google Drive

- Verifica que el archivo `credentials.json` esté en el directorio correcto
- Asegúrate de que la Google Drive API esté habilitada
- Elimina el archivo `token.pickle` y vuelve a autenticarte

### Error de Permiso en SQLite

Asegúrate de tener permisos de escritura en el directorio del proyecto.

### Imágenes No Se Cargan

- Verifica que el directorio `uploads` exista
- Asegúrate de que las imágenes no excedan el tamaño máximo (10MB por defecto)
- Verifica que el formato de imagen sea soportado (JPG, PNG, GIF, BMP)

## Pruebas de Funcionamiento

### Probar Interfaz Gráfica

1. Ejecuta `python main.py`
2. Selecciona opción 1
3. Prueba cargar una evidencia de prueba
4. Realiza una búsqueda
5. Verifica que la evidencia se muestre correctamente

### Probar Interfaz Web

1. Ejecuta `python main.py`
2. Selecciona opción 2
3. Abre http://localhost:5000 en tu navegador
4. Prueba cargar una evidencia
5. Realiza búsquedas
6. Verifica que las imágenes se muestren correctamente

## Próximos Pasos

Una vez instalado, puedes:

1. Cargar tus primeras evidencias de problemas
2. Configurar tu servicio de nube preferido
3. Organizar tus evidencias por proyectos y tipos
4. Usar las funciones de búsqueda para encontrar evidencias específicas
5. Personalizar los tipos de problema según tus necesidades

## Soporte

Si encuentras problemas:

1. Revisa esta guía de instalación
2. Verifica el archivo README.md
3. Asegúrate de tener las versiones correctas de Python y las dependencias
4. Revisa los mensajes de error específicos