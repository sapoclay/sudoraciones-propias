# 💪 Sudoraciones propias 💪 - Sistema de entrenamiento personal

<img width="200" height="200" alt="logo" src="https://github.com/user-attachments/assets/7993007a-557c-4e8f-8613-73968ad25b74" />

## 🎯 Descripción
Esto es un sistema básico para llevar un control de entrenamiento, y de paso practicar un poco Python y Streamlit.

## 🏋️ Sistema de progresión inteligente

### 📈 **Niveles de entrenamiento (20 Semanas)**

#### 🟢 **Nivel 1 - Principiante (Semanas 1-4)**
- **Entrenamientos:** 4 días por semana (Lunes, Miércoles, Viernes, Sábado)
- **Descanso:** 3 días (Martes, Jueves, Domingo)
- **Enfoque:** Adaptación suave y técnica correcta
- **Abdominales:** Solo ejercicios básicos

#### 🟡 **Nivel 2 - Intermedio (Semanas 5-8)**
- **Entrenamientos:** 5 días por semana (se añade Martes)
- **Descanso:** 2 días (Miércoles, Domingo)
- **Enfoque:** Incremento de frecuencia e intensidad
- **Abdominales:** Mantiene ejercicios básicos

#### 🟠 **Nivel 3 - Avanzado (Semanas 9-12)**
- **Entrenamientos:** 5 días por semana intensificados
- **Descanso:** 2 días (Miércoles, Domingo)
- **Enfoque:** Incremento de volumen por sesión
- **Abdominales:** Introduce ejercicios avanzados

#### 🔴 **Nivel 4+ - Experto (Semanas 13-20)**
- **Entrenamientos:** 6 días por semana (Lunes-Sábado)
- **Descanso:** 1 día (Solo Domingo)
- **Enfoque:** Máxima intensidad y plan de élite
- **Abdominales:** Alternancia completa básicos/avanzados

### 📅 **Distribución semanal por nivel**

| Día | Nivel 1 | Nivel 2 | Nivel 3 | Nivel 4+ |
|-----|---------|---------|---------|----------|
| **Lunes** | ✅ Entreno | ✅ Entreno | ✅ Entreno | ✅ Entreno |
| **Martes** | 🛌 Descanso | ✅ Entreno | ✅ Entreno | ✅ Entreno |
| **Miércoles** | ✅ Entreno | 🛌 Descanso | 🛌 Descanso | ✅ Entreno |
| **Jueves** | 🛌 Descanso | ✅ Entreno | ✅ Entreno | ✅ Entreno |
| **Viernes** | ✅ Entreno | ✅ Entreno | ✅ Entreno | ✅ Entreno |
| **Sábado** | ✅ Entreno | ✅ Entreno | ✅ Entreno | ✅ Entreno |
| **Domingo** | 🛌 Descanso | 🛌 Descanso | 🛌 Descanso | 🛌 Descanso |

### 💪 **Principios de progresión**
- **Recuperación garantizada:** Siempre al menos 1 día de descanso
- **Progresión gradual:** De 4 a 6 entrenamientos semanales
- **Cardio progresivo:** De 2 a 4+ sesiones semanales según nivel
- **Adaptación inteligente:** Incremento controlado de la carga
- **Sostenibilidad:** Programa de 20 semanas sin estancamiento

## 🔧 Configuración manual (Opcional) o personalizado optimizado para principiantes y expertos, con progresión automática inteligente y arquitectura modular.

## 🚀 Instalación paquete .deb

El usuario puede descargarse el paquete .deb desde la página de lanzamientos, o escribiendo en la terminal:
```bash
   wget https://github.com/sapoclay/sudoraciones-propias/releases/download/v1.2.1/sudoraciones_1.2.1_amd64.deb
```

Después solo hay que instalar el paquete .deb escribiendo en una terminal el comando:
```bash
   sudo dpkg -i sudoraciones_1.2.1_amd64.deb
```
En caso de que encontremos dependencias faltantes, en la misma terminal solo es necesario escribir:
```bash
   sudo apt-get install -f  
```

Tras la instalación, ya se puede buscar el lanzador en el sistema.

<img width="765" height="243" alt="lanzador-sudoraciones" src="https://github.com/user-attachments/assets/f4701246-eafe-435c-a340-3141425c8e82" />

### 🖱️ Control del programa desde el icono

El programa se puede **iniciar, parar o reiniciar** haciendo **clic derecho** sobre el icono del programa. Aparecerán las siguientes opciones:

