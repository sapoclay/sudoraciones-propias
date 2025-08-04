#!/usr/bin/env python3
"""
Sudoraciones Propias - Launcher Optimizado
Iniciador de la aplicación de entrenamiento optimizada para principiantes
"""

import os
import sys
import subprocess
import time
import venv
from pathlib import Path

def get_venv_path():
    """Obtener la ruta del entorno virtual"""
    return Path.cwd() / "venv_sudoraciones"

def get_venv_python():
    """Obtener la ruta del Python del entorno virtual"""
    venv_path = get_venv_path()
    if os.name == 'nt':  # Windows
        return venv_path / "Scripts" / "python.exe"
    else:  # Linux/Mac
        return venv_path / "bin" / "python"

def get_venv_pip():
    """Obtener la ruta del pip del entorno virtual"""
    venv_path = get_venv_path()
    if os.name == 'nt':  # Windows
        return venv_path / "Scripts" / "pip.exe"
    else:  # Linux/Mac
        return venv_path / "bin" / "pip"

def create_virtual_environment():
    """Crear entorno virtual si no existe"""
    venv_path = get_venv_path()
    
    if venv_path.exists():
        print(f"  ✅ Entorno virtual ya existe: {venv_path}")
        return True
    
    print(f"  🔧 Creando entorno virtual: {venv_path}")
    try:
        venv.create(venv_path, with_pip=True)
        print(f"  ✅ Entorno virtual creado exitosamente")
        return True
    except Exception as e:
        print(f"  ❌ Error creando entorno virtual: {e}")
        return False

