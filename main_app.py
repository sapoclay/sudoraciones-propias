"""
Sudoraciones Propias - Aplicación Principal
Sistema de entrenamiento modularizado por pestañas
"""
import streamlit as st
import os

# Configuración inicial de Streamlit
st.set_page_config(
    page_title="💪 Sudoraciones Propias",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar módulos
from modules.base_trainer import BaseTrainer
from modules.training_plan import TrainingPlanModule
from modules.progress_calendar import ProgressModule
from modules.statistics import StatisticsModule
from modules.info import InfoModule

# CSS personalizado para mejorar el diseño 
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .exercise-card {
        background: white;
        color: #2c3e50;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .progress-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    
    .rest-day {
        background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: #2d3436;
    }
</style>
""", unsafe_allow_html=True)

# Script JavaScript para traducir la interfaz de Streamlit al español
st.markdown("""
<script>
// Diccionario de traducciones inglés -> español
const translations = {
    // Menú principal y tres puntos
    'Deploy': 'Implementar',
    'Share': 'Compartir',
    'Settings': 'Configuración',
    'Rerun': 'Ejecutar de nuevo',
    'Stop': 'Detener',
    'Clear cache': 'Limpiar caché',
    'Record a screencast': 'Grabar pantalla',
    'About': 'Acerca de',
    'View fullscreen': 'Ver pantalla completa',
    'Report a bug': 'Reportar error',
    'Get help': 'Obtener ayuda',
    'Made with Streamlit': 'Hecho con Streamlit',
    
    // Elementos de interfaz
    'Running': 'Ejecutándose',
    'Please wait...': 'Por favor espera...',
    'Connecting': 'Conectando',
    'Connection error': 'Error de conexión',
    'Download': 'Descargar',
    'Full screen': 'Pantalla completa',
    'Running...': 'Ejecutándose...'
};

// Función para traducir elementos
function translateElements() {
    // Traducir elementos con atributo title
    document.querySelectorAll('[title]').forEach(element => {
        const title = element.getAttribute('title');
        if (translations[title]) {
            element.setAttribute('title', translations[title]);
        }
    });
    
    // Traducir texto de elementos específicos
    document.querySelectorAll('button, span, div').forEach(element => {
        const text = element.textContent?.trim();
        if (text && translations[text]) {
            element.textContent = translations[text];
        }
    });
    
    // Traducir placeholder de inputs
    document.querySelectorAll('input[placeholder]').forEach(element => {
        const placeholder = element.getAttribute('placeholder');
        if (translations[placeholder]) {
            element.setAttribute('placeholder', translations[placeholder]);
        }
    });
}

// Ejecutar traducción cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', translateElements);

// Observar cambios en el DOM para traducir elementos dinámicos
const observer = new MutationObserver(() => {
    translateElements();
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

// Traducir elementos existentes
translateElements();
</script>
""", unsafe_allow_html=True)


class ModernHeavyDutyTrainer:
    """Aplicación principal coordinadora"""
    
    def __init__(self):
        """Inicializar la aplicación modular"""
        # Crear instancias de todos los módulos
        self.base_trainer = BaseTrainer()
        self.training_module = TrainingPlanModule()
        self.progress_module = ProgressModule()
        self.statistics_module = StatisticsModule()
        self.info_module = InfoModule()
        
        # Sincronizar datos entre módulos
        self._sync_modules()
    
    def _sync_modules(self):
        """Sincronizar configuración y datos entre módulos"""
        config = self.base_trainer.config
        progress_data = self.base_trainer.progress_data
        
        # Sincronizar configuración
        self.training_module.config = config
        self.training_module.progress_data = progress_data
        
        self.progress_module.config = config
        self.progress_module.progress_data = progress_data
        
        self.statistics_module.config = config
        self.statistics_module.progress_data = progress_data
        
        self.info_module.config = config
        self.info_module.progress_data = progress_data
        
        # Forzar actualización de entrenamientos completados
        self.training_module.update_completed_workouts()
    
    def reset_all_progress(self):
        """Reiniciar todo el progreso del usuario"""
        import datetime
        
        # Crear datos de progreso vacíos
        current_month = datetime.datetime.now().strftime('%Y-%m')
        fresh_progress_data = {
            'total_workouts': 0,
            'current_streak': 0,
            'longest_streak': 0,
            'monthly_data': {
                current_month: {}
            },
            'completed_exercises': {},
            'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Actualizar datos en memoria
        self.base_trainer.progress_data = fresh_progress_data
        self.progress_data = fresh_progress_data
        
        # Sincronizar con todos los módulos
        self._sync_modules()
        
        # Guardar al archivo
        self.base_trainer.save_progress_data()
        
        # Resetear semana actual
        st.session_state.current_week = 1
        
        # Mostrar confirmación
        st.success("🎉 ¡Progreso reiniciado completamente! Comenzando desde la Semana 1.")
        st.balloons()
    
    
    def render_header(self):
        """Renderizar cabecera principal"""
        st.markdown("""
        <div class="main-header">
            <h1>💪 Sudoraciones Propias</h1>
            <h3>Sistema de entrenamiento con 25 ejercicios especializados + Videos YouTube</h3>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Renderizar barra lateral con opciones completas"""
        with st.sidebar:
            st.markdown("## ⚙️ Configuración")
            
            # Selección de semana
            max_week = 20  # Permitir hasta 20 semanas de progresión
            selected_week = st.selectbox(
                "📅 Selecciona la semana:",
                options=list(range(1, max_week + 1)),
                index=min(st.session_state.current_week - 1, max_week - 1),
                help="El programa progresa automáticamente cada 4 semanas"
            )
            st.session_state.current_week = selected_week
            
            # Mostrar información del nivel actual
            week_info = self.base_trainer.get_week_info(selected_week)
            st.info(f"""
            **Nivel:** {week_info['level_name']}
            **Descripción:** {week_info['level_description']}
            **Semana en ciclo:** {week_info['week_in_cycle']}/4
            """)
            
            st.markdown("---")
            
            # Opciones de vista
            st.markdown("### 📊 Opciones de Vista")
            show_videos = st.checkbox("🎥 Mostrar videos", value=True)
            show_instructions = st.checkbox("📝 Mostrar instrucciones", value=True)
            show_tips = st.checkbox("💡 Mostrar consejos", value=True)
            
            st.markdown("---")
            
            # Información del programa
            st.markdown("### ℹ️ Información")
            st.info(f"""
            **Semana actual:** {selected_week}/20
            **Total ejercicios:** 20 (5 pecho + 4 abs + 2 gemelos + cardio)
            **Días por semana:** 3-4
            **Días de descanso:** 3-4
            """)
            
            # Estadísticas rápidas
            if self.base_trainer.progress_data.get('total_workouts', 0) > 0:
                st.markdown("### 📈 Estadísticas")
                st.metric("Entrenamientos totales", self.base_trainer.progress_data['total_workouts'])
            
            # Información de arquitectura modular
            st.markdown("---")
            st.markdown("### 🏗️ Arquitectura")
            st.markdown("""
            **Sistema Modular:**
            - 🎯 Plan de Entrenamiento
            - 📊 Progreso y Calendario  
            - 📈 Estadísticas
            - ℹ️ Información del Programa
            - 🔧 Core del Sistema
            """)
            
            # Sección de reinicio de progreso
            st.markdown("---")
            st.markdown("### 🔄 Gestión de Progreso")
            
            # Mostrar información del progreso actual
            total_workouts = self.base_trainer.progress_data.get('total_workouts', 0)
            if total_workouts > 0:
                st.info(f"📊 **Progreso actual:** {total_workouts} entrenamientos completados")
            
            # Botón de reinicio con confirmación
            if st.button("🗑️ Reiniciar Todo el Progreso", type="secondary", use_container_width=True):
                if 'confirm_reset' not in st.session_state:
                    st.session_state.confirm_reset = False
                st.session_state.confirm_reset = True
            
            # Confirmación de reinicio
            if st.session_state.get('confirm_reset', False):
                st.warning("⚠️ **¿Estás seguro?** Esta acción eliminará:")
                st.markdown("""
                - ✅ Todos los ejercicios completados
                - 📅 Todo el historial del calendario
                - 📊 Todas las estadísticas y rachas
                - 🏆 El progreso de las 20 semanas
                """)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Sí, Reiniciar", type="primary", use_container_width=True):
                        self.reset_all_progress()
                        st.session_state.confirm_reset = False
                        st.rerun()
                
                with col2:
                    if st.button("❌ Cancelar", use_container_width=True):
                        st.session_state.confirm_reset = False
                        st.rerun()
            
            return show_videos, show_instructions, show_tips
    
    def render_tabs(self):
        """Renderizar pestañas principales"""
        tab1, tab2, tab3, tab4 = st.tabs([
            "🏋️ Plan de Entrenamiento", 
            "📊 Progreso", 
            "📈 Estadísticas",
            "ℹ️ Información"
        ])
        
        return tab1, tab2, tab3, tab4
    
    def run(self):
        """Ejecutar la aplicación principal"""
        try:
            # Renderizar cabecera
            self.render_header()
            
            # Sincronizar datos antes de renderizar
            self._sync_modules()
            
            # Renderizar barra lateral y obtener configuraciones
            show_videos, show_instructions, show_tips = self.render_sidebar()
            
            # Renderizar pestañas principales
            tab1, tab2, tab3, tab4 = self.render_tabs()
            
            with tab1:
                # Pestaña de Plan de Entrenamiento
                self.training_module.render_training_plan(show_videos, show_instructions, show_tips)
            
            with tab2:
                # Pestaña de Progreso y Calendario
                self.progress_module.render_progress_tab()
            
            with tab3:
                # Pestaña de Estadísticas
                self.statistics_module.render_statistics_tab()
            
            with tab4:
                # Pestaña de Información
                self.info_module.render_info_tab()
            
            # Sincronizar datos después de renderizar (por si hubo cambios)
            self._sync_modules()
            
            # Pie de página
            st.markdown("---")
            st.markdown(
                "💪 **Sudoraciones Propias** - Sistema de Entrenamiento Personal  \n"
                "🚀 Desarrollado con ☕ Python & Streamlit  \n"
                "**Creado por entreunosyceros**",
                unsafe_allow_html=False
            )
            
        except Exception as e:
            st.error(f"❌ Error en la aplicación: {str(e)}")
            st.exception(e)


# Ejecutar la aplicación
if __name__ == "__main__":
    try:
        app = ModernHeavyDutyTrainer()
        app.run()
    except Exception as e:
        st.error(f"❌ Error crítico al inicializar la aplicación: {str(e)}")
        st.exception(e)
