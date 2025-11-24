"""
Módulo de Nutrición
Proporciona calculadoras de calorías, macros y tracking básico de comidas
"""
import streamlit as st
import json
import os
import datetime
from typing import Dict, Any, List
from .base_trainer import BaseTrainer


class NutritionModule(BaseTrainer):
    """Módulo para gestión de nutrición y tracking de comidas"""
    
    def __init__(self):
        super().__init__()
        self.nutrition_file = 'nutrition_data.json'
        self.nutrition_data = self.load_nutrition_data()
    
    def load_nutrition_data(self) -> Dict[str, Any]:
        """Cargar datos de nutrición"""
        if os.path.exists(self.nutrition_file):
            try:
                with open(self.nutrition_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Datos por defecto
        return {
            'profile': {
                'age': None,
                'weight': None,
                'height': None,
                'sex': 'M',
                'activity_level': 'moderate',
                'goal': 'maintain'
            },
            'targets': {
                'calories': None,
                'protein_g': None,
                'carbs_g': None,
                'fat_g': None
            },
            'daily_logs': {}
        }
    
    def save_nutrition_data(self):
        """Guardar datos de nutrición"""
        try:
            with open(self.nutrition_file, 'w', encoding='utf-8') as f:
                json.dump(self.nutrition_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            st.error(f"Error guardando datos de nutrición: {e}")
    
    def calculate_bmr(self, weight: float, height: float, age: int, sex: str) -> float:
        """Calcular tasa metabólica basal usando Mifflin-St Jeor"""
        if sex == 'M':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:  # Female
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        return bmr
    
    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """Calcular gasto energético total diario"""
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        return bmr * activity_multipliers.get(activity_level, 1.55)
    
    def calculate_macros(self, calories: float, goal: str) -> Dict[str, float]:
        """Calcular distribución de macronutrientes"""
        # Distribuciones según objetivo
        macro_distributions = {
            'maintain': {'protein': 0.30, 'carbs': 0.40, 'fat': 0.30},
            'bulk': {'protein': 0.30, 'carbs': 0.50, 'fat': 0.20},
            'cut': {'protein': 0.40, 'carbs': 0.30, 'fat': 0.30}
        }
        
        distribution = macro_distributions.get(goal, macro_distributions['maintain'])
        
        # Calcular gramos (1g proteína = 4 kcal, 1g carbos = 4 kcal, 1g grasa = 9 kcal)
        protein_g = (calories * distribution['protein']) / 4
        carbs_g = (calories * distribution['carbs']) / 4
        fat_g = (calories * distribution['fat']) / 9
        
        return {
            'protein_g': round(protein_g, 1),
            'carbs_g': round(carbs_g, 1),
            'fat_g': round(fat_g, 1)
        }
    
    def render_calculator_tab(self):
        """Renderizar pestaña de calculadora de calorías y macros"""
        st.markdown("## 🧮 Calculadora de Calorías y Macros")
        st.info("Calcula tus necesidades calóricas diarias y distribución de macronutrientes usando la fórmula de Mifflin-St Jeor.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📝 Información Personal")
            
            age = st.number_input("Edad (años)", min_value=15, max_value=100, value=self.nutrition_data['profile'].get('age') or 30)
            weight = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=float(self.nutrition_data['profile'].get('weight') or 70.0), step=0.5)
            height = st.number_input("Altura (cm)", min_value=100, max_value=250, value=self.nutrition_data['profile'].get('height') or 170)
            sex = st.radio("Sexo", ['M', 'F'], index=0 if self.nutrition_data['profile'].get('sex', 'M') == 'M' else 1, horizontal=True)
            
            st.markdown("### 🏃 Nivel de Actividad")
            activity_options = {
                'sedentary': 'Sedentario (poco o ningún ejercicio)',
                'light': 'Ligero (ejercicio 1-3 días/semana)',
                'moderate': 'Moderado (ejercicio 3-5 días/semana)',
                'active': 'Activo (ejercicio 6-7 días/semana)',
                'very_active': 'Muy Activo (ejercicio intenso diario)'
            }
            
            activity_level = st.selectbox(
                "Nivel de actividad",
                list(activity_options.keys()),
                index=list(activity_options.keys()).index(self.nutrition_data['profile'].get('activity_level', 'moderate')),
                format_func=lambda x: activity_options[x]
            )
            
            st.markdown("### 🎯 Objetivo")
            goal_options = {
                'maintain': 'Mantener peso',
                'bulk': 'Ganar masa muscular (volumen)',
                'cut': 'Perder grasa (definición)'
            }
            
            goal = st.selectbox(
                "Tu objetivo",
                list(goal_options.keys()),
                index=list(goal_options.keys()).index(self.nutrition_data['profile'].get('goal', 'maintain')),
                format_func=lambda x: goal_options[x]
            )
            
            if st.button("💾 Guardar Perfil", type="primary"):
                self.nutrition_data['profile'] = {
                    'age': age,
                    'weight': weight,
                    'height': height,
                    'sex': sex,
                    'activity_level': activity_level,
                    'goal': goal
                }
                self.save_nutrition_data()
                st.success("✅ Perfil guardado correctamente")
                st.rerun()
        
        with col2:
            st.markdown("### 📊 Resultados")
            
            # Calcular BMR y TDEE
            bmr = self.calculate_bmr(weight, height, age, sex)
            tdee = self.calculate_tdee(bmr, activity_level)
            
            # Ajustar calorías según objetivo
            if goal == 'bulk':
                target_calories = tdee + 300  # Superávit de 300 kcal
            elif goal == 'cut':
                target_calories = tdee - 500  # Déficit de 500 kcal
            else:
                target_calories = tdee
            
            # Calcular macros
            macros = self.calculate_macros(target_calories, goal)
            
            # Mostrar resultados
            st.markdown(f"**Tasa Metabólica Basal (BMR):** {bmr:.0f} kcal/día")
            st.markdown(f"**Gasto Energético Total (TDEE):** {tdee:.0f} kcal/día")
            st.markdown("---")
            
            st.markdown(f"### 🎯 Objetivo: {goal_options[goal]}")
            st.metric("Calorías Diarias Objetivo", f"{target_calories:.0f} kcal")
            
            st.markdown("### 🍽️ Distribución de Macronutrientes")
            
            col_p, col_c, col_f = st.columns(3)
            with col_p:
                protein_pct = (macros['protein_g'] * 4 / target_calories) * 100
                st.metric("Proteínas", f"{macros['protein_g']:.0f}g", f"{protein_pct:.0f}%")
            with col_c:
                carbs_pct = (macros['carbs_g'] * 4 / target_calories) * 100
                st.metric("Carbohidratos", f"{macros['carbs_g']:.0f}g", f"{carbs_pct:.0f}%")
            with col_f:
                fat_pct = (macros['fat_g'] * 9 / target_calories) * 100
                st.metric("Grasas", f"{macros['fat_g']:.0f}g", f"{fat_pct:.0f}%")
            
            # Guardar targets
            if st.button("✅ Establecer como Objetivos"):
                self.nutrition_data['targets'] = {
                    'calories': round(target_calories),
                    'protein_g': macros['protein_g'],
                    'carbs_g': macros['carbs_g'],
                    'fat_g': macros['fat_g']
                }
                self.save_nutrition_data()
                st.success("🎯 Objetivos nutricionales establecidos")
                st.rerun()
    
    def render_tracking_tab(self):
        """Renderizar pestaña de tracking diario"""
        st.markdown("## 📝 Tracking Diario")
        
        # Verificar si hay objetivos establecidos
        if not self.nutrition_data['targets'].get('calories'):
            st.warning("⚠️ Primero establece tus objetivos en la pestaña 'Calculadora'")
            return
        
        # Seleccionar fecha
        selected_date = st.date_input("Fecha", datetime.date.today())
        date_str = selected_date.strftime('%Y-%m-%d')
        
        # Panel de resumen diario
        daily_log = self.nutrition_data['daily_logs'].get(date_str, {'meals': [], 'total': {'calories': 0, 'protein_g': 0, 'carbs_g': 0, 'fat_g': 0}})
        
        # Mostrar progreso
        st.markdown("### 📊 Resumen del Día")
        targets = self.nutrition_data['targets']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            cal_progress = (daily_log['total']['calories'] / targets['calories']) * 100
            st.metric("Calorías", f"{daily_log['total']['calories']:.0f}/{targets['calories']:.0f}", f"{cal_progress:.0f}%")
        with col2:
            prot_progress = (daily_log['total']['protein_g'] / targets['protein_g']) * 100
            st.metric("Proteínas", f"{daily_log['total']['protein_g']:.0f}g/{targets['protein_g']:.0f}g", f"{prot_progress:.0f}%")
        with col3:
            carb_progress = (daily_log['total']['carbs_g'] / targets['carbs_g']) * 100
            st.metric("Carbohidratos", f"{daily_log['total']['carbs_g']:.0f}g/{targets['carbs_g']:.0f}g", f"{carb_progress:.0f}%")
        with col4:
            fat_progress = (daily_log['total']['fat_g'] / targets['fat_g']) * 100
            st.metric("Grasas", f"{daily_log['total']['fat_g']:.0f}g/{targets['fat_g']:.0f}g", f"{fat_progress:.0f}%")
        
        # Barras de progreso
        st.progress(min(cal_progress / 100, 1.0), text=f"Calorías: {cal_progress:.0f}%")
        
        st.markdown("---")
        
        # Añadir comida
        st.markdown("### ➕ Añadir Comida")
        with st.form("add_meal"):
            meal_name = st.text_input("Nombre de la comida", placeholder="Ej: Pechuga de pollo con arroz")
            
            col_cal, col_prot, col_carb, col_fat = st.columns(4)
            with col_cal:
                meal_calories = st.number_input("Calorías", min_value=0, step=10)
            with col_prot:
                meal_protein = st.number_input("Proteínas (g)", min_value=0.0, step=0.5)
            with col_carb:
                meal_carbs = st.number_input("Carbohidratos (g)", min_value=0.0, step=0.5)
            with col_fat:
                meal_fat = st.number_input("Grasas (g)", min_value=0.0, step=0.5)
            
            submitted = st.form_submit_button("➕ Añadir Comida")
            if submitted and meal_name:
                # Añadir comida al log
                if date_str not in self.nutrition_data['daily_logs']:
                    self.nutrition_data['daily_logs'][date_str] = {'meals': [], 'total': {'calories': 0, 'protein_g': 0, 'carbs_g': 0, 'fat_g': 0}}
                
                meal = {
                    'name': meal_name,
                    'calories': meal_calories,
                    'protein_g': meal_protein,
                    'carbs_g': meal_carbs,
                    'fat_g': meal_fat,
                    'timestamp': datetime.datetime.now().strftime('%H:%M')
                }
                
                self.nutrition_data['daily_logs'][date_str]['meals'].append(meal)
                
                # Actualizar totales
                self.nutrition_data['daily_logs'][date_str]['total']['calories'] += meal_calories
                self.nutrition_data['daily_logs'][date_str]['total']['protein_g'] += meal_protein
                self.nutrition_data['daily_logs'][date_str]['total']['carbs_g'] += meal_carbs
                self.nutrition_data['daily_logs'][date_str]['total']['fat_g'] += meal_fat
                
                self.save_nutrition_data()
                st.success(f"✅ '{meal_name}' añadido")
                st.rerun()
        
        # Mostrar comidas del día
        st.markdown("### 🍽️ Comidas Registradas")
        if daily_log['meals']:
            for idx, meal in enumerate(daily_log['meals']):
                with st.expander(f"{meal['timestamp']} - {meal['name']} ({meal['calories']} kcal)"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"🥩 Proteínas: {meal['protein_g']}g")
                    with col2:
                        st.write(f"🍞 Carbohidratos: {meal['carbs_g']}g")
                    with col3:
                        st.write(f"🥑 Grasas: {meal['fat_g']}g")
                    
                    if st.button(f"🗑️ Eliminar", key=f"delete_meal_{idx}"):
                        # Restar del total
                        self.nutrition_data['daily_logs'][date_str]['total']['calories'] -= meal['calories']
                        self.nutrition_data['daily_logs'][date_str]['total']['protein_g'] -= meal['protein_g']
                        self.nutrition_data['daily_logs'][date_str]['total']['carbs_g'] -= meal['carbs_g']
                        self.nutrition_data['daily_logs'][date_str]['total']['fat_g'] -= meal['fat_g']
                        
                        # Eliminar comida
                        self.nutrition_data['daily_logs'][date_str]['meals'].pop(idx)
                        self.save_nutrition_data()
                        st.rerun()
        else:
            st.info("No hay comidas registradas para este día")
    
    def render_nutrition_tab(self):
        """Renderizar pestaña completa de nutrición"""
        # Subtabs dentro de nutrición
        tab1, tab2 = st.tabs(["🧮 Calculadora", "📝 Tracking Diario"])
        
        with tab1:
            self.render_calculator_tab()
        
        with tab2:
            self.render_tracking_tab()
