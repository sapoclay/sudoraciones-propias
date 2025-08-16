#!/bin/bash

# Script completo de instalación y verificación de Sudoraciones v1.2.6

echo "========================================================"
echo "🚀 INSTALADOR COMPLETO SUDORACIONES v1.2.6"
echo "========================================================"

DEB_FILE="/var/www/html/SUDORACIONES/sudoraciones_1.2.6.deb"

# Verificar que el archivo .deb existe
if [ ! -f "$DEB_FILE" ]; then
    echo "❌ Error: No se encuentra el archivo $DEB_FILE"
    exit 1
fi

echo "✅ Archivo .deb encontrado: $(ls -lh $DEB_FILE | awk '{print $9, $5}')"
echo ""

# Limpiar instalación previa si existe
echo "🧹 LIMPIANDO INSTALACIÓN PREVIA..."
if dpkg -l | grep -q sudoraciones; then
    echo "📦 Desinstalando versión anterior..."
    sudo systemctl stop sudoraciones 2>/dev/null || true
    sudo apt remove -y sudoraciones 2>/dev/null || true
    sudo apt purge -y sudoraciones 2>/dev/null || true
    echo "✅ Limpieza completada"
else
    echo "✅ No hay instalación previa"
fi

echo ""
echo "📦 INSTALANDO PAQUETE CORREGIDO..."
echo "🔧 Dependencias corregidas: net-tools | iproute2 (en lugar de netstat-nat)"

# Instalar el paquete
sudo dpkg -i "$DEB_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Paquete instalado correctamente"
else
    echo "⚠️ Problemas durante la instalación. Reparando dependencias..."
    sudo apt-get install -f -y
    if [ $? -eq 0 ]; then
        echo "✅ Dependencias reparadas correctamente"
    else
        echo "❌ Error reparando dependencias"
        exit 1
    fi
fi

echo ""
echo "🚀 INICIANDO SERVICIOS..."

# Iniciar el servicio
sudo systemctl start sudoraciones

echo "⏳ Esperando 15 segundos para que inicie completamente..."
sleep 15

echo ""
echo "🔍 VERIFICANDO INSTALACIÓN..."

# Verificar servicio
echo "📋 Estado del servicio:"
if sudo systemctl is-active --quiet sudoraciones; then
    echo "✅ Servicio activo y corriendo"
    sudo systemctl status sudoraciones --no-pager -l
else
    echo "❌ Servicio no está activo"
    sudo systemctl status sudoraciones --no-pager -l
    echo "📋 Logs del servicio:"
    sudo journalctl -u sudoraciones --no-pager -n 20
fi

echo ""
echo "🌐 VERIFICANDO CONECTIVIDAD..."

# Probar conexión HTTP
if curl -s -I http://localhost:8508 | grep -q "200 OK"; then
    echo "✅ Aplicación responde correctamente en http://localhost:8508"
    
    # Obtener título de la página
    PAGE_TITLE=$(curl -s http://localhost:8508 | grep -o '<title>[^<]*' | sed 's/<title>//')
    if [ ! -z "$PAGE_TITLE" ]; then
        echo "✅ Título de la página: $PAGE_TITLE"
    fi
else
    echo "❌ Aplicación no responde en http://localhost:8508"
    echo "🔍 Verificando puerto:"
    ss -tuln | grep 8508 || netstat -tuln | grep 8508 || echo "Puerto 8508 no encontrado"
fi

echo ""
echo "🎮 PROBANDO COMANDO SUDORACIONES..."

# Probar comando
if which sudoraciones >/dev/null; then
    echo "✅ Comando 'sudoraciones' disponible en el sistema"
    echo "📋 Mostrando ayuda del comando:"
    sudoraciones
else
    echo "❌ Comando 'sudoraciones' no encontrado"
fi

echo ""
echo "📂 VERIFICANDO ARCHIVOS INSTALADOS..."

# Verificar archivos
if [ -d "/opt/sudoraciones" ]; then
    echo "✅ Directorio /opt/sudoraciones existe"
    echo "   📁 Archivos principales: $(ls -1 /opt/sudoraciones/*.py 2>/dev/null | wc -l) archivos Python"
    echo "   📁 Módulos: $(ls -1 /opt/sudoraciones/modules/*.py 2>/dev/null | wc -l) módulos"
    echo "   📁 Entorno virtual: $([ -d /opt/sudoraciones/venv_sudoraciones ] && echo "✅ Existe" || echo "❌ No existe")"
else
    echo "❌ Directorio /opt/sudoraciones no existe"
fi

# Verificar usuario
if id sudoraciones >/dev/null 2>&1; then
    echo "✅ Usuario del sistema 'sudoraciones' existe"
else
    echo "❌ Usuario del sistema 'sudoraciones' no existe"
fi

echo ""
echo "========================================================"
echo "🎉 RESUMEN DE LA INSTALACIÓN"
echo "========================================================"

# Resumen final
SERVICE_STATUS=$(sudo systemctl is-active sudoraciones 2>/dev/null || echo "inactive")
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8508 2>/dev/null || echo "000")

echo "📦 Paquete: sudoraciones_1.2.6.deb"
echo "📊 Tamaño: $(ls -lh $DEB_FILE | awk '{print $5}')"
echo "🔧 Servicio: $SERVICE_STATUS"
echo "🌐 HTTP: $HTTP_STATUS"
echo "📡 Puerto: 8508"
echo "🏠 Directorio: /opt/sudoraciones"

if [ "$SERVICE_STATUS" = "active" ] && [ "$HTTP_STATUS" = "200" ]; then
    echo ""
    echo "🎉 ¡INSTALACIÓN EXITOSA!"
    echo "🌐 Accede a: http://localhost:8508"
    echo "🎮 Controla con: sudoraciones [start|stop|status|restart]"
    echo "🚀 Inicio automático: HABILITADO"
    echo ""
    echo "💪 ¡LISTO PARA ENTRENAR!"
else
    echo ""
    echo "⚠️ Instalación completada con problemas"
    echo "🔍 Revisa los logs: sudo journalctl -u sudoraciones"
    echo "🔧 Reinicia manualmente: sudo systemctl restart sudoraciones"
fi

echo "========================================================"
