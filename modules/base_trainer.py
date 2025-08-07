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
                    data = json.load(f)
                # Migrar datos antiguos que no tienen exercise_weeks
                self.migrate_progress_data(data)
                return data
            except:
                pass
        
        # Datos por defecto
        current_month = datetime.datetime.now().strftime('%Y-%m')
        return {
            "months": {},
            "current_month": current_month,
            "total_workouts": 0
        }

    def migrate_progress_data(self, data: Dict[str, Any]):
        """Migrar datos de progreso antiguos para añadir información de semanas"""
        # Si ya tiene exercise_weeks, no necesita migración
        if 'exercise_weeks' in data:
            return
        
        # Inicializar exercise_weeks
        data['exercise_weeks'] = {}
        
        # Para los datos existentes, asumiremos que fueron marcados en la semana 1
        # El usuario puede corregir esto manualmente si es necesario
        if 'completed_exercises' in data:
            for date_str in data['completed_exercises'].keys():
                # Intentar determinar la semana más probable basándose en los ejercicios
                data['exercise_weeks'][date_str] = 1  # Valor por defecto
        
        # Guardar la migración
        self.save_progress_data_internal(data)

    def save_progress_data_internal(self, data: Dict[str, Any]):
        """Método interno para guardar datos específicos (usado en migración)"""
        with open('progress_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

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
            1: "Plan básico - 4 entrenamientos, 3 días de descanso",
            2: "Incremento de frecuencia - 5 entrenamientos, 2 días de descanso",
            3: "Incremento de volumen - 5 entrenamientos intensificados, 2 días de descanso",
            4: "Plan avanzado completo - 6 entrenamientos, 1 día de descanso"
        }
        
        return {
            "level": level,
            "level_name": level_names.get(level, f"🔥 Maestro {level-3}"),
            "level_description": level_descriptions.get(level, "Plan de élite personalizado"),
            "week_in_cycle": week_in_cycle,
            "total_weeks_completed": week_number - 1
        }

    def mark_exercise_completed(self, date_str: str, exercise_id: str, completed: bool, week_number: int = None):
        """Marcar ejercicio específico como completado"""
        if 'completed_exercises' not in self.progress_data:
            self.progress_data['completed_exercises'] = {}
        
        if date_str not in self.progress_data['completed_exercises']:
            self.progress_data['completed_exercises'][date_str] = {}
        
        # Si no se proporciona week_number, usar la semana actual
        if week_number is None:
            week_number = st.session_state.get('current_week', 1)
        
        # Crear ID único que incluya la semana
        unique_exercise_id = f"{exercise_id}_week{week_number}"
        
        self.progress_data['completed_exercises'][date_str][unique_exercise_id] = completed
        
        # Guardar la semana en la que se marcó este ejercicio para futura referencia
        if 'exercise_weeks' not in self.progress_data:
            self.progress_data['exercise_weeks'] = {}
        
        if date_str not in self.progress_data['exercise_weeks']:
            self.progress_data['exercise_weeks'][date_str] = week_number
        
        # Solo actualizar la semana si es la primera vez que se marca algo en esta fecha
        # o si estamos marcando como completado (no desmarcando)
        if completed or date_str not in self.progress_data['exercise_weeks']:
            self.progress_data['exercise_weeks'][date_str] = week_number
        
        # Recalcular días completados automáticamente
        self.update_completed_workouts()
        self.save_progress_data()

    def update_completed_workouts(self):
        """Actualizar la lista de días completados basándose en ejercicios marcados"""
        if 'completed_exercises' not in self.progress_data:
            return
        
        if 'completed_workouts' not in self.progress_data:
            self.progress_data['completed_workouts'] = {}
        
        # Revisar cada fecha con ejercicios registrados
        for date_str in self.progress_data['completed_exercises'].keys():
            # Obtener semana para esta fecha
            week_number = self.progress_data.get('exercise_weeks', {}).get(date_str, 1)
            
            # Calcular estadísticas de completado para este día
            stats = self.get_day_completion_stats_internal(date_str, week_number)
            
            # Considerar el día como completado si tiene ≥80% de ejercicios realizados
            # o si es un día de descanso
            is_completed = stats['is_rest_day'] or stats['percentage'] >= 80
            
            # Obtener clave del mes
            month_key = date_str[:7]  # YYYY-MM
            
            if month_key not in self.progress_data['completed_workouts']:
                self.progress_data['completed_workouts'][month_key] = []
            
            # Añadir o remover de la lista según el estado
            if is_completed and date_str not in self.progress_data['completed_workouts'][month_key]:
                self.progress_data['completed_workouts'][month_key].append(date_str)
            elif not is_completed and date_str in self.progress_data['completed_workouts'][month_key]:
                self.progress_data['completed_workouts'][month_key].remove(date_str)
    
    def get_day_completion_stats_internal(self, date_str: str, week_number: int) -> Dict[str, Any]:
        """Método interno para calcular estadísticas de completado de un día"""
        # Obtener plan del día
        week_info = self.get_week_info(week_number)
        
        if week_number <= 4:
            week_key = f"semana{week_number}"
            if week_key not in self.config.get('weekly_schedule', {}):
                return {'completed': 0, 'total': 0, 'percentage': 100, 'exercises': [], 'muscle_groups': [], 'is_rest_day': True}
            week_plan = self.config['weekly_schedule'][week_key]
        else:
            # Para semanas avanzadas, necesitamos importar el módulo training_plan
            try:
                from .training_plan import TrainingPlanModule
                trainer = TrainingPlanModule()
                trainer.config = self.config
                trainer.progress_data = self.progress_data
                week_plan = trainer.generate_advanced_week(week_number)
            except:
                return {'completed': 0, 'total': 0, 'percentage': 100, 'exercises': [], 'muscle_groups': [], 'is_rest_day': True}
        
        # Determinar día de la semana
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        day_names = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        day_key = day_names[date_obj.weekday()]
        
        muscle_groups = week_plan.get(day_key, [])
        
        # Si no hay grupos musculares programados, es día de descanso
        if not muscle_groups:
            return {'completed': 0, 'total': 0, 'percentage': 100, 'exercises': [], 'muscle_groups': [], 'is_rest_day': True}
        
        total_exercises = 0
        completed_exercises = 0
        exercise_list = []
        
        for muscle_group in muscle_groups:
            if muscle_group in self.config.get('exercises', {}):
                for exercise in self.config['exercises'][muscle_group]:
                    exercise_id = f"{muscle_group}_{exercise['name']}_{day_key}"
                    is_completed = self.is_exercise_completed(date_str, exercise_id, week_number)
                    
                    exercise_list.append({
                        'name': exercise['name'],
                        'muscle_group': muscle_group,
                        'completed': is_completed
                    })
                    
                    total_exercises += 1
                    if is_completed:
                        completed_exercises += 1
        
        percentage = (completed_exercises / total_exercises * 100) if total_exercises > 0 else 100
        
        return {
            'completed': completed_exercises,
            'total': total_exercises,
            'percentage': percentage,
            'exercises': exercise_list,
            'muscle_groups': muscle_groups,
            'is_rest_day': False
        }

    def is_exercise_completed(self, date_str: str, exercise_id: str, week_number: int = None) -> bool:
        """Verificar si un ejercicio está completado en una fecha específica"""
        if 'completed_exercises' not in self.progress_data:
            return False
        
        # Si no se proporciona week_number, usar la semana actual
        if week_number is None:
            week_number = st.session_state.get('current_week', 1)
        
        # Crear ID único que incluya la semana
        unique_exercise_id = f"{exercise_id}_week{week_number}"
        
        return self.progress_data['completed_exercises'].get(date_str, {}).get(unique_exercise_id, False)

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
