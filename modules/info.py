"""
Módulo de Información
Contiene toda la lógica de la pestaña de información
"""
import os
import streamlit as st
from .base_trainer import BaseTrainer


class InfoModule(BaseTrainer):
    """Módulo para gestionar la información"""

    def render_info_tab(self):
        """Renderizar pestaña de información"""
        st.header("ℹ️ Información del Programa")
        
        # Título y descripción principal
        st.markdown("""
        ## 🎯 **SUDORACIONES - Sistema de Entrenamiento Personal**
        
        **Un programa de entrenamiento inteligente diseñado para maximizar tus resultados con equipamiento básico.**
        
        Este sistema está optimizado para personas que quieren entrenar desde casa con mancuernas y equipamiento mínimo,
        pero con resultados efectivos y seguimiento profesional.
        """)
        
        # Crear columnas para la información principal
        col1, col2 = st.columns(2)
        
        with col1:
            
            st.subheader("💡 Características Principales")
            st.markdown("""
            - **Plan Optimizado**: 22 ejercicios especializados
            - **Seguimiento Automático**: Progreso basado en completado
            - **Calendario Dinámico**: Visualización de entrenamiento mensual
            - **Videos Integrados**: Tutoriales YouTube y Shorts
            - **Sistema de Niveles**: Progresión automática inteligente
            """)
        
        with col2:
            st.subheader("📅 Estructura del Programa")
            st.markdown("""
            - **Progresión automática**: 5 niveles de dificultad
            - **20 semanas** de entrenamiento continuo
            - **22 ejercicios base** optimizados para principiantes
            - **Adaptación inteligente** según el progreso
            - **Sistema de niveles** desde principiante a experto
            """)
            
            st.subheader("🎯 Sistema de Progresión")
            st.markdown("""
            - **Nivel 1**: Principiante (Semanas 1-4)
            - **Nivel 2**: Básico (Semanas 5-8)  
            - **Nivel 3**: Intermedio (Semanas 9-12)
            - **Nivel 4**: Avanzado (Semanas 13-16)
            - **Nivel 5**: Experto (Semanas 17-20)
            """)

        # Equipamiento necesario
        st.subheader("🏋️ Equipamiento Necesario")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("""
            ### Equipamiento Básico:
            - **2 Mancuernas de 10kg**
            - **1 Mancuerna de 12kg**
            - **1 Banco de press (30kg)**
            - **1 Bicicleta estática**
            - **Espacio en el suelo**
            """)
        
        with col4:
            st.markdown("""
            ### Ventajas del Sistema:
            - ✅ **Mínimo equipamiento requerido**
            - ✅ **Resultados efectivos con constancia**
            - ✅ **Entrenamiento desde casa**
            - ✅ **Seguimiento automático**
            - ✅ **Videos instructivos incluidos**
            """)

        # Principios de entrenamiento
        st.subheader("⚡ Principios de Entrenamiento")
        
        principles_col1, principles_col2 = st.columns(2)
        
        with principles_col1:
            st.markdown("""
            ### 🔥 Metodología
            - **Intensidad**: Alta intensidad hasta el fallo muscular
            - **Frecuencia**: 3-4 entrenamientos por semana
            - **Descanso**: 3-5 minutos entre series
            - **Progresión**: Incremento gradual de peso o repeticiones
            """)
        
        with principles_col2:
            st.markdown("""
            ### 📈 Seguimiento
            - **Registro automático** de ejercicios completados
            - **Estadísticas detalladas** de progreso
            - **Calendario visual** con porcentajes de completado
            - **Recomendaciones inteligentes** de mejora
            """)

        # Grupos musculares trabajados
        st.subheader("💪 Grupos Musculares Trabajados")
        
        muscle_col1, muscle_col2, muscle_col3 = st.columns(3)
        
        with muscle_col1:
            st.markdown("""
            **Tren Superior:**
            - 🫸 Pecho
            - 🔙 Espalda
            - 🤷 Hombros
            - 💪 Brazos
            """)
        
        with muscle_col2:
            st.markdown("""
            **Tren Inferior:**
            - 🦵 Piernas
            - 🦶 Gemelos
            - 🏃 Cardio
            """)
        
        with muscle_col3:
            st.markdown("""
            **Core:**
            - 🔥 Abdominales
            - 🏋️ Abdominales Laterales
            - 🏪 Plancha
            """)

        # Estadísticas del programa
        st.subheader("📊 Estadísticas del Programa")
        
        if hasattr(self, 'config') and self.config:
            # Estadísticas de ejercicios
            exercise_stats = {}
            for muscle_group, exercises in self.config.get('exercises', {}).items():
                exercise_stats[muscle_group] = len(exercises)
            
            if exercise_stats:
                for group, count in exercise_stats.items():
                    st.markdown(f"- **{group.title()}**: {count} ejercicios")
            
            # Estadísticas generales
            total_exercises = sum(len(exercises) for exercises in self.config.get('exercises', {}).values())
            base_weeks = len(self.config.get('weekly_schedule', {}))
            total_weeks = base_weeks * 5  # 4 semanas base × 5 ciclos = 20 semanas totales
            
            # Contar ejercicios con video
            exercises_with_video = sum(1 for muscle_group, exercises in self.config.get('exercises', {}).items() 
                                     for exercise in exercises if exercise.get('youtube_url'))
            
            st.markdown(f"""
            ### 📈 Resumen General:
            - **Total de ejercicios**: {total_exercises}
            - **Ejercicios con video**: {exercises_with_video}/{total_exercises}
            - **Semanas programadas**: {total_weeks} (ciclo de {base_weeks} semanas × 5)
            - **Cobertura de video**: {(exercises_with_video/total_exercises*100):.1f}%
            """)
