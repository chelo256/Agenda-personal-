#!/usr/bin/env python3
"""
Evidence Manager - Sistema de gestión de evidencias de problemas
Aplicación principal con soporte para interfaz GUI y web
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Función principal"""
    import sys
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("=== Evidence Manager ===")
        print("Sistema de gestión de evidencias de problemas")
        print()
        
        # Menu de selección de interfaz
        print("Selecciona el modo de ejecución:")
        print("1. Interfaz Gráfica (GUI)")
        print("2. Interfaz Web")
        print("3. Salir")
        
        try:
            choice = input("Ingresa tu opción (1-3): ").strip()
        except EOFError:
            print("Error: No se pudo leer la entrada. Usa argumentos de línea de comandos:")
            print("python main.py gui  # Para interfaz gráfica")
            print("python main.py web  # Para interfaz web")
            sys.exit(1)
    
    if choice in ["1", "gui"]:
        print("Iniciando interfaz gráfica...")
        from src.gui import main as gui_main
        gui_main()
    elif choice in ["2", "web"]:
        print("Iniciando interfaz web...")
        
        # Verificar si estamos en Railway (variable de entorno)
        import os
        port = int(os.environ.get('PORT', 5000))
        debug_mode = os.environ.get('RAILWAY_ENVIRONMENT') is None
        
        print(f"La aplicación web estará disponible en el puerto {port}")
        from src.web.app import app
        app.run(debug=debug_mode, host='0.0.0.0', port=port)
    elif choice in ["3", "exit"]:
        print("Saliendo...")
        sys.exit(0)
    else:
        print("Opción no válida")
        print("Usa: python main.py [gui|web|exit]")
        sys.exit(1)

if __name__ == "__main__":
    main()