- **▶️ Iniciar SUDORACIONES**: Ejecuta la aplicación web
- **⏹️ Parar SUDORACIONES**: Detiene todos los procesos del programa  
- **🔄 Reiniciar SUDORACIONES**: Para y vuelve a iniciar la aplicación

Esta funcionalidad permite un **control completo** del programa sin necesidad de usar la terminal.

### Utilizar el programa Python

Tras descargar el repositorio con:

```bash
   git clone https://github.com/sapoclay/sudoraciones-propias.git
```

Tras la descarga, solo hay que meterse en el directorio:
```bash
   cd sudoraciones-propias
```
Después se puede iniciar el programa con:

```bash
# Método principal (recomendado)
python3 run_app.py

# O con permisos de ejecución
./run_app.py
```

**La aplicación utiliza arquitectura modular optimizada** - Código organizado por pestañas con mejor rendimiento y mantenibilidad.

## 📱 Acceso a la Aplicación

Una vez iniciada, accede desde tu navegador:
- **URL Local**: http://localhost:8508
- **URL Externa**: http://0.0.0.0:8508

## 🗂️ Archivos del sistema

### Archivos principales
- `run_app.py` - Launcher principal automático
- `main_app.py` - Aplicación modular principal
- `config.json` - Configuración de ejercicios y planes
- `progress_data.json` - Datos de progreso del usuario

### Archivos de configuración
- `requirements.txt` - Dependencias de Python
- `.streamlit/config.toml` - Configuración de Streamlit (opcional)

### Recursos
- `img/` - Imágenes y logos (opcional)
- `modules/` - Módulos de la aplicación modular

## 🏗️ Arquitectura modular

### Estructura de módulos
```
modules/
├── __init__.py              # Configuración del paquete
├── base_trainer.py         # Funcionalidad core del sistema
├── training_plan.py        # Lógica del plan de entrenamiento
├── progress_calendar.py    # Progreso y calendario
├── statistics.py           # Análisis y estadísticas
└── info.py                # Información del programa
```

### Beneficios de la modularización
- ✅ **Separación clara de responsabilidades** por pestaña
- ✅ **Código más legible** y fácil de mantener
- ✅ **Facilita el desarrollo en equipo**
- ✅ **Testing individual** de cada módulo
- ✅ **Reutilización de código** entre módulos

## 💪 Características principales

### Entrenamiento
- **42 ejercicios especializados** organizados en 8 grupos musculares con progresión automática
- **Progresión automática inteligente** hasta 20 semanas
- **Sistema de 4 niveles** con días de descanso adaptativos
- **Seguimiento automático** por ejercicio individual
- **Distribución inteligente de abdominales** (básicos vs avanzados)

### Tecnología
- **Streamlit 1.47.1** para la interfaz web
- **Python 3.12** como base
- **Entorno virtual automático** (venv_sudoraciones)
- **Interfaz completamente en español**

### Funcionalidades
- 🎥 **Videos YouTube integrados** (normales + Shorts)
- 📅 **Calendario inteligente** con porcentajes automáticos
- 📊 **Estadísticas avanzadas** con gráficos Plotly
- 💡 **Instrucciones detalladas** y consejos de técnica
- 🏆 **Sistema de progresión** automático e inteligente

## 📊 Grupos musculares y progresión

### 🎯 **Distribución de ejercicios (26 Total)**

#### Pecho (4 ejercicios)
- Press de Banca con Mancuernas
- Press de Banca con Barra
- Aperturas con Mancuernas
- Press Inclinado con Barra

#### Espalda (2 ejercicios)
- Remo con Mancuernas
- Peso Muerto con Mancuernas

#### Hombros (3 ejercicios)
- Press Militar con Mancuernas
- Elevaciones Laterales
- Elevaciones Frontales

#### Brazos (7 ejercicios)
- Curl de Bíceps
- Curl Martillo
- Extensiones de Tríceps
- Fondos en Silla
- Curl de Muñeca (antebrazo)
- Curl de Muñeca Inverso (antebrazo)
- Pronación/Supinación con Mancuerna (antebrazo)

> Nota: en los días de brazos, se muestra automáticamente solo 1 ejercicio de antebrazo alternado de forma inteligente. La progresión por nivel ajusta series y repeticiones: Nivel 1 (1×8-10), Nivel 2 (1×10-12), Nivel 3 (2×10-12), Nivel 4+ (2×12-15).

#### Piernas (3 ejercicios)
- Sentadillas con Mancuernas
- Zancadas con Mancuernas
- Sentadillas Búlgaras

