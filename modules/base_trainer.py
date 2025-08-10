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
        
        # Invalidar cache para asegurar datos frescos
        if hasattr(st, 'cache_data'):
            st.cache_data.clear()
    
    # --- NUEVO: Utilidades para alternar antebrazos y progresión por nivel ---
    def _get_forearm_exercises(self) -> list[dict]:
        exercises = self.config.get('exercises', {}).get('brazos', [])
        return [e for e in exercises if e.get('category') == 'forearm']
    
    def _choose_forearm_exercise_name(self, day_key: str, week_number: int) -> str | None:
        forearms = self._get_forearm_exercises()
        if not forearms:
            return None
        # Rotación determinística por semana y día (0=lun..6=dom)
        day_names = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        day_idx = day_names.index(day_key) if day_key in day_names else 0
        idx = ((week_number - 1) * 7 + day_idx) % len(forearms)
        return forearms[idx]['name']
    
    def _get_level_for_week(self, week_number: int) -> int:
        info = self.get_week_info(week_number)
        return info.get('level', 1)
    
    def get_forearm_progression(self, level: int) -> tuple[int, str]:
        """Progresión para antebrazos según nivel"""
        if level <= 1:
            return 1, '8-10'
        if level == 2:
            return 1, '10-12'
        if level == 3:
            return 2, '10-12'
        # nivel 4+
        return 2, '12-15'
    
    def get_planned_exercises_for_group(self, muscle_group: str, day_key: str, week_number: int) -> list[dict]:
        """Devolver ejercicios planificados aplicando alternancia de antebrazos en 'brazos'"""
        all_ex = self.config.get('exercises', {}).get(muscle_group, [])
        if muscle_group != 'brazos':
            return all_ex
        # En brazos: mantener todos menos los de antebrazo, y añadir solo 1 de antebrazo seleccionado
        non_forearm = [e for e in all_ex if e.get('category') != 'forearm']
        chosen = self._choose_forearm_exercise_name(day_key, week_number)
        if not chosen:
            return all_ex  # no hay antebrazos definidos
        selected_forearm = [e for e in all_ex if e.get('name') == chosen]
        return non_forearm + selected_forearm
    
    # --- FIN utilidades nuevas ---

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
            except Exception as e:
                st.warning(f"Error cargando progress_data.json: {e}")
                # Crear archivo de backup
                backup_name = f"progress_data_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                try:
                    import shutil
                    shutil.copy('progress_data.json', backup_name)
                    st.info(f"Backup creado: {backup_name}")
                except:
                    pass
        
        # Datos por defecto
        current_month = datetime.datetime.now().strftime('%Y-%m')
        default_data = {
            "months": {},
            "current_month": current_month,
            "total_workouts": 0,
            "completed_exercises": {},
            "exercise_weeks": {}
        }
        
        # Crear archivo inicial si no existe
        if not os.path.exists('progress_data.json'):
            self.save_progress_data_internal(default_data)
        
        return default_data

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

    def get_exercise_completion_count(self, muscle_group: str, exercise_name: str) -> int:
        """Contar cuántas veces se ha completado un ejercicio específico (todas las semanas)"""
        count = 0
        if 'completed_exercises' not in self.progress_data:
            return count
        
        for date_str, exercises_day in self.progress_data['completed_exercises'].items():
            for exercise_id, is_completed in exercises_day.items():
                if is_completed:
                    # Formato esperado: muscle_group_exercise_name_day_weekN
                    # Necesitamos extraer grupo y ejercicio, ignorando día y semana
                    parts = exercise_id.split('_')
                    if len(parts) >= 4:  # al menos: grupo_ejercicio_dia_weekN
                        # El grupo muscular es la primera parte
                        id_muscle_group = parts[0]
                        
                        # Buscar dónde termina el nombre del ejercicio y empieza el día
                        day_parts = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
                        
                        # Encontrar el día en el ID
                        day_index = -1
                        for i, part in enumerate(parts):
                            if part in day_parts:
                                day_index = i
                                break
                        
                        if day_index > 1:  # debe haber al menos grupo_ejercicio_dia
                            # Reconstruir el nombre del ejercicio (sin día ni semana)
                            id_exercise_name = '_'.join(parts[1:day_index])
                            
                            # Verificar coincidencia exacta (ignorando semana)
                            if (id_muscle_group == muscle_group and 
                                id_exercise_name == exercise_name):
                                count += 1
        
        return count

    def get_total_exercise_completions(self) -> Dict[str, int]:
        """Obtener el conteo total de completados para todos los ejercicios"""
        completion_counts = {}
        
        for muscle_group, exercises in self.config.get('exercises', {}).items():
            for exercise in exercises:
                exercise_key = f"{muscle_group}_{exercise['name']}"
                completion_counts[exercise_key] = self.get_exercise_completion_count(
                    muscle_group, exercise['name']
                )
        
        return completion_counts

    def save_progress_data(self):
        """Guardar datos de progreso"""
        # Añadir timestamp para debug
        self.progress_data['last_saved'] = datetime.datetime.now().isoformat()
        
        try:
            with open('progress_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.progress_data, f, indent=2, ensure_ascii=False)
            
            # Forzar recarga en streamlit
            if hasattr(st, 'cache_data'):
                st.cache_data.clear()
            
            # Debug: verificar que se guardó correctamente
            if os.path.exists('progress_data.json'):
                file_size = os.path.getsize('progress_data.json')
                if file_size < 50:  # Archivo muy pequeño, posible error
                    st.error(f"⚠️ Advertencia: progress_data.json parece estar corrupto (tamaño: {file_size} bytes)")
                    
        except Exception as e:
            st.error(f"❌ Error guardando progress_data.json: {e}")

    def reload_progress_data(self):
        """Recargar datos de progreso desde archivo"""
        self.progress_data = self.load_progress_data()
        return self.progress_data

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
        
        # Determinar el ID correcto según el formato
        if '_week' in exercise_id:
            # Ya tiene sufijo de semana, usar tal como está
            unique_exercise_id = exercise_id
        else:
            # No tiene sufijo, añadir el de la semana actual
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
                # USAR lista planificada que alterna antebrazos
                planned = self.get_planned_exercises_for_group(muscle_group, day_key, week_number)
                for exercise in planned:
                    exercise_id = f"{muscle_group}_{exercise['name']}_{day_key}_week{week_number}"
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

    def render_exercise_details(self, exercise: Dict[str, Any], muscle_group: str, day_key: str, show_videos: bool, show_instructions: bool, show_tips: bool, week_number: int = None):
        """Renderizar detalles de un ejercicio completo"""
        if week_number is None:
            week_number = st.session_state.get('current_week', 1)
        
        exercise_name = exercise['name']
        exercise_id = f"{muscle_group}_{exercise_name}_{day_key}_week{week_number}"
        
        # Obtener fecha actual para marcar progreso
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        is_completed = self.is_exercise_completed(current_date, exercise_id, week_number)
        
        # Checkbox de completado prominente
        col_checkbox, col_title = st.columns([1, 4])
        with col_checkbox:
            completed = st.checkbox(
                "✅ Marcar",
                value=is_completed,
                key=self.generate_unique_key("exercise_completed", exercise_id, current_date),
                help=f"Marcar {exercise_name} como completado hoy"
            )
            if completed != is_completed:
                self.mark_exercise_completed(current_date, exercise_id, completed, week_number)
                self.reload_progress_data()
                if completed:
                    st.success(f"🎉 ¡{exercise_name} completado!")
                else:
                    st.info(f"📋 {exercise_name} marcado como pendiente")
                st.rerun()
        
        # Progresión dinámica para antebrazos
        display_sets = exercise.get('sets', 1)
        display_reps = exercise.get('reps', '')
        if exercise.get('category') == 'forearm':
            level = self._get_level_for_week(week_number)
            s, r = self.get_forearm_progression(level)
            display_sets, display_reps = s, r
        
        with col_title:
            status_emoji = "✅" if completed else "⭕"
            st.markdown(f"### {status_emoji} {exercise_name}")
            st.markdown(f"**Series:** {display_sets} | **Reps:** {display_reps} | **Grupo:** {muscle_group.title()}")
        
        with st.expander(f"ℹ️ Ver detalles de {exercise_name}", expanded=False):
            # Información del ejercicio
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**📊 Información:**")
                st.write(f"• Series: {display_sets}")
                st.write(f"• Repeticiones: {display_reps}")
                st.write(f"• Grupo Muscular: {muscle_group.title()}")
                
                st.markdown("**📝 Descripción:**")
                st.write(exercise.get('description', ''))
            
            with col2:
                # ...existing code...
                pass

    # --- NUEVOS MÉTODOS: estado de ejercicios y utilidades de YouTube ---
    def is_exercise_completed(self, date_str: str, exercise_id: str, week_number: int | None = None) -> bool:
        """Comprobar si un ejercicio (con sufijo de semana) está marcado como completado para una fecha dada."""
        if 'completed_exercises' not in self.progress_data:
            return False
        if week_number is None:
            week_number = st.session_state.get('current_week', 1)
        day_map = self.progress_data.get('completed_exercises', {}).get(date_str, {})
        
        # Determinar el ID correcto según el formato
        if '_week' in exercise_id:
            # Ya tiene sufijo de semana, usar tal como está
            unique_id = exercise_id
        else:
            # No tiene sufijo, añadir el de la semana actual
            unique_id = f"{exercise_id}_week{week_number}"
        
        # Buscar ÚNICAMENTE el ID con sufijo de semana específico (formato actual)
        if unique_id in day_map:
            return bool(day_map.get(unique_id))
        
        # Compatibilidad SOLO para formato antiguo sin sufijos (no buscar otras semanas)
        base_id = exercise_id.replace(f"_week{week_number}", "") if '_week' in exercise_id else exercise_id
        if base_id in day_map and '_week' not in base_id:
            return bool(day_map.get(base_id))
        
        # NO buscar en otras semanas - garantizar independencia semanal
        return False

    def validate_youtube_url(self, url: str) -> tuple[bool, str]:
        """Validar URL de YouTube. Devuelve (es_valida, tipo)."""
        if not url or not isinstance(url, str):
            return False, 'empty'
        u = url.strip()
        # Tipos soportados
        if 'youtube.com/shorts/' in u:
            return True, 'shorts'
        if 'youtube.com/watch' in u and ('v=' in u or 'list=' in u or 'feature=' in u):
            return True, 'video'
        if 'youtu.be/' in u:
            return True, 'short_url'
        # Aceptar urls de youtube sin query estricta
        if 'youtube.com' in u or 'youtu.be' in u:
            return True, 'video'
        return False, 'invalid'

    def render_youtube_video(self, url: str):
        """Renderizar video de YouTube (acepta watch, shorts y youtu.be)."""
        if not url:
            return
        # Streamlit soporta directamente st.video con URLs de YouTube
        try:
            st.video(url)
        except Exception as e:
            st.warning(f"No se pudo renderizar el video: {e}")

    def update_exercise_youtube_url(self, muscle_group: str, exercise_name: str, new_url: str) -> bool:
        """Actualizar la URL de YouTube de un ejercicio tanto en memoria como en config.json"""
        try:
            exercises = self.config.get('exercises', {}).get(muscle_group, [])
            updated = False
            for ex in exercises:
                if ex.get('name') == exercise_name:
                    ex['youtube_url'] = new_url
                    updated = True
                    break
            if not updated:
                st.error("Ejercicio no encontrado en la configuración")
                return False
            # Guardar en disco
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            # Limpiar cache para reflejar cambios
            if hasattr(st, 'cache_data'):
                st.cache_data.clear()
            return True
        except Exception as e:
            st.error(f"No se pudo actualizar la URL: {e}")
            return False
