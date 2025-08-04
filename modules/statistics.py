"""
Módulo de Estadísticas
Contiene toda la lógica de la pestaña de estadísticas
"""
import pandas as pd
import plotly.express as px
import streamlit as st
from .base_trainer import BaseTrainer


class StatisticsModule(BaseTrainer):
    """Módulo para gestionar las estadísticas"""
    
    # Diccionario de traducción de grupos musculares
    MUSCLE_GROUP_TRANSLATIONS = {
        'pecho': 'Pecho',
        'espalda': 'Espalda', 
        'hombros': 'Hombros',
        'brazos': 'Brazos',
        'piernas': 'Piernas',
        'gemelos': 'Gemelos',
        'abs': 'Abdominales',
        'abdominales': 'Abdominales',
        'cardio': 'Cardio'
    }
    
    def translate_muscle_group(self, group_name):
        """Traduce el nombre del grupo muscular al español"""
        return self.MUSCLE_GROUP_TRANSLATIONS.get(group_name.lower(), group_name.title())

    def render_statistics_tab(self):
        """Renderizar pestaña de estadísticas"""
        st.header("📈 Estadísticas Detalladas")
        
        # Análisis de completado vs disponible por grupo
        exercise_counts = {}
        completed_counts = {}
        
        # Contar ejercicios disponibles por grupo
        for muscle_group, exercises in self.config.get('exercises', {}).items():
            exercise_counts[muscle_group] = len(exercises)
            completed_counts[muscle_group] = 0
        
        # Contar ejercicios completados por grupo
        if 'completed_exercises' in self.progress_data:
            for date_str, exercises in self.progress_data['completed_exercises'].items():
                for exercise_id, completed in exercises.items():
                    if completed:
                        parts = exercise_id.split('_')
                        if len(parts) >= 2:
                            muscle_group = parts[0]
                            if muscle_group in completed_counts:
                                completed_counts[muscle_group] += 1
        
        if exercise_counts:
            col1, col2 = st.columns(2)
            
            with col1:
                # Comparación completados vs disponibles
                comparison_data = []
                for group in exercise_counts.keys():
                    total_available = exercise_counts[group] * 20  # Aproximado para 20 semanas
                    completed = completed_counts[group]
                    completion_rate = (completed / total_available * 100) if total_available > 0 else 0
                    
                    comparison_data.append({
                        'Grupo': self.translate_muscle_group(group),
                        'Completados': completed,
                        'Disponibles (20 sem)': total_available,
                        'Tasa Completado (%)': round(completion_rate, 1)
                    })
                
                df_comparison = pd.DataFrame(comparison_data)
                
                fig_comparison = px.bar(df_comparison, x='Grupo', y=['Completados', 'Disponibles (20 sem)'],
                                      title='Ejercicios Completados vs Disponibles por Grupo',
                                      barmode='group',
                                      color_discrete_map={'Completados': '#2ecc71', 'Disponibles (20 sem)': '#ecf0f1'})
                st.plotly_chart(fig_comparison, use_container_width=True)
            
            with col2:
                # Ranking de grupos más y menos entrenados
                if completed_counts and sum(completed_counts.values()) > 0:
                    sorted_groups = sorted(completed_counts.items(), key=lambda x: x[1], reverse=True)
                    
                    st.markdown("#### 🏆 **Grupos Más Entrenados**")
                    for i, (group, count) in enumerate(sorted_groups[:3]):
                        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
                        st.markdown(f"{medal} **{self.translate_muscle_group(group)}**: {count} veces completado")
                    
                    st.markdown("#### 📉 **Grupos Menos Entrenados**")
                    for i, (group, count) in enumerate(reversed(sorted_groups[-3:])):
                        warning = "⚠️" if count < max(completed_counts.values()) * 0.5 else "📝"
                        st.markdown(f"{warning} **{self.translate_muscle_group(group)}**: {count} veces completado")
                else:
                    st.info("🏋️ ¡Comienza a entrenar para ver tus estadísticas!")
        
        st.markdown("---")
        
        # Análisis de progreso temporal
        st.subheader("📊 Análisis de Progreso Temporal")
        
        if 'completed_workouts' in self.progress_data:
            # Preparar datos de progreso mensual
            monthly_data = []
            for month_key, dates in self.progress_data['completed_workouts'].items():
                year, month = month_key.split('-')
                monthly_data.append({
                    'Mes': f"{month}/{year}",
                    'Entrenamientos': len(dates),
                    'Año': int(year),
                    'Mes_Num': int(month)
                })
            
            if monthly_data:
                df_monthly = pd.DataFrame(monthly_data)
                df_monthly = df_monthly.sort_values(['Año', 'Mes_Num'])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Gráfico de líneas de progreso mensual
                    fig_line = px.line(df_monthly, x='Mes', y='Entrenamientos',
                                     title='Progreso de Entrenamientos por Mes',
                                     markers=True)
                    fig_line.update_traces(line=dict(color='#e74c3c', width=3))
                    st.plotly_chart(fig_line, use_container_width=True)
                
                with col2:
                    # Gráfico de barras de entrenamientos por mes
                    fig_monthly_bar = px.bar(df_monthly, x='Mes', y='Entrenamientos',
                                           title='Entrenamientos Completados por Mes',
                                           color='Entrenamientos',
                                           color_continuous_scale='blues')
                    st.plotly_chart(fig_monthly_bar, use_container_width=True)
        
        st.markdown("---")
        
        # Análisis detallado de entrenamientos por grupo
        st.subheader("💪 Análisis de Rendimiento por Grupo")
        
        # Calcular estadísticas avanzadas por grupo
        muscle_group_detailed = {}
        
        if 'completed_exercises' in self.progress_data:
            for date_str, exercises in self.progress_data['completed_exercises'].items():
                for exercise_id, completed in exercises.items():
                    if completed:
                        parts = exercise_id.split('_')
                        if len(parts) >= 2:
                            muscle_group = parts[0]
                            if muscle_group not in muscle_group_detailed:
                                muscle_group_detailed[muscle_group] = {
                                    'total_completados': 0,
                                    'dias_entrenados': set(),
                                    'ejercicios_unicos': set()
                                }
                            muscle_group_detailed[muscle_group]['total_completados'] += 1
                            muscle_group_detailed[muscle_group]['dias_entrenados'].add(date_str)
                            muscle_group_detailed[muscle_group]['ejercicios_unicos'].add(exercise_id)
        
        if muscle_group_detailed:
            col1, col2 = st.columns(2)
            
            with col1:
                # Frecuencia de entrenamiento por grupo (días únicos)
                frequency_data = []
                for group, stats in muscle_group_detailed.items():
                    frequency_data.append({
                        'Grupo': self.translate_muscle_group(group),
                        'Días Entrenados': len(stats['dias_entrenados']),
                        'Ejercicios Únicos': len(stats['ejercicios_unicos']),
                        'Total Completados': stats['total_completados']
                    })
                
                df_frequency = pd.DataFrame(frequency_data)
                df_frequency = df_frequency.sort_values('Días Entrenados', ascending=True)
                
                fig_frequency = px.bar(df_frequency, x='Días Entrenados', y='Grupo',
                                     title='Frecuencia de Entrenamiento (Días Únicos)',
                                     orientation='h',
                                     color='Días Entrenados',
                                     color_continuous_scale='greens',
                                     text='Días Entrenados')
                fig_frequency.update_traces(textposition='outside')
                st.plotly_chart(fig_frequency, use_container_width=True)
            
            with col2:
                # Intensidad promedio por grupo (completados por día)
                intensity_data = []
                for group, stats in muscle_group_detailed.items():
                    dias_entrenados = len(stats['dias_entrenados'])
                    intensity = stats['total_completados'] / dias_entrenados if dias_entrenados > 0 else 0
                    intensity_data.append({
                        'Grupo': self.translate_muscle_group(group),
                        'Intensidad Promedio': round(intensity, 2),
                        'Total Completados': stats['total_completados']
                    })
                
                df_intensity = pd.DataFrame(intensity_data)
                df_intensity = df_intensity.sort_values('Intensidad Promedio', ascending=False)
                
                fig_intensity = px.scatter(df_intensity, x='Intensidad Promedio', y='Grupo',
                                         size='Total Completados',
                                         title='Intensidad Promedio por Grupo (Ejercicios/Día)',
                                         color='Intensidad Promedio',
                                         color_continuous_scale='oranges')
                st.plotly_chart(fig_intensity, use_container_width=True)
        
        st.markdown("---")
        
        # Tabla de ejercicios completa
        st.subheader("📋 Lista Completa de Ejercicios")
        
        all_exercises = []
        for muscle_group, exercises in self.config.get('exercises', {}).items():
            for exercise in exercises:
                # Calcular cuántas veces se ha completado este ejercicio
                completed_count = 0
                if 'completed_exercises' in self.progress_data:
                    for date_str, exercises_day in self.progress_data['completed_exercises'].items():
                        for exercise_id, completed in exercises_day.items():
                            if (completed and 
                                exercise['name'] in exercise_id and 
                                muscle_group in exercise_id):
                                completed_count += 1
                
                all_exercises.append({
                    'Grupo': self.translate_muscle_group(muscle_group),
                    'Ejercicio': exercise['name'],
                    'Series': exercise['sets'],
                    'Repeticiones': exercise['reps'],
                    'Video': '✅' if exercise.get('youtube_url') else '❌',
                    'Veces Completado': completed_count
                })
        
        if all_exercises:
            df_all = pd.DataFrame(all_exercises)
            
            # Opciones de filtrado
            col1, col2 = st.columns(2)
            with col1:
                selected_groups = st.multiselect(
                    "Filtrar por grupo muscular:",
                    options=df_all['Grupo'].unique(),
                    default=df_all['Grupo'].unique()
                )
            
            with col2:
                show_only_with_video = st.checkbox("Solo mostrar ejercicios con video", value=False)
            
            # Aplicar filtros
            df_filtered = df_all[df_all['Grupo'].isin(selected_groups)]
            if show_only_with_video:
                df_filtered = df_filtered[df_filtered['Video'] == '✅']
            
            # Ordenar por veces completado (descendente)
            df_filtered = df_filtered.sort_values('Veces Completado', ascending=False)
            
            st.dataframe(df_filtered, use_container_width=True)
            
            # Estadísticas resumen de la tabla
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Ejercicios", len(df_filtered))
            with col2:
                st.metric("Con Video", len(df_filtered[df_filtered['Video'] == '✅']))
            with col3:
                st.metric("Sin Video", len(df_filtered[df_filtered['Video'] == '❌']))
            with col4:
                total_completions = df_filtered['Veces Completado'].sum()
                st.metric("Total Completados", total_completions)
        
        st.markdown("---")
        
        # Recomendaciones basadas en datos
        st.subheader("🎯 Recomendaciones Personalizadas")
        
        recommendations = []
        
        # Análisis de grupos menos entrenados
        if muscle_group_detailed:
            # Obtener conteos simples para las recomendaciones
            simple_counts = {group: stats['total_completados'] for group, stats in muscle_group_detailed.items()}
            min_trained = min(simple_counts.values())
            max_trained = max(simple_counts.values())
            
            for group, count in simple_counts.items():
                if count == min_trained and min_trained < max_trained * 0.7:
                    recommendations.append(f"💡 **{self.translate_muscle_group(group)}**: Grupo menos entrenado. Considera aumentar la frecuencia.")
        elif completed_counts and sum(completed_counts.values()) > 0:
            # Usar los datos de la primera sección como respaldo
            min_trained = min(completed_counts.values())
            max_trained = max(completed_counts.values())
            
            for group, count in completed_counts.items():
                if count == min_trained and min_trained < max_trained * 0.7:
                    recommendations.append(f"💡 **{self.translate_muscle_group(group)}**: Grupo menos entrenado. Considera aumentar la frecuencia.")
        
        # Análisis de consistencia
        if 'completed_workouts' in self.progress_data:
            total_months = len(self.progress_data['completed_workouts'])
            if total_months > 1:
                monthly_avg = sum(len(dates) for dates in self.progress_data['completed_workouts'].values()) / total_months
                if monthly_avg < 8:
                    recommendations.append(f"📈 **Consistencia**: Promedio de {monthly_avg:.1f} entrenamientos/mes. Meta recomendada: 12+ entrenamientos/mes.")
        
        # Análisis de videos
        total_exercises = sum(len(exercises) for exercises in self.config.get('exercises', {}).values())
        exercises_with_video = sum(1 for muscle_group, exercises in self.config.get('exercises', {}).items() 
                                 for exercise in exercises if exercise.get('youtube_url'))
        
        if exercises_with_video < total_exercises * 0.8:
            recommendations.append(f"🎥 **Videos**: Solo {exercises_with_video}/{total_exercises} ejercicios tienen video. Agregar más videos mejorará la técnica.")
        
        if recommendations:
            for rec in recommendations:
                st.info(rec)
        else:
            st.success("🎉 ¡Excelente! Tu entrenamiento está bien balanceado y consistente.")
        
        # Datos técnicos
        with st.expander("🔧 Información Técnica"):
            st.markdown("### Datos del Sistema")
            st.json({
                "Total ejercicios configurados": sum(len(exercises) for exercises in self.config.get('exercises', {}).values()),
                "Grupos musculares": len(self.config.get('exercises', {})),
                "Semanas de progreso disponibles": 20,
                "Ejercicios con video": exercises_with_video,
                "Datos de progreso guardados": len(self.progress_data.get('completed_exercises', {})),
                "Entrenamientos totales": self.progress_data.get('total_workouts', 0)
            })