#### Gemelos (2 ejercicios)
- Elevaciones de Gemelos de Pie
- Elevaciones de Gemelos Sentado

#### Abdominales (4 ejercicios divididos en básicos y avanzados)
**Abs básicos (Nivel 1-2):**
- Abdominales Tradicionales
- Plancha

**Abs avanzados (Nivel 3+):**
- Abdominales Bajas
- Abdominales Laterales

#### Cardio (1 ejercicio)
- Bicicleta Estática

**📈 Distribución de cardio por semana:**
- **Semanas 1-2**: 2 sesiones (miércoles + viernes)
- **Semanas 3-4**: 3 sesiones (lunes + miércoles + viernes)  
- **Semanas 5+**: Cardio distribuido inteligentemente según nivel de progresión

## 🔄 Funcionamiento del programa

### 📅 Sistema de progresión semanal

El programa utiliza un **sistema inteligente de progresión por niveles** que cambia automáticamente cada 4 semanas:

#### 🟢 **Nivel 1 - Principiante (Semanas 1-4)**
- **Objetivo**: Adaptación inicial al entrenamiento personalizado
- **Características**: 
  - Plan básico predefinido en `config.json`
  - Cada semana tiene ejercicios específicos diferentes
  - Enfoque en aprender la técnica correcta
  - Volumen moderado para evitar agotamiento

#### 🟡 **Nivel 2 - Intermedio (Semanas 5-8)**
- **Objetivo**: Incremento de frecuencia e intensidad
- **Características**:
  - Generación automática de entrenamientos
  - Se añaden grupos musculares complementarios
  - Mayor frecuencia de entrenamiento
  - Intensificación progresiva

#### 🟠 **Nivel 3 - Avanzado (Semanas 9-12)**
- **Objetivo**: Incremento de volumen de entrenamiento
- **Características**:
  - Se añaden días adicionales de entrenamiento
  - Conversión de días de descanso en días activos
  - Mayor variedad de ejercicios
  - Entrenamientos más complejos

#### 🔴 **Nivel 4+ - Experto (Semanas 13+)**
- **Objetivo**: Máxima intensidad y rendimiento
- **Características**:
  - Plan avanzado completo
  - Combinación de intensidad y volumen
  - Entrenamientos de élite personalizados
  - Progresión continua sin límite

### 🔄 **Cambios entre semanas**

**¿Qué sucede al cambiar de semana?**

1. **Semanas 1-4**: Cada semana tiene un **plan fijo diferente** definido en la configuración
2. **Semanas 5+**: El sistema **genera automáticamente** nuevos entrenamientos usando algoritmos de progresión
3. **Ciclo base**: Se repite cada 4 semanas pero con **mayor intensidad** en cada nivel
4. **Sin reseteo**: Tu progreso se mantiene - ejercicios completados, estadísticas y calendario se conservan

### 🎯 **Control de progresión**

#### **Progresión automática**:
- El programa avanza automáticamente cada semana
- Los entrenamientos se intensifican progresivamente
- No es necesaria intervención manual

#### **Control manual**:
- Selector de semana en la barra lateral (1-20)
- Puedes revisar semanas pasadas
- Posibilidad de saltar a semanas futuras
- Información detallada de cada nivel

### 📊 **Seguimiento del progreso**

#### **Por ejercicio**:
- Marca individual cada ejercicio como "Completado"
- Sistema inteligente: día completado al 80% de ejercicios
- Flexibilidad para desmarcar si es necesario

#### **Por día**:
- Colores en el calendario según porcentaje completado:
  - 🟢 Verde: 100% completado
  - 🟡 Amarillo: 80-99% completado  
  - 🟠 Naranja: 1-79% completado
  - ⚪ Blanco: 0% completado

#### **🆕 Vistas del Calendario por Semana**:
- **Vista Acumulativa** (por defecto): Muestra progreso combinado de todas las semanas
- **Vista por Semana Específica**: Filtra solo el progreso de una semana en particular
- **Días de descanso adaptativos**: Cambian según el nivel de dificultad de cada semana
- **Independencia entre semanas**: El progreso de una semana no afecta a otras
- **Navegación temporal**: Puedes revisar el progreso de semanas anteriores

#### **Funcionalidades del Calendario**:
- **Semanas independientes**: Cada semana tiene su propio plan de entrenamiento
- **Días de descanso dinámicos**: Cambian según el nivel (Principiante: 3 días, Experto: 1 día)
- **Porcentajes precisos**: Se calculan solo con ejercicios de la semana seleccionada
- **Historial completo**: Mantiene el registro de todas las semanas completadas

