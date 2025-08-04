"""
Módulo base del entrenamiento
Contiene la funcionalidad core del sistema
"""
import json
import os
import datetime
import hashlib
from typing import Dict, List, Any
import streamlit as st


class BaseTrainer:
    """Clase base con funcionalidad core del sistema"""
    
    def __init__(self):
        """Inicializar la aplicación"""
        self.config = self.load_config()
        self.progress_data = self.load_progress_data()
        
        # Configurar estado de sesión
        if 'current_week' not in st.session_state:
            st.session_state.current_week = 1
        if 'current_tab' not in st.session_state:
            st.session_state.current_tab = 0

    def load_config(self) -> Dict[str, Any]:
        """Cargar configuración desde config.json"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            st.error("❌ Archivo config.json no encontrado")
            return {}
        except json.JSONDecodeError:
            st.error("❌ Error al leer config.json")
            return {}

    def load_progress_data(self) -> Dict[str, Any]:
        """Cargar datos de progreso"""
        if os.path.exists('progress_data.json'):
            try:
                with open('progress_data.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Datos por defecto
        current_month = datetime.datetime.now().strftime('%Y-%m')
        return {
            "months": {},
            "current_month": current_month,
            "total_workouts": 0
        }

    def save_progress_data(self):
        """Guardar datos de progreso"""
        with open('progress_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.progress_data, f, indent=2, ensure_ascii=False)

    def generate_unique_key(self, *args) -> str:
        """Generar clave única basada en argumentos"""
        key_string = "_".join(str(arg) for arg in args)
        hash_suffix = hashlib.md5(key_string.encode()).hexdigest()[:8]
        return f"{key_string}_{hash_suffix}"

    def get_week_info(self, week_number: int) -> Dict[str, Any]:
        """Obtener información sobre la semana y el nivel"""
        level = (week_number - 1) // 4 + 1
        week_in_cycle = (week_number - 1) % 4 + 1
        
        level_names = {
            1: "🟢 Principiante",
            2: "🟡 Intermedio",
            3: "🟠 Avanzado",
            4: "🔴 Experto"
        }
        
        level_descriptions = {
            1: "Plan básico - 3 entrenamientos, 4 días de descanso",
            2: "Incremento de frecuencia - 4 entrenamientos, 3 días de descanso",
            3: "Incremento de volumen - 5 entrenamientos, 2 días de descanso",
            4: "Plan avanzado completo - 6 entrenamientos, 1 día de descanso"
        }
        
        return {
            "level": level,
            "level_name": level_names.get(level, f"🔥 Maestro {level-3}"),
            "level_description": level_descriptions.get(level, "Plan de élite personalizado"),
            "week_in_cycle": week_in_cycle,
            "total_weeks_completed": week_number - 1
        }

    def mark_exercise_completed(self, date_str: str, exercise_id: str, completed: bool):
        """Marcar ejercicio específico como completado"""
        if 'completed_exercises' not in self.progress_data:
            self.progress_data['completed_exercises'] = {}
        
        if date_str not in self.progress_data['completed_exercises']:
            self.progress_data['completed_exercises'][date_str] = {}
        
        self.progress_data['completed_exercises'][date_str][exercise_id] = completed
        
        # Recalcular días completados automáticamente
        self.update_completed_workouts()
        self.save_progress_data()

    def is_exercise_completed(self, date_str: str, exercise_id: str) -> bool:
        """Verificar si un ejercicio está completado en una fecha"""
        if 'completed_exercises' not in self.progress_data:
            return False
        
        return self.progress_data['completed_exercises'].get(date_str, {}).get(exercise_id, False)

    def update_exercise_youtube_url(self, muscle_group: str, exercise_name: str, youtube_url: str) -> bool:
        """Actualizar la URL de YouTube de un ejercicio específico"""
        try:
            # Buscar el ejercicio en la configuración
            if muscle_group in self.config['exercises']:
                for exercise in self.config['exercises'][muscle_group]:
                    if exercise['name'] == exercise_name:
                        exercise['youtube_url'] = youtube_url
                        
                        # Guardar la configuración actualizada
                        with open('config.json', 'w', encoding='utf-8') as f:
                            json.dump(self.config, f, indent=2, ensure_ascii=False)
                        return True
            return False
        except Exception as e:
            st.error(f"Error al actualizar URL: {e}")
            return False

    def extract_video_id(self, url: str) -> str:
        """Extraer ID de video de diferentes formatos de URL de YouTube"""
        if 'youtube.com/watch?v=' in url:
            return url.split('watch?v=')[1].split('&')[0]
        elif 'youtu.be/' in url:
            return url.split('youtu.be/')[1].split('?')[0]
        elif 'youtube.com/shorts/' in url:
            return url.split('shorts/')[1].split('?')[0]
        return ""

    def validate_youtube_url(self, url: str) -> tuple[bool, str]:
        """Validar y clasificar URLs de YouTube"""
        if not url.strip():
            return True, "empty"
        
        url = url.strip()
        
        if 'youtube.com/watch?v=' in url:
            try:
                video_id = url.split('watch?v=')[1].split('&')[0]
                if len(video_id) == 11:
                    return True, "video"
            except:
                pass
        elif 'youtu.be/' in url:
            try:
                video_id = url.split('youtu.be/')[1].split('?')[0]
                if len(video_id) == 11:
                    return True, "short_url"
            except:
                pass
        elif 'youtube.com/shorts/' in url:
            try:
                video_id = url.split('shorts/')[1].split('?')[0]
                if len(video_id) == 11:
                    return True, "shorts"
            except:
                pass
        
        return False, "invalid"

    def render_youtube_video(self, url: str) -> None:
        """Renderizar video de YouTube con soporte optimizado para Shorts"""
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                st.error("No se pudo extraer el ID del video")
                return
                
            if 'youtube.com/shorts/' in url:
                # Para YouTube Shorts, usar iframe optimizado
                embed_url = f"https://www.youtube.com/embed/{video_id}"
                st.markdown(f"""
                <div style="display: flex; justify-content: center; margin: 20px 0;">
                    <div style="position: relative; width: 100%; max-width: 400px; height: 500px; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                        <iframe 
                            src="{embed_url}" 
                            width="100%" 
                            height="100%" 
                            frameborder="0" 
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                            allowfullscreen
                            style="border-radius: 15px;">
                        </iframe>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.success("📱 YouTube Short cargado")
            else:
                # Para videos normales, usar st.video
                st.video(url)
                st.info("🎥 Video cargado")
                
        except Exception as e:
            st.error(f"Error al cargar el video: {str(e)}")
            st.markdown(f"[Ver en YouTube]({url})")
