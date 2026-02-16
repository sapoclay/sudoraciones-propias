# 💪 Sudoraciones propias 💪

<img width="1073" height="1808" alt="sudoraciones_propias" src="https://github.com/user-attachments/assets/bb27c8a1-1c5b-430b-b3df-f2f8352882f7" />

Sistema personal de entrenamiento en Python + Streamlit con progresión automática, calendario de progreso y módulo de nutrición.

## Descripción

Aplicación modular para planificar y seguir entrenamientos durante 20 semanas, con:

- Plan semanal por niveles
- Seguimiento por ejercicio y por día
- Calendario y estadísticas
- Biblioteca de ejercicios
- Nutrición (calorías y macros)

## 🆕 Novedades de la versión 1.2.8

- Corrección del calendario: la fecha de inicio respeta exactamente el día elegido por el usuario (sin forzar lunes).
- Corrección del mapeo semana-fecha para evitar desplazamientos en vistas semanales.
- Ajustes de estabilidad y tipado en módulos principales.
- Frecuencia de abdominales ajustada por nivel (sin sobrecarga en principiante).
- Referencias y empaquetado `.deb` sincronizados con versión `1.2.8`.

## Progresión de entrenamiento

### Niveles (20 semanas)

- **Nivel 1 (Semanas 1-4):** adaptación inicial.
- **Nivel 2 (Semanas 5-8):** incremento de frecuencia.
- **Nivel 3 (Semanas 9-12):** incremento de volumen.
- **Nivel 4+ (Semanas 13-20):** plan avanzado.

### Frecuencia de abdominales por nivel

- **Nivel 1:** 2 días/semana
- **Nivel 2:** 3 días/semana
- **Nivel 3:** 4 días/semana
- **Nivel 4+:** 5 días/semana

## Instalación (.deb)

```bash
wget https://github.com/sapoclay/sudoraciones-propias/releases/download/v1.2.8/sudoraciones_1.2.8_amd64.deb
sudo dpkg -i sudoraciones_1.2.8_amd64.deb
sudo apt-get install -f
```

### Comandos del launcher

```bash
sudoraciones start
sudoraciones stop
sudoraciones restart
sudoraciones status
sudoraciones log
```

Si el puerto `8508` está ocupado, usa `sudoraciones restart`.

## Uso desde código fuente

```bash
git clone https://github.com/sapoclay/sudoraciones-propias.git
cd sudoraciones-propias
python3 run_app.py
```

Acceso web:

- Local: `http://localhost:8508`
- Red: `http://0.0.0.0:8508`

## Pestañas de la aplicación

- 🏋️ Plan de Entrenamiento
- 📊 Progreso
- 📈 Estadísticas
- 📚 Biblioteca de Ejercicios
- 🍎 Nutrición
- ℹ️ Información

## Estructura principal

```text
modules/
├── __init__.py
├── base_trainer.py
├── exercise_library.py
├── info.py
├── nutrition.py
├── progress_calendar.py
├── statistics.py
└── training_plan.py
```

Archivos clave:

- `main_app.py`: aplicación principal
- `run_app.py`: launcher
- `config.json`: configuración de ejercicios y plan
- `progress_data.json`: progreso del usuario
- `nutrition_data.json`: datos de nutrición

## Requisitos

- Python 3.12+
- Navegador moderno
- Linux/macOS/Windows
- Internet (para videos de YouTube)

## Solución rápida de problemas

### La app no inicia

1. Verifica Python 3.12+.
2. Ejecuta desde la raíz del proyecto: `python3 run_app.py`.

### Dependencias

```bash
source venv_sudoraciones/bin/activate
pip install -r requirements.txt
```

---

Desarrollado con Python y Streamlit por entreunosyceros.
