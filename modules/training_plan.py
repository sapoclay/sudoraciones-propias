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
                for exercise in self.config['exercises'][muscle_group]:
                    exercise_id = f"{muscle_group}_{exercise['name']}_{day_key}"
                    is_completed = self.is_exercise_completed(date_str, exercise_id)
                    
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
            
            # Obtener estadísticas del día (usar semana actual por defecto)
            current_week = st.session_state.get('current_week', 1)
            day_stats = self.get_day_completion_stats(date_str, current_week)
            
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
                    # Convertir martes en día de entrenamiento
                    new_schedule[day] = ['hombros', 'abs']
                else:
                    new_schedule[day] = muscle_groups
                    
            elif mode == "volume":
                # Nivel 3: Mantener 2 días de descanso (miércoles y domingo), intensificar existentes
                if day == 'martes' and not muscle_groups:
                    # Asegurar que martes tenga entrenamiento del nivel 2
                    new_schedule[day] = ['hombros', 'abs', 'cardio']
                elif muscle_groups:  # Intensificar días existentes
                    # Añadir un grupo muscular extra a días que ya tienen entrenamiento
                    if 'abs' not in muscle_groups and len(muscle_groups) < 3:
                        new_schedule[day] = muscle_groups + ['abs']
                    else:
                        new_schedule[day] = muscle_groups
                else:
                    new_schedule[day] = muscle_groups  # Mantener miércoles y domingo como descanso
                    
            elif mode == "advanced":
                # Nivel 4+: Solo 1 día de descanso (domingo)
                advanced_plan = {
                    'lunes': ['pecho', 'hombros', 'abs'],
                    'martes': ['espalda', 'brazos'],
                    'miercoles': ['piernas', 'abs'],  # Convierte miércoles en día de entrenamiento
                    'jueves': ['pecho', 'brazos'],
                    'viernes': ['espalda', 'hombros', 'abs'],
                    'sabado': ['piernas', 'cardio'],
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
            'Aperturas con Mancuernas': "Acostado en el banco, abre los brazos en arco amplio manteniendo codos ligeramente flexionados, baja hasta sentir estiramiento en pecho.",
            'Press Inclinado con Mancuernas': "En banco inclinado a 30-45°, presiona las mancuernas hacia arriba manteniendo control del movimiento.",
            'Flexiones en el Suelo': "Posición de plancha, baja el pecho hasta casi tocar el suelo, mantén el core contraído, empuja hacia arriba.",
            
            # ESPALDA
            'Remo con Mancuernas': "Torso paralelo al suelo, tira del codo hacia atrás llevando la mancuerna hacia las costillas.",
            'Remo a Una Mano': "Apoyo en banco con una mano, tira de la mancuerna hacia la cadera manteniendo el torso estable.",
            'Peso Muerto con Mancuernas': "Pies separados, baja las mancuernas manteniendo la espalda recta, empuja con los talones para subir.",
            
            # HOMBROS
            'Press Militar con Mancuernas': "De pie, mancuernas a la altura de los hombros, empuja hacia arriba hasta extensión completa.",
            'Elevaciones Laterales': "De pie, eleva los brazos lateralmente hasta la altura de los hombros con control.",
            'Elevaciones Frontales': "De pie, eleva las mancuernas al frente hasta la altura de los hombros alternando brazos.",
            'Pájaros con Mancuernas': "Inclinado hacia adelante, abre los brazos lateralmente apretando los omóplatos.",
            
            # BRAZOS
            'Curl de Bíceps': "Brazos extendidos, codos pegados al torso, flexiona llevando las mancuernas hacia los hombros.",
            'Curl Martillo': "Como el curl normal pero con agarre neutro (palmas enfrentadas), movimiento controlado.",
            'Curl Concentrado': "Sentado, codo apoyado en la pierna, flexiona el brazo con concentración total en el bíceps.",
            'Extensiones de Tríceps': "Acostado, codos fijos apuntando al techo, baja la mancuerna hacia la frente flexionando antebrazos.",
            'Patada de Tríceps': "Inclinado, brazo superior paralelo al suelo, extiende el antebrazo hacia atrás.",
            
            # PIERNAS
            'Sentadillas con Mancuernas': "Pies separados, baja como si te sentaras en una silla, mantén el pecho erguido.",
            'Zancadas con Mancuernas': "Paso largo adelante, baja hasta que ambas rodillas estén a 90 grados.",
            'Peso Muerto Rumano': "Piernas ligeramente flexionadas, baja las mancuernas manteniendo la curva lumbar.",
            'Sentadillas Sumo': "Pies muy separados, puntas hacia afuera, baja manteniendo rodillas alineadas con pies.",
            'Elevación de Talones': "De pie, elévate sobre las puntas de los pies contrayendo las pantorrillas.",
            
            # ABDOMINALES
            'Abdominales Tradicionales': "Acostado, rodillas flexionadas, eleva el torso hacia las rodillas sin tirar del cuello.",
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
            'Aperturas con Mancuernas': "No bajes demasiado para evitar lesiones en el hombro. Mantén codos ligeramente flexionados siempre.",
            'Press Inclinado con Mancuernas': "Ángulo del banco no mayor a 45°. Enfócate en la parte superior del pecho.",
            'Flexiones en el Suelo': "Mantén línea recta del cuerpo, si es difícil hazlas de rodillas. Progresa gradualmente.",
            
            # ESPALDA
            'Remo con Mancuernas': "Inicia el movimiento con los músculos de la espalda, no gires el torso. Aprieta omóplatos al final.",
            'Remo a Una Mano': "Mantén la espalda neutral, no uses impulso. El codo debe ir hacia atrás, no hacia afuera.",
            'Peso Muerto con Mancuernas': "Mantén la barra cerca del cuerpo, pecho arriba, peso en los talones.",
            
            # HOMBROS
            'Press Militar con Mancuernas': "Core contraído, no uses impulso con las piernas. Cuidado con la posición del cuello.",
            'Elevaciones Laterales': "Movimiento lento y controlado, no uses peso excesivo. Evita balancear el cuerpo.",
            'Elevaciones Frontales': "Alterna los brazos para mejor estabilidad. No subas más allá de la altura del hombro.",
            'Pájaros con Mancuernas': "Mantén rodillas ligeramente flexionadas. Enfócate en apretar los omóplatos.",
            
            # BRAZOS
            'Curl de Bíceps': "Mantén los codos fijos, no balancees el cuerpo. Contracción completa en la parte superior.",
            'Curl Martillo': "Variación excelente para el braquial. Alterna brazos para mejor concentración.",
            'Curl Concentrado': "Ideal para máxima concentración. No uses impulso, movimiento muy controlado.",
            'Extensiones de Tríceps': "Mantén los brazos superiores fijos, cuidado con el peso cerca de la cabeza.",
            'Patada de Tríceps': "Mantén el brazo superior inmóvil. Extensión completa pero sin bloquear agresivamente.",
            
            # PIERNAS
            'Sentadillas con Mancuernas': "Peso en los talones, no dejes que las rodillas se vayan hacia adentro. Profundidad completa.",
            'Zancadas con Mancuernas': "Mantén el equilibrio, rodilla delantera no debe sobrepasar el pie. Tronco erguido.",
            'Peso Muerto Rumano': "Excelente para isquiotibiales. Mantén las mancuernas cerca de las piernas.",
            'Sentadillas Sumo': "Activa los glúteos al subir. Rodillas siguen la dirección de los pies.",
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

    def render_exercise_details(self, exercise: Dict[str, Any], muscle_group: str, day_key: str, show_videos: bool, show_instructions: bool, show_tips: bool):
        """Renderizar detalles de un ejercicio completo"""
        exercise_name = exercise['name']
        exercise_id = f"{muscle_group}_{exercise_name}_{day_key}"
        
        # Obtener fecha actual para marcar progreso
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        is_completed = self.is_exercise_completed(current_date, exercise_id)
        
        # Checkbox de completado prominente
        col_checkbox, col_title = st.columns([1, 4])
        with col_checkbox:
            completed = st.checkbox(
                "✅ Completado",
                value=is_completed,
                key=self.generate_unique_key("exercise_completed", exercise_id, current_date),
                help=f"Marcar {exercise_name} como completado hoy"
            )
            
            # Actualizar estado si cambió
            if completed != is_completed:
                self.mark_exercise_completed(current_date, exercise_id, completed)
                if completed:
                    st.success(f"🎉 ¡{exercise_name} completado!")
                else:
                    st.info(f"📋 {exercise_name} marcado como pendiente")
                st.rerun()
        
        with col_title:
            # Mostrar estado visual del ejercicio
            status_emoji = "✅" if completed else "⭕"
            st.markdown(f"### {status_emoji} {exercise_name}")
            st.markdown(f"**Series:** {exercise['sets']} | **Reps:** {exercise['reps']} | **Grupo:** {muscle_group.title()}")
        
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
                st.write(f"• Series: {exercise['sets']}")
                st.write(f"• Repeticiones: {exercise['reps']}")
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
        
        # Mostrar progreso si es una semana avanzada
        if current_week > 4:
            progress_bar = min(week_info['week_in_cycle'] / 4, 1.0)
            st.progress(progress_bar, text=f"Progreso en nivel actual: {week_info['week_in_cycle']}/4 semanas")
        
        # Panel de progreso diario
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
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
        
        st.markdown("---")
        
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
        
        for day_key in day_order:
            muscle_groups = week_plan.get(day_key, [])
            day_display = day_names.get(day_key, day_key.upper())
            
            st.markdown(f"### {day_display}")
            
            if not muscle_groups:  # Día de descanso
                st.markdown("""
                <div class="rest-day">
                    <h3>🛌 Día de Descanso</h3>
                    <p>Recuperación activa - Estiramiento ligero, caminata o yoga</p>
                </div>
                """, unsafe_allow_html=True)
                continue
            
            for muscle_group in muscle_groups:
                if muscle_group in self.config['exercises']:
                    st.markdown(f"#### 💪 {muscle_group.title()}")
                    
                    for exercise in self.config['exercises'][muscle_group]:
                        self.render_exercise_details(exercise, muscle_group, day_key, show_videos, show_instructions, show_tips)
