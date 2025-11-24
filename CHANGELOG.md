# Changelog - Sudoraciones Propias

## Versión 1.2.7 (2025-11-24)

### 🆕 Nuevas Funcionalidades

#### 📚 Biblioteca de Ejercicios Extendida
- **25 nuevos ejercicios añadidos**:
  - 7 ejercicios de calentamiento (rotaciones, círculos, jumping jacks, etc.)
  - 10 ejercicios de estiramiento (pectorales, dorsales, isquiotibiales, etc.)
  - 8 ejercicios de movilidad (gato-camello, bird dog, 90/90 hip switch, etc.)
- **Total de ejercicios: 67** (anteriormente 42)
- **Nueva pestaña**: "📚 Biblioteca de Ejercicios"
  - Filtros por nivel de dificultad
  - Filtros por equipamiento necesario
  - Filtros por categoría (calentamiento, entrenamiento, estiramiento, movilidad)
  - Búsqueda por nombre de ejercicio
  - Tarjetas expandibles con información completa
  - Videos de YouTube integrados

#### 🍎 Módulo de Nutrición
- **Nueva pestaña**: "🍎 Nutrición"
- **Calculadora de Calorías**:
  - Fórmula de Mifflin-St Jeor para cálculo de BMR
  - Ajuste por nivel de actividad
  - Objetivos personalizables (mantener, volumen, definición)
- **Calculadora de Macros**:
  - Distribución automática de proteínas, carbohidratos y grasas
  - Adaptada según objetivo seleccionado
- **Tracking Diario de Comidas**:
  - Registro de comidas con macronutrientes
  - Seguimiento de progreso vs objetivos
  - Barras de progreso visuales
  - Historial por fecha
  - Persistencia en archivo JSON

### 🐛 Correcciones de Errores
- Corregidos errores de sintaxis en diccionarios de `training_plan.py`
- Solucionado error de valores `None` en inputs numéricos de nutrición
- Corregida indentación en módulo de nutrición
- Añadidas comas faltantes en definiciones de ejercicios

### 📝 Documentación
- Actualizada documentación de todos los ejercicios existentes
- Añadidas instrucciones detalladas para los 25 nuevos ejercicios
- Añadidos consejos de seguridad para todos los ejercicios nuevos

### 📦 Empaquetado
- Paquete .deb actualizado a versión 1.2.7
- Tamaño del paquete: ~120KB (comprimido con xz)

---

## Versión 1.2.6 (Anterior)

### Funcionalidades Principales
- Sistema de progresión de 20 semanas
- 42 ejercicios especializados
- 4 niveles de dificultad
- Mapeo de calendario inteligente
- Tracking de progreso por semana
- Estadísticas acumulativas
- Videos de YouTube integrados
- Interfaz completamente en español

---

## Instalación

Para instalar la versión 1.2.7:

```bash
sudo dpkg -i sudoraciones_1.2.7_amd64.deb
sudo apt-get install -f  # Si hay dependencias faltantes
```

Para ejecutar:
```bash
sudoraciones
```

O desde el menú de aplicaciones: "Sudoraciones Propias"
