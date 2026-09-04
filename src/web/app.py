from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from ..storage import EvidenceDatabase
from ..storage.google_drive_storage import GoogleDriveStorage
from ..storage.dropbox_storage import DropboxStorage
from ..storage.aws_s3_storage import AWSS3Storage
from ..storage.gcs_storage import GCSStorage
from ..utils.helpers import generate_id, validate_image, resize_image, format_date, sanitize_filename
from ..models.evidence import Evidence

# Configurar rutas correctas para templates y static
template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.secret_key = 'tu_clave_secreta_aqui'

# Crear directorio de uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializar base de datos
db = EvidenceDatabase()

# Almacenamiento activo
active_storage = None

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_evidence():
    """Endpoint simplificado para cargar evidencias desde chat"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No se envió ninguna imagen'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        # Crear directorio de uploads si no existe
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Guardar archivo localmente
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Validar imagen
        is_valid, message = validate_image(filepath)
        if not is_valid:
            os.remove(filepath)
            return jsonify({'error': message}), 400
        
        # Redimensionar si es necesario
        filepath = resize_image(filepath)
        
        # Obtener datos del formulario (con valores por defecto simplificados)
        description = request.form.get('description', 'Sin descripción')
        problem_type = request.form.get('problem_type', 'General')
        project = request.form.get('project', 'Personal')
        tags = [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()]
        
        # Crear objeto de evidencia
        evidence = Evidence(
            id=generate_id(),
            image_path=filepath,
            description=description,
            problem_type=problem_type,
            project=project,
            date=datetime.now(),
            cloud_provider="local",
            tags=tags
        )
        
        # Guardar en base de datos
        if db.add_evidence(evidence):
            return jsonify({'success': True, 'evidence_id': evidence.id})
        else:
            return jsonify({'error': 'Error al guardar en base de datos'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['GET'])
def search_evidence():
    """Endpoint para buscar evidencias"""
    try:
        query = request.args.get('query')
        problem_type = request.args.get('problem_type')
        project = request.args.get('project')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Convertir fechas si se proporcionan
        date_from_obj = datetime.fromisoformat(date_from) if date_from else None
        date_to_obj = datetime.fromisoformat(date_to) if date_to else None
        
        results = db.search_evidence(
            query=query if query else None,
            problem_type=problem_type if problem_type and problem_type != "all" else None,
            project=project if project else None,
            date_from=date_from_obj,
            date_to=date_to_obj
        )
        
        # Convertir a formato JSON
        results_json = [evidence.to_dict() for evidence in results]
        
        return jsonify({'success': True, 'results': results_json})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/evidence/<evidence_id>')
def get_evidence(evidence_id):
    """Obtener detalles de una evidencia específica"""
    try:
        evidence = db.get_evidence(evidence_id)
        if evidence:
            return jsonify({'success': True, 'evidence': evidence.to_dict()})
        else:
            return jsonify({'error': 'Evidencia no encontrada'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/image/<evidence_id>')
def get_image(evidence_id):
    """Obtener imagen de una evidencia"""
    try:
        evidence = db.get_evidence(evidence_id)
        if evidence and os.path.exists(evidence.image_path):
            return send_file(evidence.image_path)
        else:
            return jsonify({'error': 'Imagen no encontrada'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/evidence/<evidence_id>', methods=['DELETE'])
def delete_evidence(evidence_id):
    """Eliminar una evidencia"""
    try:
        evidence = db.get_evidence(evidence_id)
        if not evidence:
            return jsonify({'error': 'Evidencia no encontrada'}), 404
        
        # Eliminar archivo de imagen si existe
        if os.path.exists(evidence.image_path):
            os.remove(evidence.image_path)
        
        # Eliminar de la base de datos
        if db.delete_evidence(evidence_id):
            return jsonify({'success': True, 'message': 'Evidencia eliminada correctamente'})
        else:
            return jsonify({'error': 'Error al eliminar de la base de datos'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/config/cloud', methods=['POST'])
def configure_cloud():
    """Configurar conexión con nube"""
    try:
        provider = request.json.get('provider')
        config = request.json.get('config', {})
        
        if not provider:
            return jsonify({'error': 'Proveedor no especificado'}), 400
        
        # Guardar configuración
        if db.save_cloud_config(provider, config, is_active=True):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Error al guardar configuración'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/config/cloud/<provider>', methods=['GET'])
def get_cloud_config(provider):
    """Obtener configuración de nube"""
    try:
        config_data = db.get_cloud_config(provider)
        if config_data:
            return jsonify({'success': True, 'config': config_data})
        else:
            return jsonify({'error': 'Configuración no encontrada'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def get_stats():
    """Obtener estadísticas del sistema"""
    try:
        evidences = db.get_all_evidence()
        
        # Calcular estadísticas
        total = len(evidences)
        by_type = {}
        by_project = {}
        
        for evidence in evidences:
            by_type[evidence.problem_type] = by_type.get(evidence.problem_type, 0) + 1
            by_project[evidence.project] = by_project.get(evidence.project, 0) + 1
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'by_type': by_type,
                'by_project': by_project
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)