def install_requirements():
    """Instalar dependencias en el entorno virtual"""
    pip_path = get_venv_pip()
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("  ❌ Archivo requirements.txt no encontrado")
        return False
    
    print("  📦 Instalando dependencias en entorno virtual...")
    try:
        cmd = [str(pip_path), "install", "-r", str(requirements_file)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("  ✅ Dependencias instaladas correctamente")
            return True
        else:
            print(f"  ❌ Error instalando dependencias: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("  ❌ Timeout instalando dependencias")
        return False
    except Exception as e:
        print(f"  ❌ Error ejecutando pip: {e}")
        return False

def setup_virtual_environment():
    """Configurar entorno virtual completo"""
    print("🔧 Configurando entorno virtual...")
    
    # Crear entorno virtual
    if not create_virtual_environment():
        return False
    
    # Instalar dependencias
    if not install_requirements():
        return False
    
    print("  ✅ Entorno virtual configurado correctamente")
    return True

def print_banner():
    """Mostrar banner de inicio"""
    print("\n" + "="*60)
    print("🎯 SUDORACIONES PROPIAS - SISTEMA DE ENTRENAMIENTO")
    print("="*60)
    print("💪 Entrenamiento Personalizado para Principiantes y Expertos")
    print("📊 21 ejercicios especializados (5 pecho + 4 abdominales + 3 brazos + 2 gemelos)")
    print("⏰ Progresión automática inteligente")
    print("📈 Hasta 20 semanas de entrenamiento continuo")
    print("🏗️ Arquitectura Modular Optimizada")
    print("="*60)

def check_dependencies():
    """Verificar dependencias necesarias en el entorno virtual"""
    print("🔍 Verificando dependencias en entorno virtual...")
    
    # Usar el Python del entorno virtual para verificar
    venv_python = get_venv_python()
    
    if not venv_python.exists():
        print("  ❌ Entorno virtual no encontrado")
        return False
    
    # Verificar Streamlit
    try:
        cmd = [str(venv_python), "-c", "import streamlit; print(streamlit.__version__)"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"  ✅ Streamlit {version}")
        else:
            print("  ❌ Streamlit no encontrado en entorno virtual")
            return False
    except Exception:
        print("  ❌ Error verificando Streamlit")
        return False
    
    # Verificar Pandas
    try:
        cmd = [str(venv_python), "-c", "import pandas; print(pandas.__version__)"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"  ✅ Pandas {version}")
        else:
            print("  ❌ Pandas no encontrado en entorno virtual")
            return False
    except Exception:
        print("  ❌ Error verificando Pandas")
        return False
    
    # Verificar Plotly
    try:
        cmd = [str(venv_python), "-c", "import plotly; print(plotly.__version__)"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"  ✅ Plotly {version}")
        else:
            print("  ❌ Plotly no encontrado en entorno virtual")
            return False
    except Exception:
        print("  ❌ Error verificando Plotly")
        return False
    
    return True

def check_files():
    """Verificar archivos necesarios para la aplicación modular"""
    print("📁 Verificando archivos...")
    
    required_files = [
        'main_app.py',  # Aplicación modular principal
        'config.json', 
        'progress_data.json',
        'requirements.txt'
    ]
    
    # Verificar archivos obligatorios
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  ✅ {file} ({size} bytes)")
        else:
            print(f"  ❌ {file} no encontrado")
            return False
    
    # Verificar directorio de módulos (obligatorio para app modular)
    if os.path.exists('modules') and os.path.isdir('modules'):
        module_files = [f for f in os.listdir('modules') if f.endswith('.py')]
        print(f"  ✅ modules/ ({len(module_files)} módulos) - Arquitectura modular")
        
        # Verificar módulos específicos
        required_modules = [
            '__init__.py',
            'base_trainer.py',
            'training_plan.py', 
            'progress_calendar.py',
            'statistics.py',
            'info.py'
        ]
        
        for module in required_modules:
            module_path = f"modules/{module}"
            if os.path.exists(module_path):
                print(f"    ✅ {module}")
            else:
                print(f"    ❌ {module} no encontrado")
                return False
    else:
        print(f"  ❌ modules/ no encontrado - Requerido para aplicación modular")
        return False
    
    return True

def kill_existing_streamlit():
    """Terminar procesos existentes de Streamlit"""
    try:
        result = subprocess.run(['pkill', '-f', 'streamlit'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  🔄 Procesos anteriores terminados")
        time.sleep(2)
    except Exception:
        pass

def get_app_file():
    """Obtener el archivo de la aplicación modular"""
    if os.path.exists("main_app.py"):
        return "main_app.py"
    else:
        print("❌ main_app.py no encontrado.")
        return None

def start_streamlit():
    """Iniciar la aplicación Streamlit modular en el entorno virtual"""
    # Obtener archivo de la aplicación modular
    app_file = get_app_file()
    
    if not app_file:
        print("❌ No se puede iniciar: aplicación modular no encontrada")
        return {'success': False}
    
    print("🚀 Iniciando aplicación MODULAR en entorno virtual...")
    print("  ✨ Arquitectura modular por pestañas")
    print("  🏗️ Código organizado y mantenible")
    
    # Configuración optimizada
    port = 8508
    address = "0.0.0.0"
    venv_python = get_venv_python()
    
    # Variables de entorno básicas para reducir mensajes
    env = os.environ.copy()
    env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    env['STREAMLIT_GLOBAL_SUPPRESS_DEPRECATION_WARNINGS'] = 'true'
    
    print(f"  📡 Puerto: {port}")
    print(f"  🌐 Dirección: {address}")
    print(f"  🐍 Python: {venv_python}")
    print("  🔇 Mensajes de deploy suprimidos via CSS")
    print("  ⏳ Iniciando servidor...")
    
    try:
        # Configuración simplificada de Streamlit
        cmd = [
            str(venv_python), '-m', 'streamlit', 'run',
            app_file,  # Usar el archivo elegido por el usuario
            '--server.port', str(port),
            '--server.address', address,
            '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false'
        ]
        
        # Iniciar proceso 
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL,
                                 env=env)
        
        # Esperar a que inicie
        time.sleep(5)
        
        # Verificar que está ejecutándose
        check_cmd = ['netstat', '-tuln']
        result = subprocess.run(check_cmd, capture_output=True, text=True)
        
        if f":{port}" in result.stdout:
            print("  ✅ ¡Servidor iniciado correctamente!")
            print(f"  📱 Aplicación: {app_file}")
            # Retornar las URLs en lugar de imprimirlas aquí
            return {
                'success': True,
                'local_url': f"http://localhost:{port}",
                'external_url': f"http://0.0.0.0:{port}",
                'app_file': app_file
            }
        else:
            print("  ❌ Error: servidor no responde")
            return {'success': False}
            
    except Exception as e:
        print(f"  ❌ Error al iniciar: {e}")
        return {'success': False}

def show_summary():
    """Mostrar resumen de la aplicación modular optimizada"""
    print("\n" + "="*60)
    print("📊 RESUMEN DE LA APLICACIÓN MODULAR")
    print("="*60)
    print("💪 ENTRENAMIENTO PERSONALIZADO OPTIMIZADO:")
    print("  • 21 ejercicios especializados")
    print("  • 5 ejercicios de pecho + 4 de abdominales + 2 de gemelos")
    print("  • Progresión automática hasta 20 semanas")
    print("  • Sistema de niveles: Principiante → Experto")
    print("")
    print("🏗️ ARQUITECTURA MODULAR:")
    print("  • ⭐ Código organizado por pestañas")
    print("  • 📦 6 módulos especializados")
    print("  • 🔧 Fácil mantenimiento y escalabilidad")
    print("  • 🧪 Testing individual por módulo")
    print("")
    print("💪 GRUPOS MUSCULARES:")
    print("  • Pecho: Press de Banca + Aperturas + Press Inclinado + Flexiones")
    print("  • Espalda: Remo + Remo Una Mano + Peso Muerto")
    print("  • Hombros: Press Militar + Elevaciones Laterales + Frontales + Pájaros")
    print("  • Brazos: Curl Bíceps + Martillo + Concentrado + Extensiones + Patadas")
    print("  • Piernas: Sentadillas + Zancadas + Peso Muerto Rumano + Sumo + Talones")
    print("  • Abdominales: Tradicionales + Plancha + Bajas + Laterales")
    print("  • Cardio: Bicicleta Estática")
    print("")
    print("🚀 CARACTERÍSTICAS:")
    print("  • ✅ Sistema automático de seguimiento")
    print("  • ✅ Calendario inteligente con porcentajes")
    print("  • ✅ Progresión automática hasta 20 semanas")
    print("  • ✅ Videos YouTube integrados (Shorts + normales)")
    print("  • ✅ Instrucciones detalladas y consejos")
    print("  • ✅ Entorno virtual aislado y automático")
    print("  • ✅ Interfaz completamente en español")
    print("="*60)

def main():
    """Función principal"""
    print_banner()
    
    # Configurar entorno virtual
    if not setup_virtual_environment():
        print("\n❌ Error configurando entorno virtual. Ejecuta manualmente:")
        print("   python -m venv venv_sudoraciones")
        print("   source venv_sudoraciones/bin/activate  # Linux/Mac")
        print("   venv_sudoraciones\\Scripts\\activate     # Windows")
        print("   pip install -r requirements.txt")
        return False
    
    # Verificaciones
    if not check_dependencies():
        print("\n❌ Faltan dependencias en entorno virtual.")
        print("   Reinstalando automáticamente...")
        if not install_requirements():
            print("   Error en instalación automática.")
            return False
    
    if not check_files():
        print("\n❌ Faltan archivos necesarios.")
        return False
    
    # Terminar procesos anteriores
    print("\n🔄 Preparando inicio...")
    kill_existing_streamlit()
    
    # Iniciar aplicación
    server_result = start_streamlit()
    if server_result['success']:
        show_summary()
        print("\n🎉 ¡APLICACIÓN MODULAR LISTA PARA ENTRENAR!")
        print("   Accede desde tu navegador a las siguientes URLs:")
        print(f"   🌐 URL local: {server_result['local_url']}")
        print(f"   🌐 URL externa: {server_result['external_url']}")
        print(f"   📱 Aplicación: {server_result['app_file']} (Modular)")
        print("   Presiona Ctrl+C para detener la aplicación")
        print(f"   Entorno virtual: {get_venv_path()}")
        
        try:
            # Mantener el script corriendo
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n\n👋 Deteniendo aplicación...")
            kill_existing_streamlit()
            print("✅ Aplicación detenida correctamente")
        
        return True
    else:
        print("\n❌ Error al iniciar la aplicación")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