#### **Estadísticas globales**:
- Total de entrenamientos realizados
- Rachas de entrenamiento consecutivas
- Gráficos de progreso mensual
- Recomendaciones personalizadas

### 🏋️ **Métodos de intensificación**

El sistema utiliza tres métodos para intensificar los entrenamientos:

1. **Frecuencia**: Añade grupos musculares complementarios a días existentes
2. **Volumen**: Convierte días de descanso en días de entrenamiento activo
3. **Avanzado**: Combina ambos métodos para máxima intensidad

### 💾 **Persistencia de datos**

- **Configuración**: `config.json` - Ejercicios, planes de entrenamiento, URLs de videos
- **Progreso**: `progress_data.json` - Ejercicios completados, estadísticas, historial
- **Sincronización**: Los datos se guardan automáticamente entre sesiones
- **Respaldo**: El progreso nunca se pierde al cambiar de semana o nivel

## 🎯 Metodología de entrenamiento

### Principios a seguir
- **Alta Intensidad**: Cada serie hasta el fallo muscular
- **Frecuencia Óptima**: 3-4 entrenamientos por semana
- **Sesiones Efectivas**: Sesiones enfocadas e intensas
- **Progresión Gradual**: Incremento constante de peso/repeticiones
- **Descanso Completo**: Recuperación total entre entrenamientos

### Sistema de progresión
1. **🟢 Nivel 1 (Semanas 1-4)**: Plan básico de adaptación
2. **🟡 Nivel 2 (Semanas 5-8)**: Incremento de frecuencia
3. **🟠 Nivel 3 (Semanas 9-12)**: Incremento de volumen
4. **🔴 Nivel 4 (Semanas 13-16)**: Plan avanzado completo
5. **🔥 Nivel 5+ (Semanas 17+)**: Entrenamiento de élite

## 🔄 Sistema de seguimiento

### Automático
- **Progreso por ejercicio**: Marca individual cada ejercicio
- **Cálculo inteligente**: Un día se considera completado al 80% de ejercicios
- **Calendario visual**: Colores que indican nivel de progreso
- **Estadísticas automáticas**: Sin configuración manual necesaria

### Manual
- Solo necesitas marcar ejercicios como "Completado"
- El sistema calcula automáticamente todo lo demás

## 📱 Guía de uso práctica

### 🚀 **Primer uso**
1. **Iniciar aplicación**: Ejecuta `python3 run_app.py`
2. **Acceder**: Abre http://localhost:8508 en tu navegador
3. **Revisar barra lateral**: Verifica que estás en "Semana 1" (🟢 Principiante)
4. **Explorar pestañas**: Familiarízate con las 4 secciones principales

### 🏋️ **Durante el entrenamiento**
1. **Pestaña "plan de entrenamiento"**:
   - Ve los ejercicios del día actual
   - Mira los videos tutorial haciendo clic en "ℹ️ Detalles"
   - Lee las instrucciones y consejos de técnica
   - Marca como "✅ Completado" cada ejercicio que hagas

2. **Seguimiento en tiempo real**:
   - El sistema calcula automáticamente tu progreso diario
   - Verde = día completado, Amarillo = parcial, etc.
   - Las estadísticas se actualizan instantáneamente

### 📅 **Progresión semanal**
1. **Semana actual**: Se muestra en la barra lateral
2. **Cambio automático**: Cada 7 días reales o manual con el selector
3. **Nuevos entrenamientos**: El sistema genera automáticamente nuevos ejercicios (semana 5+)
4. **Sin pérdida de datos**: Tu progreso anterior se mantiene siempre

### 📊 **Monitorización del progreso**
1. **Pestaña "Progreso"**: 
   - Calendario visual con tu historial completo
   - Estadísticas de días entrenados
   - Rachas de entrenamiento consecutivas

2. **Pestaña "Estadísticas"**:
   - Gráficos de progreso mensual
   - Recomendaciones personalizadas
   - Análisis de rendimiento

### ⚙️ **Personalización**
1. **Opciones de vista** (barra lateral):
   - ☑️ Mostrar videos: Activa/desactiva reproductores YouTube
   - ☑️ Mostrar instrucciones: Detalles de cada ejercicio
   - ☑️ Mostrar consejos: Tips de técnica y seguridad

2. **Configurar videos**:
   - Haz clic en "ℹ️ Detalles" de cualquier ejercicio
   - Sección "🔗 Configurar Video Tutorial"
   - Pega URL de YouTube (normal o Shorts)
   - Haz clic en "💾 Guardar URL"

