"""
Módulo de Biblioteca de Ejercicios
Muestra todos los ejercicios disponibles con filtros y búsqueda
"""
import streamlit as st
from .base_trainer import BaseTrainer
from typing import List, Dict, Any


class ExerciseLibraryModule(BaseTrainer):
    """Módulo para explorar la biblioteca completa de ejercicios"""
    
    def get_all_exercises(self) -> Dict[str, List[Dict]]:
        """Obtener todos los ejercicios organizados por categoría"""
        return self.config.get('exercises', {})
    
    def filter_exercises(self, exercises: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Filtrar ejercicios según criterios"""
        filtered = exercises.copy()
        
        # Filtro por nivel
        if filters.get('level') and filters['level'] != 'Todos':
            level_map = {'Principiante': 1, 'Intermedio': 2, 'Avanzado': 3, 'Experto': 4}
            filtered = [ex for ex in filtered if ex.get('difficulty_level', 1) == level_map[filters['level']]]
        
        # Filtro por equipamiento
        if filters.get('equipment') and filters['equipment'] != 'Todos':
            filtered = [ex for ex in filtered if ex.get('equipment') == filters['equipment']]
        
        # Búsqueda por nombre
        if filters.get('search'):
            search_term = filters['search'].lower()
            filtered = [ex for ex in filtered if search_term in ex.get('name', '').lower()]
        
        return filtered
    
    def render_exercise_card(self, exercise: Dict[str, Any], category: str):
        """Renderizar tarjeta de ejercicio individual"""
        with st.expander(f"📋 {exercise['name']}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**📝 Descripción:**")
                st.write(exercise.get('description', 'No disponible'))
                
                st.markdown(f"**📊 Información:**")
                st.write(f"• Series: {exercise.get('sets', 1)}")
                st.write(f"• Repeticiones: {exercise.get('reps', '')}")
                st.write(f"• Equipo: {exercise.get('equipment', 'No especificado')}")
                
                # Nivel de dificultad
                level_emoji = {1: '🟢', 2: '🟡', 3: '🟠', 4: '🔴'}
                level_name = {1: 'Principiante', 2: 'Intermedio', 3: 'Avanzado', 4: 'Experto'}
                difficulty = exercise.get('difficulty_level', 1)
                st.write(f"• Nivel: {level_emoji.get(difficulty, '🟢')} {level_name.get(difficulty, 'Principiante')}")
            
            with col2:
                # Video de YouTube si está disponible
                youtube_url = exercise.get('youtube_url', '')
                if youtube_url:
                    st.markdown("**🎥 Video:**")
                    st.video(youtube_url)
    
    def render_category_section(self, category_name: str, category_label: str, exercises: List[Dict], filters: Dict):
        """Renderizar sección de categoría de ejercicios"""
        filtered_exercises = self.filter_exercises(exercises, filters)
        
        if filtered_exercises:
            st.markdown(f"### {category_label} ({len(filtered_exercises)})")
            
            for exercise in filtered_exercises:
                self.render_exercise_card(exercise, category_name)
            
            st.markdown("---")
    
    def render_filters_sidebar(self) -> Dict[str, Any]:
        """Renderizar panel de filtros en sidebar"""
        filters = {}
        
        st.sidebar.markdown("### 🔍 Filtros")
        
        # Búsqueda por nombre
        filters['search'] = st.sidebar.text_input(
            "Buscar ejercicio:",
            placeholder="Ej: flexiones, curl..."
        )
        
        #  Filtro por nivel
        filters['level'] = st.sidebar.selectbox(
            "Nivel de dificultad:",
            ['Todos', 'Principiante', 'Intermedio', 'Avanzado', 'Experto']
        )
        
        # Filtro por equipamiento
        equipment_options: List[str] = ['Todos', 'floor_space', 'dumbbells_8kg', 'dumbbell_12kg', 'bench_press_30kg', 'stationary_bike']
        equipment_labels: Dict[str, str] = {
            'Todos': 'Todos',
            'floor_space': 'Solo suelo',
            'dumbbells_8kg': 'Mancuernas 8kg',
            'dumbbell_12kg': 'Mancuerna 12kg',
            'bench_press_30kg': 'Banco con barra 30kg',
            'stationary_bike': 'Bicicleta estática'
        }

        def format_equipment(option: str) -> str:
            return equipment_labels.get(option, option)
        
        selected_equipment: str = st.sidebar.selectbox(
            "Equipamiento:",
            equipment_options,
            format_func=format_equipment
        )
        filters['equipment'] = selected_equipment if selected_equipment != 'Todos' else None
        
        # Filtro por categoría
        filters['category'] = st.sidebar.multiselect(
            "Categorías:",
            ['Calentamiento', 'Entrenamiento', 'Estiramiento', 'Movilidad'],
            default=['Calentamiento', 'Entrenamiento', 'Estiramiento', 'Movilidad']
        )
        
        return filters
    
    def render_library_tab(self):
        """Renderizar pestaña completa de biblioteca de ejercicios"""
        st.markdown("## 📚 Biblioteca de Ejercicios")
        st.info("Explora todos los ejercicios disponibles. Usa los filtros en la barra lateral para encontrar ejercicios específicos.")
        
        # Obtener filtros
        filters = self.render_filters_sidebar()
        
        # Obtener todos los ejercicios
        all_exercises = self.get_all_exercises()
        
        # Estadísticas generales
        total_exercises = sum(len(exercises) for exercises in all_exercises.values())
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Ejercicios", total_exercises)
        with col2:
            calentamiento_count = len(all_exercises.get('calentamiento', []))
            st.metric("Calentamiento", calentamiento_count)
        with col3:
            estiramiento_count = len(all_exercises.get('estiramiento', []))
            st.metric("Estiramiento", estiramiento_count)
        with col4:
            movilidad_count = len(all_exercises.get('movilidad', []))
            st.metric("Movilidad", movilidad_count)
        
        st.markdown("---")
        
        # Mapeo de categorías
        category_map = {
            'Calentamiento': ('calentamiento', '🔥 Calentamiento'),
            'Entrenamiento': (None, '💪 Entrenamiento'),
            'Estiramiento': ('estiramiento', '🧘 Estiramiento'),
            'Movilidad': ('movilidad', '🤸 Movilidad')
        }
        
        # Renderizar categorías según filtros
        for category_filter, (category_key, category_label) in category_map.items():
            if category_filter in filters.get('category', []):
                if category_key == None:
                    # Mostrar todos los grupos de entrenamiento
                    training_groups = ['pecho', 'espalda', 'hombros', 'brazos', 'piernas', 'gemelos', 'abs', 'abs_avanzados', 'cardio']
                    training_exercises = []
                    for group in training_groups:
                        training_exercises.extend(all_exercises.get(group, []))
                    
                    self.render_category_section('entrenamiento', category_label, training_exercises, filters)
                else:
                    exercises = all_exercises.get(category_key, [])
                    self.render_category_section(category_key, category_label, exercises, filters)
