import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import os
from ..storage import EvidenceDatabase
from ..storage.google_drive_storage import GoogleDriveStorage
from ..storage.dropbox_storage import DropboxStorage
from ..storage.aws_s3_storage import AWSS3Storage
from ..storage.gcs_storage import GCSStorage
from ..utils.helpers import generate_id, validate_image, resize_image, format_date, sanitize_filename

class EvidenceManagerGUI:
    """Interfaz gráfica principal para el gestor de evidencias"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Evidencias de Problemas")
        self.root.geometry("800x600")
        
        # Inicializar base de datos
        self.db = EvidenceDatabase()
        
        # Almacenamiento activo
        self.active_storage = None
        
        # Crear interfaz
        self.create_widgets()
        
        # Cargar evidencias existentes
        self.load_evidence_list()
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña de carga
        self.create_upload_tab()
        
        # Pestaña de búsqueda
        self.create_search_tab()
        
        # Pestaña de configuración
        self.create_config_tab()
    
    def create_upload_tab(self):
        """Crear pestaña de carga de evidencias"""
        self.upload_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.upload_frame, text="Cargar Evidencia")
        
        # Formulario de carga
        form_frame = ttk.LabelFrame(self.upload_frame, text="Nueva Evidencia")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Selección de imagen
        ttk.Label(form_frame, text="Imagen:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.image_path = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.image_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(form_frame, text="Seleccionar", command=self.select_image).grid(row=0, column=2, padx=5, pady=5)
        
        # Descripción
        ttk.Label(form_frame, text="Descripción:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.description = tk.Text(form_frame, height=4, width=50)
        self.description.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
        
        # Tipo de problema
        ttk.Label(form_frame, text="Tipo de Problema:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.problem_type = ttk.Combobox(form_frame, values=["Mecánico", "Eléctrico", "Estructural", "Software", "Otro"])
        self.problem_type.grid(row=2, column=1, padx=5, pady=5)
        
        # Proyecto
        ttk.Label(form_frame, text="Proyecto:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.project = ttk.Entry(form_frame, width=30)
        self.project.grid(row=3, column=1, padx=5, pady=5)
        
        # Etiquetas
        ttk.Label(form_frame, text="Etiquetas (separadas por coma):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.tags = ttk.Entry(form_frame, width=30)
        self.tags.grid(row=4, column=1, padx=5, pady=5)
        
        # Botón de carga
        ttk.Button(form_frame, text="Cargar Evidencia", command=self.upload_evidence).grid(row=5, column=1, pady=10)
    
    def create_search_tab(self):
        """Crear pestaña de búsqueda"""
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="Buscar Evidencias")
        
        # Filtros de búsqueda
        filter_frame = ttk.LabelFrame(self.search_frame, text="Filtros de Búsqueda")
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Búsqueda por texto
        ttk.Label(filter_frame, text="Texto:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.search_text = ttk.Entry(filter_frame, width=30)
        self.search_text.grid(row=0, column=1, padx=5, pady=5)
        
        # Tipo de problema
        ttk.Label(filter_frame, text="Tipo:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.search_type = ttk.Combobox(filter_frame, values=["Todos", "Mecánico", "Eléctrico", "Estructural", "Software", "Otro"])
        self.search_type.set("Todos")
        self.search_type.grid(row=0, column=3, padx=5, pady=5)
        
        # Proyecto
        ttk.Label(filter_frame, text="Proyecto:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.search_project = ttk.Entry(filter_frame, width=30)
        self.search_project.grid(row=1, column=1, padx=5, pady=5)
        
        # Botón de búsqueda
        ttk.Button(filter_frame, text="Buscar", command=self.search_evidence).grid(row=1, column=3, padx=5, pady=5)
        
        # Lista de resultados
        self.results_tree = ttk.Treeview(self.search_frame, columns=("Fecha", "Tipo", "Proyecto", "Descripción"), show="headings")
        self.results_tree.heading("Fecha", text="Fecha")
        self.results_tree.heading("Tipo", text="Tipo")
        self.results_tree.heading("Proyecto", text="Proyecto")
        self.results_tree.heading("Descripción", text="Descripción")
        self.results_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.search_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón para ver detalles
        ttk.Button(self.search_frame, text="Ver Detalles", command=self.view_evidence_details).pack(pady=5)
    
    def create_config_tab(self):
        """Crear pestaña de configuración"""
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="Configuración")
        
        # Selección de nube
        cloud_frame = ttk.LabelFrame(self.config_frame, text="Configuración de Nube")
        cloud_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(cloud_frame, text="Proveedor:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.cloud_provider = ttk.Combobox(cloud_frame, values=["Google Drive", "Dropbox", "AWS S3", "Google Cloud Storage"])
        self.cloud_provider.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(cloud_frame, text="Configurar", command=self.configure_cloud).grid(row=0, column=2, padx=5, pady=5)
        
        # Estado de conexión
        self.connection_status = ttk.Label(cloud_frame, text="No conectado", foreground="red")
        self.connection_status.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Información de configuración
        info_frame = ttk.LabelFrame(self.config_frame, text="Información")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text="Total de evidencias:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.total_evidence = ttk.Label(info_frame, text="0")
        self.total_evidence.grid(row=0, column=1, padx=5, pady=5)
    
    def select_image(self):
        """Seleccionar imagen del sistema de archivos"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if file_path:
            self.image_path.set(file_path)
    
    def upload_evidence(self):
        """Cargar una nueva evidencia"""
        try:
            # Validar campos
            if not self.image_path.get():
                messagebox.showerror("Error", "Debes seleccionar una imagen")
                return
            
            description = self.description.get("1.0", tk.END).strip()
            if not description:
                messagebox.showerror("Error", "Debes ingresar una descripción")
                return
            
            if not self.problem_type.get():
                messagebox.showerror("Error", "Debes seleccionar un tipo de problema")
                return
            
            if not self.project.get():
                messagebox.showerror("Error", "Debes ingresar un proyecto")
                return
            
            # Validar imagen
            is_valid, message = validate_image(self.image_path.get())
            if not is_valid:
                messagebox.showerror("Error", message)
                return
            
            # Redimensionar si es necesario
            image_path = resize_image(self.image_path.get())
            
            # Crear objeto de evidencia
            from ..models.evidence import Evidence
            evidence = Evidence(
                id=generate_id(),
                image_path=image_path,
                description=description,
                problem_type=self.problem_type.get(),
                project=self.project.get(),
                date=datetime.now(),
                cloud_provider="local",
                tags=[tag.strip() for tag in self.tags.get().split(",") if tag.strip()]
            )
            
            # Guardar en base de datos local
            if self.db.add_evidence(evidence):
                messagebox.showinfo("Éxito", "Evidencia cargada correctamente")
                
                # Limpiar formulario
                self.image_path.set("")
                self.description.delete("1.0", tk.END)
                self.problem_type.set("")
                self.project.delete(0, tk.END)
                self.tags.delete(0, tk.END)
                
                # Actualizar lista
                self.load_evidence_list()
            else:
                messagebox.showerror("Error", "Error al guardar la evidencia")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar evidencia: {str(e)}")
    
    def search_evidence(self):
        """Buscar evidencias según filtros"""
        try:
            query = self.search_text.get()
            problem_type = self.search_type.get() if self.search_type.get() != "Todos" else None
            project = self.search_project.get()
            
            results = self.db.search_evidence(
                query=query if query else None,
                problem_type=problem_type,
                project=project if project else None
            )
            
            # Limpiar resultados anteriores
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # Mostrar resultados
            for evidence in results:
                self.results_tree.insert("", tk.END, values=(
                    format_date(evidence.date),
                    evidence.problem_type,
                    evidence.project,
                    evidence.description[:50] + "..." if len(evidence.description) > 50 else evidence.description
                ))
            
            if not results:
                messagebox.showinfo("Resultados", "No se encontraron evidencias")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar: {str(e)}")
    
    def view_evidence_details(self):
        """Ver detalles de una evidencia seleccionada"""
        selected_item = self.results_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Selecciona una evidencia para ver detalles")
            return
        
        # Aquí se podría implementar una ventana de detalles
        messagebox.showinfo("Detalles", "Funcionalidad de detalles en desarrollo")
    
    def configure_cloud(self):
        """Configurar conexión con nube"""
        provider = self.cloud_provider.get()
        if not provider:
            messagebox.showwarning("Advertencia", "Selecciona un proveedor de nube")
            return
        
        # Aquí se implementaría la configuración específica para cada proveedor
        messagebox.showinfo("Configuración", f"Configuración para {provider} en desarrollo")
    
    def load_evidence_list(self):
        """Cargar lista de evidencias en la interfaz"""
        try:
            evidences = self.db.get_all_evidence()
            self.total_evidence.config(text=str(len(evidences)))
        except Exception as e:
            print(f"Error cargando evidencias: {e}")

def main():
    root = tk.Tk()
    app = EvidenceManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()