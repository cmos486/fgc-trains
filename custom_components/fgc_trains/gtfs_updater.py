"""Actualizador de GTFS."""
import os
import logging
import requests
import zipfile
import shutil
from datetime import datetime

from .const import GTFS_URL

_LOGGER = logging.getLogger(__name__)

def update_gtfs(gtfs_path=None):
    """Descargar y actualizar GTFS."""
    if gtfs_path is None:
        from .const import DEFAULT_GTFS_PATH
        gtfs_path = DEFAULT_GTFS_PATH
    
    temp_dir = None
    backup_path = None
    
    try:
        _LOGGER.info(f"🚆 Iniciando descarga GTFS desde {GTFS_URL}...")
        
        # Descargar a archivo temporal
        response = requests.get(GTFS_URL, timeout=30)
        response.raise_for_status()
        
        temp_file = f"/tmp/gtfs_fgc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        
        _LOGGER.info(f"✅ Descarga completada ({len(response.content)} bytes)")
        
        # Extraer a directorio temporal primero
        temp_dir = f"/tmp/gtfs_fgc_extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(temp_dir, exist_ok=True)
        
        with zipfile.ZipFile(temp_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        _LOGGER.info(f"✅ Archivos extraídos a temporal")
        
        # Verificar que se extrajeron archivos importantes
        required_files = ['trips.txt', 'stops.txt', 'stop_times.txt']
        for req_file in required_files:
            if not os.path.exists(os.path.join(temp_dir, req_file)):
                raise Exception(f"Archivo requerido no encontrado: {req_file}")
        
        # Ahora sí, hacer backup y reemplazar
        if os.path.exists(gtfs_path):
            backup_path = f"{gtfs_path}_backup_{datetime.now().strftime('%Y%m%d')}"
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.move(gtfs_path, backup_path)
            _LOGGER.info(f"📦 Backup creado: {backup_path}")
        
        # Mover archivos del temporal al destino final
        shutil.move(temp_dir, gtfs_path)
        
        # Limpiar archivo zip temporal
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        cleanup_old_backups(gtfs_path)
        
        _LOGGER.info("✅ GTFS actualizado correctamente")
        return True
        
    except Exception as e:
        _LOGGER.error(f"❌ Error actualizando GTFS: {e}", exc_info=True)
        
        # Restaurar backup si existe y el destino está vacío/corrupto
        if backup_path and os.path.exists(backup_path) and not os.path.exists(gtfs_path):
            _LOGGER.warning(f"🔄 Restaurando backup desde {backup_path}")
            shutil.copytree(backup_path, gtfs_path)
            _LOGGER.info("✅ Backup restaurado")
        
        # Limpiar temporales
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        return False

def cleanup_old_backups(gtfs_path, keep=3):
    """Limpiar backups antiguos."""
    try:
        parent_dir = os.path.dirname(gtfs_path)
        base_name = os.path.basename(gtfs_path)
        
        backups = sorted([
            f for f in os.listdir(parent_dir)
            if f.startswith(f"{base_name}_backup_")
        ], reverse=True)
        
        for backup in backups[keep:]:
            backup_path = os.path.join(parent_dir, backup)
            shutil.rmtree(backup_path)
            _LOGGER.info(f"🗑️ Backup antiguo eliminado: {backup}")
            
    except Exception as e:
        _LOGGER.warning(f"⚠️ Error limpiando backups: {e}")
