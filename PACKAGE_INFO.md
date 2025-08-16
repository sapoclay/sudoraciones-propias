# Sudoraciones Propias v1.2.6 - Paquete Debian

## 📦 Información del Paquete

- **Archivo**: `sudoraciones_1.2.6.deb`
- **Versión**: 1.2.6
- **Arquitectura**: all (compatible con todas las arquitecturas)
- **Tamaño**: ~110KB

## 🚀 Instalación

```bash
# Instalar el paquete
sudo dpkg -i sudoraciones_1.2.6.deb

# Si hay problemas de dependencias, ejecutar:
sudo apt-get install -f
```

## 📋 Dependencias

- python3 (>= 3.8)
- python3-pip
- python3-venv
- curl
- net-tools | iproute2 (herramientas de red estándar)

## 🎯 Características del Paquete

### ✅ Lo que incluye:
- **Aplicación completa** en `/opt/sudoraciones/`
- **Servicio systemd** para ejecución automática
- **Comando global** `sudoraciones` para control fácil
- **Entorno virtual** automático con todas las dependencias
- **Archivo .desktop** para menú de aplicaciones
- **Scripts de instalación/desinstalación** automatizados

### 🏗️ Estructura del paquete:
```
/opt/sudoraciones/           # Aplicación principal
├── main_app.py             # Aplicación Streamlit modular
├── run_app.py              # Launcher optimizado
├── config.json             # Configuración de ejercicios
├── requirements.txt        # Dependencias Python
├── modules/                # Módulos especializados
│   ├── base_trainer.py     # Core del sistema
│   ├── training_plan.py    # Plan de entrenamiento
│   ├── progress_calendar.py # Progreso y calendario
│   ├── statistics.py       # Estadísticas
│   └── info.py            # Información
└── img/                   # Recursos gráficos

/usr/bin/sudoraciones       # Comando global de control
/etc/systemd/system/        # Servicio del sistema
/usr/share/applications/    # Entrada en menú
/usr/share/pixmaps/         # Icono del sistema
```

## 🎮 Uso después de la instalación

### Comandos disponibles:
```bash
# Iniciar la aplicación
sudoraciones start

# Detener la aplicación
sudoraciones stop

# Ver estado
sudoraciones status

# Ver logs en tiempo real
sudoraciones logs

# Reiniciar
sudoraciones restart

# Habilitar inicio automático
sudoraciones enable

# Deshabilitar inicio automático
sudoraciones disable

# Ejecutar en modo desarrollo
sudoraciones run
```

### Acceso web:
- **URL local**: http://localhost:8508
- **Navegador**: Se abrirá automáticamente o acceder manualmente

## 🔧 Servicio del Sistema

El paquete instala un servicio systemd que:
- ✅ Se ejecuta como usuario `sudoraciones` (seguridad)
- ✅ Se reinicia automáticamente si falla
- ✅ Usa entorno virtual aislado
- ✅ Se puede habilitar para inicio automático

## 🗑️ Desinstalación

```bash
# Desinstalar conservando configuración
sudo apt remove sudoraciones

# Desinstalar eliminando todos los datos
sudo apt purge sudoraciones
```

## 🧪 Prueba del Paquete

Se incluye un script de prueba:
```bash
./test_package.sh
```

Este script:
1. Verifica el paquete .deb
2. Lo instala
3. Prueba todas las funcionalidades
4. Verifica que la aplicación responde
5. Muestra información de estado

## 📱 Características de la Aplicación

- **42 ejercicios especializados** organizados por grupos musculares
- **Progresión automática** de 20 semanas con 4 niveles
- **Sistema modular** con 6 módulos especializados
- **Interfaz web moderna** con Streamlit
- **Videos de YouTube** integrados
- **Seguimiento de progreso** con calendario real
- **Estadísticas completas** y métricas de rendimiento
- **Arquitectura escalable** y mantenible

## 🛠️ Información Técnica

- **Framework**: Streamlit
- **Lenguaje**: Python 3.8+
- **Puerto**: 8508
- **Datos**: JSON persistente
- **Entorno**: Virtual environment aislado
- **Servicio**: systemd
- **Plataforma**: Linux (todas las distribuciones con dpkg)

## 📞 Soporte

- **Repositorio**: https://github.com/sapoclay/sudoraciones-propias
- **Versión**: 1.2.6
- **Desarrollador**: EntreunosyCeros

## 🎉 ¡Listo para Entrenar!

Una vez instalado, simplemente ejecuta:
```bash
sudoraciones start
```

Y accede a http://localhost:8508 para comenzar tu entrenamiento personalizado.
