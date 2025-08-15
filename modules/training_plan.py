"""
Módulo del Plan de Entrenamiento
Contiene toda la lógica de la pestaña de entrenamiento
"""
import datetime
from typing import Dict, List, Any
import streamlit as st
from .base_trainer import BaseTrainer


class TrainingPlanModule(BaseTrainer):
    """Módulo para gestionar el plan de entrenamiento"""

    def get_day_completion_stats(self, date_str: str, week_number: int) -> Dict[str, Any]:
        """Obtener estadísticas de finalización para un día específico"""
        # Obtener plan del día
        week_info = self.get_week_info(week_number)
        
        if week_number <= 4:
            week_key = f"semana{week_number}"
            if week_key not in self.config.get('weekly_schedule', {}):
                return {'completed': 0, 'total': 0, 'percentage': 100, 'exercises': [], 'muscle_groups': [], 'is_rest_day': True}
            week_plan = self.config['weekly_schedule'][week_key]
        else:
            week_plan = self.generate_advanced_week(week_number)
        
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
                planned = self.get_planned_exercises_for_group(muscle_group, day_key, week_number)
                for exercise in planned:
                    exercise_id = f"{muscle_group}_{exercise['name']}_{day_key}_week{week_number}"
                    is_completed = self.is_exercise_completed(date_str, exercise_id, week_number)
                    
                    # Progresión dinámica para antebrazos (mostrar en reps/series si aplica)
                    display_sets = exercise.get('sets', 1)
                    display_reps = exercise.get('reps', '')
                    if exercise.get('category') == 'forearm':
                        level = self.get_week_info(week_number).get('level', 1)
                        s, r = self.get_forearm_progression(level)
                        display_sets, display_reps = s, r
                    
                    exercise_list.append({
                        'name': exercise['name'],
                        'muscle_group': muscle_group,
                        'completed': is_completed,
                        'sets': display_sets,
                        'reps': display_reps
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

    def get_week_completion_stats(self, week_number: int) -> Dict[str, Any]:
        """Obtener estadísticas de finalización para una semana específica"""
        week_dates = self.get_week_dates(week_number)
        if not week_dates or 'dates' not in week_dates:
            return {'completed': 0, 'total': 0, 'percentage': 0, 'days': []}
        
        total_exercises = 0
        completed_exercises = 0
        day_stats = []
        
        for date_str in week_dates['dates']:
            # Recalcular stats en tiempo real para asegurar datos actualizados
            self.reload_progress_data()
            day_stat = self.get_day_completion_stats(date_str, week_number)
            day_stats.append({
                'date': date_str,
                'completed': day_stat['completed'],
                'total': day_stat['total'],
                'percentage': day_stat['percentage'],
                'is_rest_day': day_stat['is_rest_day']
            })
            
            total_exercises += day_stat['total']
            completed_exercises += day_stat['completed']
        
        percentage = (completed_exercises / total_exercises * 100) if total_exercises > 0 else 100
        
        return {
            'completed': completed_exercises,
            'total': total_exercises,
            'percentage': percentage,
            'days': day_stats
        }

    def get_newly_unlocked_exercises(self, week_number: int) -> Dict[str, List[Dict]]:
        """Obtener ejercicios que se han desbloqueado en la semana actual"""
        current_level = (week_number - 1) // 4 + 1
        previous_level = max(1, current_level - 1)
        
        # Si es la primera semana del nivel, mostrar ejercicios nuevos
        week_in_cycle = (week_number - 1) % 4 + 1
        if week_in_cycle != 1:
            return {}
        
        newly_unlocked = {}
        
        for muscle_group, exercises in self.config.get('exercises', {}).items():
            new_exercises = []
            for exercise in exercises:
                exercise_level = exercise.get('difficulty_level', 1)
                if exercise_level == current_level and exercise_level > previous_level:
                    new_exercises.append(exercise)
            
            if new_exercises:
                newly_unlocked[muscle_group] = new_exercises
        
        return newly_unlocked

    def get_week_number_for_date(self, date_str: str) -> int:
        """Determinar qué número de semana corresponde a una fecha específica"""
        # Primero, verificar si tenemos la semana guardada explícitamente
        if 'exercise_weeks' in self.progress_data and date_str in self.progress_data['exercise_weeks']:
            return self.progress_data['exercise_weeks'][date_str]
        
        # Si la fecha tiene ejercicios registrados, intentar determinar la semana basándose en los IDs de ejercicios
        if 'completed_exercises' in self.progress_data and date_str in self.progress_data['completed_exercises']:
            exercise_ids = list(self.progress_data['completed_exercises'][date_str].keys())
            if exercise_ids:
                # Extraer número de semana de los IDs que tienen formato _weekN
                week_numbers = []
                for exercise_id in exercise_ids:
                    if '_week' in exercise_id:
                        try:
                            week_part = exercise_id.split('_week')[-1]
                            week_num = int(week_part)
                            week_numbers.append(week_num)
                        except (ValueError, IndexError):
                            continue
                
                if week_numbers:
                    # Usar la semana más común en los ejercicios de esa fecha
                    from collections import Counter
                    most_common_week = Counter(week_numbers).most_common(1)[0][0]
                    
                    # Guardar esta información para futura referencia
                    if 'exercise_weeks' not in self.progress_data:
                        self.progress_data['exercise_weeks'] = {}
                    self.progress_data['exercise_weeks'][date_str] = most_common_week
                    self.save_progress_data()
                    return most_common_week
        
        # Fallback: usar la semana actual
        return st.session_state.get('current_week', 1)

    def update_completed_workouts(self):
        """Actualizar lista de entrenamientos completados basándose en ejercicios"""
        if 'completed_exercises' not in self.progress_data:
            self.progress_data['completed_workouts'] = {}
            return
        
        self.progress_data['completed_workouts'] = {}
        total_workouts = 0
        
        # Obtener todas las fechas con ejercicios (completados o no)
        all_dates = set(self.progress_data['completed_exercises'].keys())
        
        # También revisar fechas recientes que podrían ser días de descanso
        today = datetime.datetime.now().date()
        for i in range(30):  # Revisar últimos 30 días
            check_date = today - datetime.timedelta(days=i)
            all_dates.add(check_date.strftime("%Y-%m-%d"))
        
        for date_str in all_dates:
            month_key = date_str[:7]  # YYYY-MM
            
            # Determinar qué semana corresponde a esta fecha específica
            week_for_date = self.get_week_number_for_date(date_str)
            day_stats = self.get_day_completion_stats(date_str, week_for_date)
            
            # Considerar completado si:
            # 1. Es día de descanso (is_rest_day = True), O
            # 2. >= 80% de ejercicios están hechos
            if day_stats.get('is_rest_day', False) or day_stats['percentage'] >= 80:
                if month_key not in self.progress_data['completed_workouts']:
                    self.progress_data['completed_workouts'][month_key] = []
                if date_str not in self.progress_data['completed_workouts'][month_key]:
                    self.progress_data['completed_workouts'][month_key].append(date_str)
                total_workouts += 1
        
        self.progress_data['total_workouts'] = total_workouts

    def generate_advanced_week(self, week_number: int) -> Dict[str, List[str]]:
        """Generar semana avanzada con mayor complejidad"""
        cycle = (week_number - 1) % 4 + 1  # Ciclo de 4 semanas base
        base_schedule = self.config.get('weekly_schedule', {}).get(f'semana{cycle}', {})
        
        # Patrones de progresión basados en el nivel
        level = (week_number - 1) // 4 + 1  # Nivel 1, 2, 3, etc.
        
        if level == 1:  # Semanas 1-4: Plan básico
            return base_schedule
        elif level == 2:  # Semanas 5-8: Incremento de frecuencia
            return self.intensify_schedule(base_schedule, "frequency")
        elif level == 3:  # Semanas 9-12: Incremento de volumen
            return self.intensify_schedule(base_schedule, "volume")
        elif level >= 4:  # Semanas 13+: Plan avanzado completo
            return self.intensify_schedule(base_schedule, "advanced")

    def intensify_schedule(self, base_schedule: Dict[str, List[str]], mode: str) -> Dict[str, List[str]]:
        """Intensificar horario según el modo de progresión"""
        new_schedule = {}
        
        for day, muscle_groups in base_schedule.items():
            if mode == "frequency":
                # Nivel 2: De 3 días descanso → 2 días descanso (agregar martes)
                if day == 'martes' and not muscle_groups:
                    # Convertir martes en día de entrenamiento con cardio
                    new_schedule[day] = ['hombros', 'abs', 'cardio']
                else:
                    new_schedule[day] = muscle_groups
                    
            elif mode == "volume":
                # Nivel 3: Mantener 2 días de descanso (miércoles y domingo), intensificar existentes
                if day == 'martes' and not muscle_groups:
                    # Asegurar que martes tenga entrenamiento del nivel 2 con cardio
                    new_schedule[day] = ['hombros', 'abs', 'cardio']
                elif muscle_groups:  # Intensificar días existentes
                    # Añadir cardio a lunes y sábado si no lo tienen
                    if day in ['lunes', 'sabado'] and 'cardio' not in muscle_groups:
                        new_schedule[day] = muscle_groups + ['cardio']
                    # Añadir un grupo muscular extra a días que ya tienen entrenamiento
                    elif 'abs' not in muscle_groups and len(muscle_groups) < 3:
                        new_schedule[day] = muscle_groups + ['abs']
                    else:
                        new_schedule[day] = muscle_groups
                else:
                    new_schedule[day] = muscle_groups  # Mantener miércoles y domingo como descanso
                    
            elif mode == "advanced":
                # Nivel 4+: Solo 1 día de descanso (domingo) con cardio distribuido
                advanced_plan = {
                    'lunes': ['pecho', 'hombros', 'abs', 'cardio'],
                    'martes': ['espalda', 'brazos', 'cardio'],
                    'miercoles': ['piernas', 'abs', 'cardio'],  # Convierte miércoles en día de entrenamiento
                    'jueves': ['pecho', 'brazos'],
                    'viernes': ['espalda', 'hombros', 'abs'],
                    'sabado': ['piernas', 'gemelos', 'cardio'],
                    'domingo': []  # ÚNICO DÍA DE DESCANSO
                }
                new_schedule = advanced_plan
                break
        
        return new_schedule if mode != "advanced" else new_schedule

    def get_complementary_muscle(self, existing_groups: List[str]) -> List[str]:
        """Obtener grupo muscular complementario"""
        complements = {
            'pecho': ['hombros'],
            'espalda': ['brazos'],
            'hombros': ['pecho'],
            'brazos': ['abs'],
            'piernas': ['abs'],
            'abs': [],
            'cardio': []
        }
        
        for group in existing_groups:
            complement = complements.get(group, [])
            if complement and complement[0] not in existing_groups:
                return complement
        return []

    def get_detailed_instructions(self, exercise_name: str) -> str:
        """Obtener instrucciones detalladas para todos los ejercicios"""
        instructions = {
            # PECHO
            'Press de Banca con Mancuernas': "Acuéstate en el banco, baja las mancuernas lentamente hasta sentir estiramiento en el pecho, empuja hacia arriba con control.",
            'Press de Banca con Barra': "Acostado en el banco, presiona la barra hacia arriba con control total",
            'Aperturas con Mancuernas': "Acostado en el banco, abre los brazos en arco amplio manteniendo codos ligeramente flexionados, baja hasta sentir estiramiento en pecho.",
            'Press Inclinado con Barra': "En banco inclinado, presiona la barra trabajando pecho superior",
            'Flexiones en el Suelo': "Posición de plancha, baja el pecho hasta casi tocar el suelo, mantén el core contraído, empuja hacia arriba.",

            # ESPALDA
            'Remo con Mancuernas': "Torso paralelo al suelo, tira del codo hacia atrás llevando la mancuerna hacia las costillas.",
            'Peso Muerto con Mancuernas': "Pies separados, baja las mancuernas manteniendo la espalda recta, empuja con los talones para subir.",
            'Remo a Una Mano': "Apoyo en banco con una mano, tira de la mancuerna hacia la cadera manteniendo el torso estable.",

            # HOMBROS
            'Press Militar con Mancuernas': "De pie, mancuernas a la altura de los hombros, empuja hacia arriba hasta extensión completa.",
            'Elevaciones Laterales': "De pie, eleva los brazos lateralmente hasta la altura de los hombros con control.",
            'Elevaciones Frontales': "De pie, eleva las mancuernas al frente hasta la altura de los hombros alternando brazos.",
            'Pájaros con Mancuernas': "Inclinado hacia adelante, abre los brazos lateralmente apretando los omóplatos.",

            # BRAZOS
            'Curl de Bíceps': "Brazos extendidos, codos pegados al torso, flexiona llevando las mancuernas hacia los hombros.",
            'Curl Martillo': "Como el curl normal pero con agarre neutro (palmas enfrentadas), movimiento controlado.",
            'Extensiones de Tríceps': "Acostado, codos fijos apuntando al techo, baja la mancuerna hacia la frente flexionando antebrazos.",
            'Fondos en Silla': "Manos en el borde de una silla/banco, codos hacia atrás, baja controlado y sube extendiendo tríceps.",
            'Curl Concentrado': "Sentado, codo apoyado en la pierna, flexiona el brazo con concentración total en el bíceps.",
            'Patada de Tríceps': "Inclinado, brazo superior paralelo al suelo, extiende el antebrazo hacia atrás.",

            # ANTEBRAZOS
            'Curl de Muñeca': "Sentado, antebrazos apoyados, palmas hacia arriba; flexiona solo las muñecas elevando la mancuerna y baja controlado.",
            'Curl de Muñeca Inverso': "Sentado, antebrazos apoyados, palmas hacia abajo; extiende las muñecas elevando el dorso y desciende controlado.",
            'Pronación/Supinación con Mancuerna': "Con codo a 90° y antebrazo estable, rota lentamente la mancuerna entre palma arriba (supinación) y palma abajo (pronación).",

            # PIERNAS
            'Sentadillas con Mancuernas': "Pies separados, baja como si te sentaras en una silla, mantén el pecho erguido.",
            'Zancadas con Mancuernas': "Paso largo adelante, baja hasta que ambas rodillas estén a 90 grados.",
            'Sentadillas Búlgaras': "Un pie elevado atrás, baja con la pierna delantera hasta 90 grados",
            'Peso Muerto Rumano': "Piernas ligeramente flexionadas, baja las mancuernas manteniendo la curva lumbar.",
            'Sentadillas Sumo': "Pies muy separados, puntas hacia afuera, baja manteniendo rodillas alineadas con pies.",

            # GEMELOS
            'Elevaciones de Gemelos de Pie': "De pie con mancuernas, elévate en puntillas contrayendo los gemelos",
            'Elevaciones de Gemelos Sentado': "Sentado en el banco, mancuernas en los muslos, elévate en puntillas",
            'Elevación de Talones': "De pie, elévate sobre las puntas de los pies contrayendo las pantorrillas.",

            # ABDOMINALES
            'Abdominales Tradicionalales': "Acostado, rodillas flexionadas, eleva el torso hacia las rodillas sin tirar del cuello.",
            'Plancha': "Antebrazos en el suelo, cuerpo en línea recta, mantén la posición.",
            'Abdominales Bajas': "Acostado boca arriba, manos bajo la espalda baja, eleva las piernas hacia el pecho manteniendo control.",
            'Abdominales Laterales': "De lado, eleva el torso hacia la cadera, trabajando los oblicuos con movimiento controlado.",
            'Abdominales con Mancuerna': "Acostado, sujeta mancuerna en el pecho, realiza abdominales con peso adicional.",
            'Russian Twists': "Sentado, inclínate hacia atrás, rota el torso de lado a lado con mancuerna.",
            'Plancha Lateral': "De lado, apoyado en antebrazo, mantén el cuerpo recto lateralmente.",

            # CARDIO
            'Bicicleta Estática': "Ajusta el asiento, mantén la espalda recta, pedalea con movimiento fluido."
        }
        return instructions.get(exercise_name, f"Instrucciones para '{exercise_name}' próximamente disponibles.")

    def get_exercise_tips(self, exercise_name: str) -> str:
        """Obtener consejos específicos para todos los ejercicios"""
        tips = {
            # PECHO
            'Press de Banca con Mancuernas': "Mantén los omóplatos retraídos, no arquees excesivamente la espalda. Respiración: inhala al bajar, exhala al subir.",
            'Press de Banca con Barra': "Agarre ligeramente más ancho que los hombros. Baja la barra al pecho controladamente.",
            'Aperturas con Mancuernas': "No bajes demasiado para evitar lesiones en el hombro. Mantén codos ligeramente flexionados siempre.",
            'Press Inclinado con Barra': "Enfócate en la parte superior del pecho. No uses un agarre demasiado ancho.",
            'Flexiones en el Suelo': "Mantén línea recta del cuerpo, si es difícil hazlas de rodillas. Progresa gradualmente.",

            # ESPALDA
            'Remo con Mancuernas': "Inicia el movimiento con los músculos de la espalda, no gires el torso. Aprieta omóplatos al final.",
            'Peso Muerto con Mancuernas': "Mantén la barra cerca del cuerpo, pecho arriba, peso en los talones.",
            'Remo a Una Mano': "Mantén la espalda neutral, no uses impulso. El codo debe ir hacia atrás, no hacia afuera.",

            # HOMBROS
            'Press Militar con Mancuernas': "Core contraído, no uses impulso con las piernas. Cuidado con la posición del cuello.",
            'Elevaciones Laterales': "Movimiento lento y controlado, no uses peso excesivo. Evita balancear el cuerpo.",
            'Elevaciones Frontales': "Alterna los brazos para mejor estabilidad. No subas más allá de la altura del hombro.",
            'Pájaros con Mancuernas': "Mantén rodillas ligeramente flexionadas. Enfócate en apretar los omóplatos.",

            # BRAZOS
            'Curl de Bíceps': "Mantén los codos fijos, no balancees el cuerpo. Contracción completa en la parte superior.",
            'Curl Martillo': "Variación excelente para el braquial. Alterna brazos para mejor concentración.",
            'Extensiones de Tríceps': "Mantén los brazos superiores fijos, cuidado con el peso cerca de la cabeza.",
            'Fondos en Silla': "Hombros abajo y atrás; evita encogerte. No desciendas más de lo cómodo para tus hombros.",
            'Curl Concentrado': "Ideal para máxima concentración. No uses impulso, movimiento muy controlado.",
            'Patada de Tríceps': "Mantén el brazo superior inmóvil. Extensión completa pero sin bloquear agresivamente.",

            # ANTEBRAZOS
            'Curl de Muñeca': "Recorrido corto y controlado, pausa 1s arriba. No flexiones los codos; solo muñecas.",
            'Curl de Muñeca Inverso': "Usa peso moderado, evita compensar con hombros. Controla la bajada.",
            'Pronación/Supinación con Mancuerna': "Coge la mancuerna por un extremo para mayor palanca. Rotación lenta, sin balanceos.",

            # PIERNAS
            'Sentadillas con Mancuernas': "Peso en los talones, no dejes que las rodillas se vayan hacia adentro. Profundidad completa.",
            'Zancadas con Mancuernas': "Mantén el equilibrio, rodilla delantera no debe sobrepasar el pie. Tronco erguido.",
            'Sentadillas Búlgaras': "Mantén el torso erguido. La rodilla de atrás casi toca el suelo.",
            'Peso Muerto Rumano': "Excelente para isquiotibiales. Mantén las mancuernas cerca de las piernas.",
            'Sentadillas Sumo': "Activa los glúteos al subir. Rodillas siguen la dirección de los pies.",

            # GEMELOS
            'Elevaciones de Gemelos de Pie': "Rango de movimiento completo. Estira abajo y contrae arriba.",
            'Elevaciones de Gemelos Sentado': "Enfócate en el sóleo. Pausa en la contracción máxima.",
            'Elevación de Talones': "Pausa 1-2 segundos arriba. Baja controladamente para máximo estiramiento.",

            # ABDOMINALES
            'Abdominales Tradicionales': "El movimiento viene del abdomen, calidad sobre cantidad. No tires del cuello.",
            'Plancha': "Mantén la línea recta, si duele la espalda baja detente. Respira normalmente.",
            'Abdominales Bajas': "Enfócate en la parte baja del abdomen, no uses impulso. Movimiento lento y controlado.",
            'Abdominales Laterales': "Contrae los oblicuos, no hagas movimientos bruscos. Alterna los lados uniformemente.",
            'Abdominales con Mancuerna': "Peso moderado, enfócate en la técnica. Progresa gradualmente.",
            'Russian Twists': "Mantén los pies elevados para mayor dificultad. Control en la rotación.",
            'Plancha Lateral': "Progresa desde rodillas si es necesario. Mantén caderas elevadas.",

            # CARDIO
            'Bicicleta Estática': "Cadencia constante, no te encorves sobre el manillar. Ajusta resistencia gradualmente."
        }
        return tips.get(exercise_name, f"Consejos para '{exercise_name}' próximamente disponibles.")

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
            
            # Actualizar estado si cambió
            if completed != is_completed:
                self.mark_exercise_completed(current_date, exercise_id, completed, week_number)
                
                # Recargar datos para asegurar persistencia
                self.reload_progress_data()
                
                if completed:
                    st.success(f"🎉 ¡{exercise_name} completado!")
                else:
                    st.info(f"📋 {exercise_name} marcado como pendiente")
                st.rerun()
        
        # Mostrar estado y progresión dinámica para antebrazo
        display_sets = exercise.get('sets', 1)
        display_reps = exercise.get('reps', '')
        if exercise.get('category') == 'forearm':
            level = self.get_week_info(week_number).get('level', 1)
            s, r = self.get_forearm_progression(level)
            display_sets, display_reps = s, r
        
        with col_title:
            # Mostrar estado visual del ejercicio
            status_emoji = "✅" if completed else "⭕"
            st.markdown(f"### {status_emoji} {exercise_name}")
            st.markdown(f"**Series:** {display_sets} | **Reps:** {display_reps} | **Grupo:** {muscle_group.title()}")
        
        with st.expander(f"ℹ️ Ver detalles de {exercise_name}", expanded=False):
            # Video de YouTube si está habilitado
            youtube_url = exercise.get('youtube_url', '')
            if youtube_url and show_videos:
                st.markdown("### 🎥 Video Tutorial")
                self.render_youtube_video(youtube_url)
            
            # Editor de URL de YouTube
            st.markdown("### 🔗 Configurar Video Tutorial")
            input_key = self.generate_unique_key("youtube_url", muscle_group, exercise_name, day_key, st.session_state.current_week)
            new_url = st.text_input(
                "URL de YouTube:",
                value=youtube_url,
                key=input_key,
                placeholder="Ej: https://www.youtube.com/shorts/35_gCUE3SmM"
            )
            
            # Validación en tiempo real
            if new_url.strip():
                is_valid, url_type = self.validate_youtube_url(new_url)
                if is_valid:
                    if url_type == "shorts":
                        st.success("✅ YouTube Short válido")
                    elif url_type == "video":
                        st.success("✅ Video de YouTube válido")
                    elif url_type == "short_url":
                        st.success("✅ URL corta válida")
                    elif url_type == "empty":
                        st.info("ℹ️ URL vacía")
                else:
                    st.error("❌ URL no válida")
            
            # Botón para guardar URL
            button_key = self.generate_unique_key("save_url", muscle_group, exercise_name, day_key, st.session_state.current_week)
            if st.button(f"💾 Guardar URL", key=button_key):
                is_valid, url_type = self.validate_youtube_url(new_url)
                if is_valid:
                    if self.update_exercise_youtube_url(muscle_group, exercise_name, new_url):
                        st.success("✅ URL guardada correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al guardar")
                else:
                    st.error("❌ URL no válida")
            
            # Información del ejercicio
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**📊 Información:**")
                st.write(f"• Series: {display_sets}")
                st.write(f"• Repeticiones: {display_reps}")
                st.write(f"• Grupo Muscular: {muscle_group.title()}")
                
                st.markdown("**📝 Descripción:**")
                st.write(exercise['description'])
            
            with col2:
                if show_instructions:
                    instructions = self.get_detailed_instructions(exercise_name)
                    st.markdown("**🎯 Instrucciones:**")
                    st.write(instructions)
                
                if show_tips:
                    tips = self.get_exercise_tips(exercise_name)
                    st.markdown("**💡 Consejos:**")
                    st.write(tips)

    def render_training_plan(self, show_videos: bool, show_instructions: bool, show_tips: bool):
        """Renderizar plan de entrenamiento completo"""
        current_week = st.session_state.current_week
        
        # Obtener información del nivel y semana
        week_info = self.get_week_info(current_week)
        
        # Generar plan de la semana (básico o avanzado)
        if current_week <= 4:
            week_key = f"semana{current_week}"
            if 'weekly_schedule' not in self.config or week_key not in self.config['weekly_schedule']:
                st.error(f"❌ No se encontró configuración para {week_key}")
                return
            week_plan = self.config['weekly_schedule'][week_key]
        else:
            # Generar semana avanzada automáticamente
            week_plan = self.generate_advanced_week(current_week)
        
        # Mostrar información de la semana actual
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info(f"📅 **Semana {current_week}** - {week_info['level_name']}")
        with col2:
            if current_week > 4:
                st.success(f"🎉 ¡Progresión automática activa!")
        
        st.markdown(f"*{week_info['level_description']}*")
        
        # Panel de información del nivel
        st.markdown("### 🎯 Información del Nivel")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nivel Actual", week_info['level_name'])
        with col2:
            st.metric("Semana en Ciclo", f"{week_info['week_in_cycle']}/4")
        with col3:
            st.metric("Semanas Completadas", week_info['total_weeks_completed'])
        
        st.markdown(f"**{week_info['level_description']}**")
        
        # Mostrar ejercicios desbloqueados
        new_exercises = self.get_newly_unlocked_exercises(current_week)
        if new_exercises:
            with st.expander("🆕 Nuevos ejercicios desbloqueados", expanded=True):
                for muscle_group, exercises in new_exercises.items():
                    if exercises:
                        st.markdown(f"**💪 {muscle_group.title()}:**")
                        for exercise in exercises:
                            difficulty_emoji = ["", "🟢", "🟡", "🟠", "🔴"][exercise.get('difficulty_level', 1)]
                            st.markdown(f"  • {difficulty_emoji} {exercise['name']}")
        
        # Mostrar progreso si es una semana avanzada
        if current_week > 4:
            progress_bar = min(week_info['week_in_cycle'] / 4, 1.0)
            st.progress(progress_bar, text=f"Progreso en nivel actual: {week_info['week_in_cycle']}/4 semanas")
        
        # Panel de progreso diario
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        # Recargar progreso para asegurar datos actualizados
        self.reload_progress_data()
        day_stats = self.get_day_completion_stats(current_date, current_week)
        
        if day_stats['total'] > 0:
            st.markdown("### 📊 Progreso de Hoy")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Ejercicios Completados", day_stats['completed'], f"de {day_stats['total']}")
            with col2:
                progress_percentage = day_stats['percentage']
                st.metric("Progreso del Día", f"{progress_percentage:.1f}%")
            with col3:
                remaining = day_stats['total'] - day_stats['completed']
                st.metric("Pendientes", remaining, f"{-remaining}" if remaining > 0 else "0")
            with col4:
                if progress_percentage >= 80:
                    st.metric("Estado", "🎉 Completado", "¡Excelente!")
                elif progress_percentage >= 50:
                    st.metric("Estado", "👍 En progreso", "¡Sigue así!")
                else:
                    st.metric("Estado", "💪 Iniciando", "¡Vamos!")
            
            # Barra de progreso del día
            st.progress(progress_percentage / 100, text=f"Progreso diario: {progress_percentage:.0f}%")
            
            # Lista rápida de ejercicios pendientes
            pending_exercises = [ex for ex in day_stats['exercises'] if not ex['completed']]
            if pending_exercises:
                with st.expander(f"📋 Ejercicios pendientes ({len(pending_exercises)})", expanded=False):
                    for ex in pending_exercises:
                        st.markdown(f"• **{ex['name']}** ({ex['muscle_group'].title()})")
        
        # Panel de progreso semanal
        st.markdown("### 📈 Progreso de la Semana")
        week_stats = self.get_week_completion_stats(current_week)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Ejercicios Completados", week_stats['completed'], f"de {week_stats['total']}")
        with col2:
            week_percentage = week_stats['percentage']
            st.metric("Progreso de la Semana", f"{week_percentage:.1f}%")
        with col3:
            week_remaining = week_stats['total'] - week_stats['completed']
            st.metric("Pendientes", week_remaining, f"{-week_remaining}" if week_remaining > 0 else "0")
        with col4:
            if week_percentage >= 80:
                st.metric("Estado", "🎉 Excelente", "¡Casi completada!")
            elif week_percentage >= 50:
                st.metric("Estado", "👍 Buen ritmo", "¡Sigue así!")
            else:
                st.metric("Estado", "💪 En marcha", "¡A por ello!")
        
        # Barra de progreso de la semana
        st.progress(week_percentage / 100, text=f"Progreso semanal: {week_percentage:.0f}%")
        
        # Mostrar progreso por días de la semana
        with st.expander("📅 Detalle por días", expanded=False):
            day_names_full = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            for i, day_stat in enumerate(week_stats['days']):
                if day_stat['is_rest_day']:
                    st.markdown(f"**{day_names_full[i]}**: 🛌 Día de descanso")
                else:
                    completion_text = f"{day_stat['completed']}/{day_stat['total']} ejercicios ({day_stat['percentage']:.1f}%)"
                    status_emoji = "✅" if day_stat['percentage'] >= 80 else "🔄" if day_stat['percentage'] > 0 else "⏳"
                    st.markdown(f"**{day_names_full[i]}**: {status_emoji} {completion_text}")
        
        st.markdown("---")
        
        # Obtener las fechas de la semana actual
        week_dates = self.get_week_dates(current_week)
        dates_list = week_dates.get('dates', []) if week_dates else []
        
        day_names = {
            'lunes': '🟢 LUNES',
            'martes': '🔵 MARTES', 
            'miercoles': '🟡 MIÉRCOLES',
            'jueves': '🟠 JUEVES',
            'viernes': '🔴 VIERNES',
            'sabado': '🟣 SÁBADO',
            'domingo': '⚪ DOMINGO'
        }
        
        day_order = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        
        for day_index, day_key in enumerate(day_order):
            muscle_groups = week_plan.get(day_key, [])
            day_display = day_names.get(day_key, day_key.upper())
            
            # Agregar la fecha del día si está disponible
            if day_index < len(dates_list):
                # Formatear la fecha de YYYY-MM-DD a DD-MM-YYYY
                try:
                    date_obj = datetime.datetime.strptime(dates_list[day_index], '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%d-%m-%Y')
                    day_display_with_date = f"{day_display} - {formatted_date}"
                except:
                    day_display_with_date = day_display
            else:
                day_display_with_date = day_display
            
            st.markdown(f"### {day_display_with_date}")
            
            if not muscle_groups:  # Día de descanso
                st.markdown("""
                <div class="rest-day">
                    <h3>🛌 Día de descanso 🛌</h3>
                    <p>Recuperación activa - Estiramiento ligero, caminata o yoga</p>
                </div>
                """, unsafe_allow_html=True)
                continue
            
            for muscle_group in muscle_groups:
                if muscle_group in self.config['exercises']:
                    st.markdown(f"#### 💪 {muscle_group.title()}")
                    
                    # USAR lista planificada (1 ejercicio de antebrazo alternado)
                    planned_list = self.get_planned_exercises_for_group(muscle_group, day_key, current_week)
                    for exercise in planned_list:
                        self.render_exercise_details(exercise, muscle_group, day_key, show_videos, show_instructions, show_tips, current_week)