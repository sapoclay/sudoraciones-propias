"""
Módulo de Progreso y Calendario
Contiene toda la lógica de la pestaña de progreso
"""
import datetime
import calendar
from typing import Dict, Any
import streamlit as st
from .base_trainer import BaseTrainer


class ProgressModule(BaseTrainer):
    """Módulo para gestionar el progreso y calendario"""
    
    # Diccionarios de traducción para meses
    MONTH_NAMES_ES = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    MONTH_ABBR_ES = {
        1: 'ENE', 2: 'FEB', 3: 'MAR', 4: 'ABR',
        5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AGO',
        9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DIC'
    }
    
    def get_month_name_es(self, month: int) -> str:
        """Obtener nombre del mes en español"""
        return self.MONTH_NAMES_ES.get(month, f'Mes {month}')
    
    def get_day_completion_stats_filtered(self, date_str: str, filter_week: int = None) -> Dict[str, Any]:
        """Obtener estadísticas de completado de un día filtradas por semana"""
        if filter_week is None:
            filter_week = st.session_state.get('current_week', 1)
        
        # Obtener ejercicios de esa fecha
        exercises_data = self.progress_data.get('completed_exercises', {}).get(date_str, {})
        
        if not exercises_data:
            return {
                'completed': 0,
                'total': 0,
                'percentage': 0,
                'exercises': [],
                'muscle_groups': [],
                'is_rest_day': False,
                'is_empty_day': True
            }
        
        # Filtrar solo ejercicios de la semana especificada
        week_suffix = f"_week{filter_week}"
        filtered_exercises = {}
        
        for exercise_id, is_completed in exercises_data.items():
            if exercise_id.endswith(week_suffix):
                filtered_exercises[exercise_id] = is_completed
        
        # Si no hay ejercicios de la semana especificada, mostrar día vacío
        if not filtered_exercises:
            return {
                'completed': 0,
                'total': 0,
                'percentage': 0,
                'exercises': [],
                'muscle_groups': [],
                'is_rest_day': False,
                'is_empty_day': True
            }
        
        # Calcular estadísticas de los ejercicios filtrados
        total_exercises = len(filtered_exercises)
        completed_exercises = sum(1 for completed in filtered_exercises.values() if completed)
        
        # Extraer grupos musculares
        muscle_groups = set()
        exercise_list = []
        for exercise_id, is_completed in filtered_exercises.items():
            parts = exercise_id.split('_')
            if len(parts) >= 2:
                mg = parts[0]
                name = '_'.join(parts[1:-2]) if len(parts) > 3 else parts[1]
                muscle_groups.add(mg)
                exercise_list.append({'name': name, 'muscle_group': mg, 'completed': is_completed})
        
        percentage = (completed_exercises / total_exercises * 100) if total_exercises > 0 else 0
        
        return {
            'completed': completed_exercises,
            'total': total_exercises,
            'percentage': percentage,
            'exercises': exercise_list,
            'muscle_groups': list(muscle_groups),
            'is_rest_day': False,
            'is_empty_day': False
        }
    
    def get_month_abbr_es(self, month: int) -> str:
        """Obtener abreviación del mes en español"""
        return self.MONTH_ABBR_ES.get(month, f'M{month}')

    def get_month_stats(self, year: int, month: int) -> Dict[str, int]:
        """Obtener estadísticas del mes"""
        month_key = f"{year:04d}-{month:02d}"
        completed_days = self.progress_data.get('completed_workouts', {}).get(month_key, [])
        
        # Obtener días del mes
        days_in_month = calendar.monthrange(year, month)[1]
        
        return {
            'completed': len(completed_days),
            'total_days': days_in_month,
            'completion_rate': (len(completed_days) / days_in_month) * 100 if days_in_month > 0 else 0,
            'completed_dates': completed_days
        }

    def get_month_stats_filtered(self, year: int, month: int, filter_week: int) -> Dict[str, Any]:
        """Obtener estadísticas del mes filtradas por semana específica"""
        _, last_day = calendar.monthrange(year, month)
        
        total_days = 0
        completed_days = 0
        total_exercises = 0
        completed_exercises = 0
        
        for day in range(1, last_day + 1):
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            day_stats = self.get_day_completion_stats_filtered(date_str, filter_week)
            
            if not day_stats.get('is_empty_day', True):
                total_days += 1
                total_exercises += day_stats.get('total', 0)
                completed_exercises += day_stats.get('completed', 0)
                if day_stats.get('percentage', 0) == 100:
                    completed_days += 1
        
        completion_rate = (completed_days / total_days * 100) if total_days > 0 else 0
        
        return {
            'completed': completed_exercises,
            'total': total_exercises,
            'completion_rate': completion_rate,
            'total_days': total_days,
            'completed_days': completed_days
        }

    def get_week_number_for_date(self, date_str: str) -> int:
        """Determinar qué número de semana corresponde a una fecha específica"""
        # Primero, verificar si tenemos la semana guardada explícitamente
        if 'exercise_weeks' in self.progress_data and date_str in self.progress_data['exercise_weeks']:
            return self.progress_data['exercise_weeks'][date_str]
        
        # Si la fecha tiene ejercicios registrados, intentar determinar la semana basándose en los IDs de ejercicios
        if 'completed_exercises' in self.progress_data and date_str in self.progress_data['completed_exercises']:
            exercise_ids = list(self.progress_data['completed_exercises'][date_str].keys())
            if exercise_ids:
                # Los IDs de ejercicio incluyen el día de la semana al final
                # Podemos intentar hacer coincidir con diferentes semanas
                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                day_names = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
                day_key = day_names[date_obj.weekday()]
                
                # Buscar en qué semana estos ejercicios tienen sentido
                for week_num in range(1, 21):  # Revisar semanas 1-20
                    week_info = self.get_week_info(week_num)
                    
                    if week_num <= 4:
                        week_key = f"semana{week_num}"
                        if week_key not in self.config.get('weekly_schedule', {}):
                            continue
                        week_plan = self.config['weekly_schedule'][week_key]
                    else:
                        # Para semanas avanzadas, usar el primer módulo de training
                        from .training_plan import TrainingPlanModule
                        trainer = TrainingPlanModule()
                        trainer.config = self.config
                        trainer.progress_data = self.progress_data
                        week_plan = trainer.generate_advanced_week(week_num)
                    
                    muscle_groups = week_plan.get(day_key, [])
                    
                    # Verificar si los ejercicios registrados coinciden con esta semana
                    expected_exercises = set()
                    for muscle_group in muscle_groups:
                        if muscle_group in self.config.get('exercises', {}):
                            for exercise in self.config['exercises'][muscle_group]:
                                exercise_id = f"{muscle_group}_{exercise['name']}_{day_key}"
                                expected_exercises.add(exercise_id)
                    
                    # Si al menos el 50% de los ejercicios registrados coinciden con esta semana
                    registered_exercises = set(exercise_ids)
                    if expected_exercises and len(registered_exercises & expected_exercises) >= len(registered_exercises) * 0.5:
                        # Guardar esta información para futura referencia
                        if 'exercise_weeks' not in self.progress_data:
                            self.progress_data['exercise_weeks'] = {}
                        self.progress_data['exercise_weeks'][date_str] = week_num
                        self.save_progress_data()
                        return week_num
        
        # NUEVO: Inferir semana desde otros días de la MISMA semana calendario (Lun-Dom)
        try:
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            start_of_week = date_obj - datetime.timedelta(days=date_obj.weekday())  # lunes
            dates_in_week = [(start_of_week + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

            # 1) Si cualquiera de esos días ya tiene mapeo, usarlo
            weeks_map = self.progress_data.get('exercise_weeks', {})
            for d in dates_in_week:
                if d in weeks_map:
                    inferred = weeks_map[d]
                    # Persistir para la fecha consultada
                    self.progress_data.setdefault('exercise_weeks', {})[date_str] = inferred
                    self.save_progress_data()
                    return inferred

            # 2) Si alguno tiene ejercicios con sufijo _weekN, extraer N y usar la moda
            from collections import Counter
            week_nums = []
            for d in dates_in_week:
                ex_data = self.progress_data.get('completed_exercises', {}).get(d, {})
                for ex_id in ex_data.keys():
                    # Buscar patrón _week<number> al final
                    if '_week' in ex_id:
                        try:
                            suffix = ex_id.split('_week')[-1]
                            n = ''
                            for ch in suffix:
                                if ch.isdigit():
                                    n += ch
                                else:
                                    break
                            if n:
                                week_nums.append(int(n))
                        except Exception:
                            pass
            if week_nums:
                inferred = Counter(week_nums).most_common(1)[0][0]
                self.progress_data.setdefault('exercise_weeks', {})[date_str] = inferred
                self.save_progress_data()
                return inferred
        except Exception:
            pass
        
        # Fallback: usar la semana actual SOLO si no se pudo inferir de ninguna forma
        return st.session_state.get('current_week', 1)

    def get_day_completion_stats(self, date_str: str, week_number: int = None) -> Dict[str, Any]:
        """Obtener estadísticas de finalización para un día específico"""
        # Si no se proporciona week_number, usar el mapeo calendario
        if week_number is None:
            week_number = self.get_calendar_week_for_date(date_str)
        
        # Determinar día de la semana (clave en español)
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        day_names = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        day_key = day_names[date_obj.weekday()]
        
        # Obtener plan de la semana correspondiente
        week_plan = {}
        if week_number <= 4:
            week_key = f"semana{week_number}"
            week_plan = self.config.get('weekly_schedule', {}).get(week_key, {})
        else:
            from .training_plan import TrainingPlanModule
            trainer = TrainingPlanModule()
            trainer.config = self.config
            trainer.progress_data = self.progress_data
            week_plan = trainer.generate_advanced_week(week_number)
        
        muscle_groups_planned = week_plan.get(day_key, []) or []
        is_rest_day_planned = len(muscle_groups_planned) == 0
        
        # Prioridad: si el plan marca descanso, devolver descanso SIEMPRE
        if is_rest_day_planned:
            return {
                'completed': 0,
                'total': 0,
                'percentage': 0,
                'exercises': [],
                'muscle_groups': [],
                'is_rest_day': True,
                'is_empty_day': False,
                'calendar_week': week_number
            }
        
        # 1) Si hay datos en la fecha, calcular en base a los ejercicios reales de ese día
        exercises_data = self.progress_data.get('completed_exercises', {}).get(date_str)
        if exercises_data:
            # Filtrar solo ejercicios de la semana calendario correspondiente
            week_suffix = f"_week{week_number}"
            filtered_exercises = {k: v for k, v in exercises_data.items() if k.endswith(week_suffix)}
            
            if filtered_exercises:
                total_exercises = len(filtered_exercises)
                completed_exercises = sum(1 for completed in filtered_exercises.values() if completed)
                
                # Extraer grupos musculares presentes en los IDs
                muscle_groups = set()
                exercise_list = []
                for exercise_id, is_completed in filtered_exercises.items():
                    parts = exercise_id.split('_')
                    if len(parts) >= 2:
                        mg = parts[0]
                        name = '_'.join(parts[1:-2]) if len(parts) > 3 else parts[1]
                        muscle_groups.add(mg)
                        exercise_list.append({'name': name, 'muscle_group': mg, 'completed': is_completed})
                
                percentage = (completed_exercises / total_exercises * 100) if total_exercises > 0 else 0
                return {
                    'completed': completed_exercises,
                    'total': total_exercises,
                    'percentage': percentage,
                    'exercises': exercise_list,
                    'muscle_groups': list(muscle_groups),
                    'is_rest_day': False,
                    'is_empty_day': False,
                    'calendar_week': week_number
                }
        
        # 2) Si NO hay datos en la fecha actual, calcular ejercicios esperados según el plan del día
        expected_total = 0
        for mg in muscle_groups_planned:
            planned_list = self.get_planned_exercises_for_group(mg, day_key, week_number)
            expected_total += len(planned_list)
        
        return {
            'completed': 0,
            'total': expected_total,
            'percentage': 0,
            'exercises': [],
            'muscle_groups': muscle_groups_planned,
            'is_rest_day': False,
            'is_empty_day': True,
            'calendar_week': week_number
        }

    def render_calendar(self, year: int, month: int, view_week: int = None):
        """Renderizar calendario de solo visualización con porcentajes de todas las semanas"""
        current_week = st.session_state.get('current_week', 1)
        month_name = self.get_month_name_es(month)
        st.subheader(f"📅 {month_name} {year} - Progreso Acumulativo (Semana Actual: {current_week})")
        
        # Obtener estadísticas del mes SIN filtrar por semana (mostrar todo)
        stats = self.get_month_stats(year, month)
        
        # Crear calendario
        cal = calendar.monthcalendar(year, month)
        
        # Nombres de días
        days_names = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        
        # CSS para el calendario con gradientes de progreso
        st.markdown("""
        <style>
        .calendar-day {
            text-align: center;
            padding: 8px;
            margin: 2px;
            border-radius: 8px;
            min-height: 60px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 12px;
        }
        .day-perfect {
            background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
            color: white;
        }
        .day-good {
            background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
            color: white;
        }
        .day-partial {
            background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%);
            color: white;
        }
        .day-none {
            background: #ddd;
            color: #666;
        }
        .day-rest {
            background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%);
            color: #1b5e20;
            border: 2px solid #43a047;
        }
        .day-today {
            border: 3px solid #0984e3;
        }
        .day-empty {
            background: transparent;
        }
        .percentage-text {
            font-size: 10px;
            margin-top: 2px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Mostrar estadísticas del mes
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Días con Entrenamiento", stats['completed'], f"de {stats['total_days']}")
        with col2:
            st.metric("Tasa de Cumplimiento", f"{stats['completion_rate']:.1f}%")
        with col3:
            if stats['completed'] > 0:
                avg_per_week = stats['completed'] / 4.33  # Promedio mensual
                st.metric("Promedio Semanal", f"{avg_per_week:.1f}", "días/semana")
        
        # Leyenda de colores
        st.markdown("#### Leyenda del Calendario")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("🟢 **100%** - Entrenamiento completo")
        with col2:
            st.markdown("🟡 **80-99%** - Casi completo")
        with col3:
            st.markdown("🟠 **1-79%** - Parcialmente completado")
        with col4:
            st.markdown("⚪ **0%** - Sin entrenamientos")
        
        st.info("✅ **Días de descanso** se marcan automáticamente como completados con un ✓")
        
        st.markdown("---")
        
        # Cabecera con días de la semana
        header_cols = st.columns(7)
        for i, day_name in enumerate(days_names):
            with header_cols[i]:
                st.markdown(f"**{day_name}**")
        
        # Renderizar semanas
        today = datetime.datetime.now()
        current_week = st.session_state.get('current_week', 1)
        
        for week in cal:
            week_cols = st.columns(7)
            for i, day in enumerate(week):
                with week_cols[i]:
                    if day == 0:
                        st.markdown('<div class="calendar-day day-empty"></div>', unsafe_allow_html=True)
                    else:
                        date_str = f"{year:04d}-{month:02d}-{day:02d}"
                        # SIEMPRE mostrar todos los ejercicios de todas las semanas para ver progreso completo
                        day_stats = self.get_day_completion_stats(date_str)
                        
                        # Determinar clase CSS según porcentaje y tipo de día
                        if day_stats.get('is_rest_day', False):
                            css_class = "day-rest"
                            percentage_text = "✓"
                        elif day_stats.get('is_empty_day', False):
                            # Día sin entrenar - mostrarlo en blanco/gris
                            css_class = "day-none"
                            percentage_text = ""  # Sin texto
                        elif day_stats['percentage'] == 100:
                            css_class = "day-perfect"
                            percentage_text = f"{day_stats['percentage']:.0f}%"
                        elif day_stats['percentage'] >= 80:
                            css_class = "day-good"
                            percentage_text = f"{day_stats['percentage']:.0f}%"
                        elif day_stats['percentage'] > 0:
                            css_class = "day-partial"
                            percentage_text = f"{day_stats['percentage']:.0f}%"
                        else:
                            css_class = "day-none"
                            percentage_text = f"{day_stats['percentage']:.0f}%"
                        
                        # Agregar clase especial si es hoy
                        today_class = ""
                        if (year == today.year and month == today.month and day == today.day):
                            today_class = " day-today"
                        
                        # Crear tooltip con información
                        if day_stats.get('is_rest_day', False):
                            tooltip = f"Día {day}: Día de descanso ✓"
                        elif day_stats.get('is_empty_day', False):
                            tooltip = f"Día {day}: Sin entrenar"
                        else:
                            tooltip = f"Día {day}: {day_stats['percentage']:.0f}% completado"
                            if day_stats['total'] > 0:
                                tooltip += f"\nEjercicios: {day_stats['completed']}/{day_stats['total']}"
                                tooltip += f"\nGrupos: {', '.join(day_stats['muscle_groups'])}"
                        
                        st.markdown(f"""
                        <div class=\"calendar-day {css_class}{today_class}\" title=\"{tooltip}\">\n                            <div>{day}</div>\n                            <div class=\"percentage-text\">{percentage_text}</div>\n                        </div>
                        """, unsafe_allow_html=True)
        
        # Información adicional
        st.info("""
        **Calendario automático basado en ejercicios completados:**
        - Los porcentajes se calculan automáticamente desde el plan de entrenamiento
        - Un día se considera "completado" cuando ≥80% de ejercicios están hechos
        - Los colores indican el nivel de progreso del día
        - No es necesario marcar días manualmente
        """)

    def calculate_current_streak(self) -> int:
        """Calcular la racha actual de días consecutivos de entrenamiento"""
        if 'completed_workouts' not in self.progress_data:
            return 0
        
        # Obtener todas las fechas completadas y ordenarlas
        all_completed = []
        for month_dates in self.progress_data['completed_workouts'].values():
            all_completed.extend(month_dates)
        
        if not all_completed:
            return 0
        
        all_completed.sort(reverse=True)  # Más reciente primero
        
        # Calcular racha desde hoy hacia atrás
        current_date = datetime.datetime.now().date()
        streak = 0
        
        for i in range(30):  # Revisar últimos 30 días
            check_date = current_date - datetime.timedelta(days=i)
            date_str = check_date.strftime("%Y-%m-%d")
            
            if date_str in all_completed:
                streak += 1
            else:
                break
        
        return streak

    def render_progress_tab(self):
        """Renderizar pestaña de progreso con calendario"""
        st.header("📊 Tu Progreso de Entrenamiento")
        
        # Inicializar estado de navegación del calendario
        current_date = datetime.datetime.now()
        
        if 'calendar_year' not in st.session_state:
            st.session_state.calendar_year = current_date.year
        if 'calendar_month' not in st.session_state:
            st.session_state.calendar_month = current_date.month
        
        # Mostrar información de la semana actual
        current_week = st.session_state.get('current_week', 1)
        week_info = self.get_week_info(current_week)
        
        st.info(f"📅 **Semana Actual: {current_week}** - {week_info['level_name']} | {week_info['level_description']}")
        st.caption("*El calendario muestra el progreso acumulativo de todas las semanas*")
        
        st.markdown("---")
        
        # Selector de mes y año
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            year_options = list(range(current_date.year - 1, current_date.year + 2))
            year_index = year_options.index(st.session_state.calendar_year) if st.session_state.calendar_year in year_options else 1
            selected_year = st.selectbox(
                "Año:",
                options=year_options,
                index=year_index,
                key="year_selector"
            )
            st.session_state.calendar_year = selected_year
        
        with col2:
            month_names = [self.get_month_name_es(i) for i in range(1, 13)]  # Meses en español
            month_index = st.session_state.calendar_month - 1
            selected_month_name = st.selectbox(
                "Mes:",
                options=month_names,
                index=month_index,
                key="month_selector"
            )
            selected_month = month_names.index(selected_month_name) + 1
            st.session_state.calendar_month = selected_month
        
        with col3:
            # Botones de navegación rápida
            col_prev, col_today, col_next = st.columns(3)
            with col_prev:
                if st.button("⬅️ Mes Anterior", key="btn_prev_month"):
                    if st.session_state.calendar_month == 1:
                        st.session_state.calendar_year -= 1
                        st.session_state.calendar_month = 12
                    else:
                        st.session_state.calendar_month -= 1
                    st.rerun()
            
            with col_today:
                current_date = datetime.datetime.now()
                month_names = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", 
                              "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
                month_abbr = month_names[current_date.month - 1]
                
                # Usar solo el botón nativo de Streamlit con texto personalizado
                calendar_button_label = f"📅 {current_date.day} {month_abbr}"
                
                if st.button(calendar_button_label, key="calendar_today_btn", help="Ir al mes y año actual"):
                    st.session_state.calendar_year = current_date.year
                    st.session_state.calendar_month = current_date.month
                    st.rerun()
                
                # CSS simple para estilizar solo el botón nativo
                st.markdown(f"""
                <style>
                /* Estilizar el botón del calendario para que se vea como un icono */
                div[data-testid="stButton"]:has(button[title="Ir al mes y año actual"]) button {{
                    background: linear-gradient(135deg, #ff4757, #ff3838) !important;
                    color: white !important;
                    border: 3px solid white !important;
                    border-radius: 12px !important;
                    box-shadow: 0 4px 15px rgba(255, 71, 87, 0.4) !important;
                    font-weight: bold !important;
                    font-size: 14px !important;
                    padding: 8px 12px !important;
                    min-height: 45px !important;
                    transition: all 0.3s ease !important;
                }}
                
                div[data-testid="stButton"]:has(button[title="Ir al mes y año actual"]) button:hover {{
                    transform: scale(1.05) !important;
                    box-shadow: 0 6px 20px rgba(255, 71, 87, 0.6) !important;
                }}
                
                /* Centrar el botón */
                div[data-testid="stButton"]:has(button[title="Ir al mes y año actual"]) {{
                    display: flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                }}
                </style>
                """, unsafe_allow_html=True)
            
            with col_next:
                if st.button("➡️ Mes Siguiente", key="btn_next_month"):
                    if st.session_state.calendar_month == 12:
                        st.session_state.calendar_year += 1
                        st.session_state.calendar_month = 1
                    else:
                        st.session_state.calendar_month += 1
                    st.rerun()
        
        st.markdown("---")
        
        # Renderizar calendario del mes seleccionado con progreso acumulativo
        self.render_calendar(st.session_state.calendar_year, st.session_state.calendar_month)
        
        st.markdown("---")
        
        # Estadísticas generales
        st.subheader("📈 Estadísticas Generales")
        
        # Calcular estadísticas de varios meses
        total_completed = 0
        months_data = []
        
        for i in range(6):  # Últimos 6 meses
            date = current_date - datetime.timedelta(days=30 * i)
            stats = self.get_month_stats(date.year, date.month)
            total_completed += stats['completed']
            months_data.append({
                'Mes': f"{calendar.month_abbr[date.month]} {date.year}",
                'Entrenamientos': stats['completed'],
                'Tasa': stats['completion_rate']
            })
        
        months_data.reverse()  # Mostrar en orden cronológico
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Entrenamientos Totales", self.progress_data.get('total_workouts', 0))
        
        with col2:
            selected_month_stats = self.get_month_stats(st.session_state.calendar_year, st.session_state.calendar_month)
            current_month_stats = self.get_month_stats(current_date.year, current_date.month)
            if st.session_state.calendar_year == current_date.year and st.session_state.calendar_month == current_date.month:
                st.metric("Este Mes", current_month_stats['completed'], f"{current_month_stats['completion_rate']:.1f}%")
            else:
                month_name = self.get_month_abbr_es(st.session_state.calendar_month)
                st.metric(f"{month_name} {st.session_state.calendar_year}", selected_month_stats['completed'], f"{selected_month_stats['completion_rate']:.1f}%")
        
        with col3:
            week_info = self.get_week_info(st.session_state.current_week)
            st.metric("Nivel Actual", week_info['level'], week_info['level_name'])
        
        with col4:
            # Racha actual (días consecutivos)
            streak = self.calculate_current_streak()
            st.metric("Racha Actual", f"{streak} días", "🔥" if streak > 0 else "")
        
        # Consejos y motivación
        st.subheader("💡 Consejos de Progreso")
        
        current_month_stats = self.get_month_stats(current_date.year, current_date.month)
        
        if current_month_stats['completion_rate'] >= 80:
            st.success("🎉 ¡Excelente! Mantienes una rutina muy consistente.")
        elif current_month_stats['completion_rate'] >= 60:
            st.info("👍 Buen progreso. Intenta ser más consistente para mejores resultados.")
        elif current_month_stats['completion_rate'] >= 40:
            st.warning("📈 Puedes mejorar. Intenta entrenar al menos 4 días por semana.")
        else:
            st.error("💪 ¡Es hora de retomar el ritmo! Cada entrenamiento cuenta.")
        
        # Instrucciones
        st.info("""
        **Cómo interpretar el calendario:**
        - 🟢 Verde (100%): Entrenamiento completado
        - 🟡 Amarillo (80-99%): Casi completado
        - 🟠 Naranja (1-79%): Parcialmente completado
        - ⚪ Gris (0%): Sin entrenamientos
        - 🔵 Borde azul: Día actual
        - **Los porcentajes se calculan automáticamente** desde el Plan de Entrenamiento
        """)