3. **Gestión del progreso**:
   - 📊 Vista del progreso actual en la barra lateral
   - 🗑️ Botón de reinicio completo con confirmación de seguridad
   - ⚠️ Advertencias claras sobre acciones irreversibles

### 🔄 **Casos de uso comunes**

#### **"¿Qué hago hoy?"**
→ Ve a "Plan de Entrenamiento", mira los ejercicios destacados para hoy

#### **"¿Cómo va mi progreso?"**
→ Ve a "Progreso" para el calendario o "Estadísticas" para gráficos detallados

#### **"¿Cómo hago este ejercicio?"**
→ Haz clic en "ℹ️ Detalles" del ejercicio para ver video e instrucciones

#### **"Quiero ver una semana futura"**
→ Usa el selector de semana en la barra lateral (1-20)

#### **"No puedo entrenar hoy"**
→ No marques ejercicios. El sistema registra automáticamente como día de descanso

#### **"Me equivoqué marcando un ejercicio"**
→ Vuelve a hacer clic en el checkbox para desmarcarlo

#### **"Quiero empezar de nuevo desde cero"**
→ Ve a la barra lateral → "🔄 Gestión de Progreso" → "🗑️ Reiniciar Todo el Progreso"

### 🔄 **Gestión del progreso**

#### **Reinicio completo**
La aplicación incluye una función de reinicio completo que permite:
- **Eliminar todos los ejercicios completados** 
- **Borrar el historial del calendario**
- **Resetear todas las estadísticas y rachas**
- **Volver a la Semana 1** (🟢 Principiante)
- **Mantener la configuración de ejercicios** y videos

#### **Cómo reiniciar el progreso**
1. **Ir a la barra lateral** → Sección "🔄 Gestión de Progreso"
2. **Hacer clic** en "🗑️ Reiniciar Todo el Progreso"
3. **Confirmar la acción** (⚠️ Es irreversible)
4. **El sistema limpia todo** y vuelve al estado inicial

**⚠️ Importante**: Esta acción es **irreversible**. Una vez confirmada, todo el progreso se perderá permanentemente.

### 🎯 **Consejos para máximo rendimiento**
1. **Consistencia**: Mejor entrenar 15 min diarios que 2 horas esporádicas
2. **Técnica primero**: Mira los videos antes de aumentar peso
3. **Escucha tu cuerpo**: Usa días de descanso cuando sea necesario
4. **Progresión gradual**: Confía en el sistema de 20 semanas
5. **Registro constante**: Marca ejercicios inmediatamente después de hacerlos

## 🏋️ Equipo necesario

### Mínimo recomendado
- 2 Mancuernas de 10kg
- 1 Mancuerna de 12kg
- 1 Banco de pectoral con 30kg
- 1 Bicicleta estática
- Espacio en el suelo para ejercicios de core

## 📋 Requisitos del sistema

- **Python 3.12+**
- **Sistema operativo**: Linux, Mac, Windows
- **Navegador web moderno**
- **Conexión a internet** (para videos de YouTube)

## 🔧 Solución de problemas

### La aplicación no inicia
1. Verifica que Python 3.12+ esté instalado
2. Ejecuta `python3 run_app.py` desde el directorio del proyecto
3. Comprueba que todos los archivos estén presentes

### Error de dependencias
El launcher instala automáticamente las dependencias, pero si hay problemas:
```bash
source venv_sudoraciones/bin/activate
pip install -r requirements.txt
```

### Puerto ocupado
Si el puerto 8508 está ocupado, el sistema intentará automáticamente terminar procesos previos.

## 🏆 Resultados Esperados

### Semanas 1-4 (Principiante)
- Adaptación al ejercicio regular
- Mejora de la técnica básica
- Establecimiento de rutina
- Aumento inicial de resistencia

### Semanas 5-8 (Intermedio)
- Incremento notable de fuerza
- Mejor definición muscular
- Mayor resistencia cardiovascular
- Confianza en ejercicios complejos

### Semanas 9-12 (Avanzado)
- Desarrollo muscular visible
- Mejora significativa de la forma física
- Capacidad para entrenamientos intensos
- Dominio técnico avanzado

### Semanas 13-20 (Experto)
- Transformación física completa
- Fuerza y resistencia de élite
- Hábitos de entrenamiento consolidados
- Capacidad de mantener resultados

---

**💪 ¡Comienza tu transformación con SUDORACIONES propias!**

*Desarrollado con un poco de ☕ y 🚬 usando Python y Streamlit - Sistema de entrenamiento inteligente*
