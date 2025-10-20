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
    
    try:
        _LOGGER.info(f"Descargando GTFS desde {GTFS_URL}...")
        
        response = requests.get(GTFS_URL, timeout=30)
        response.raise_for_status()
        
        temp_file = f"/tmp/gtfs_fgc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        
        _LOGGER.info(f"Descarga completada. Extrayendo a {gtfs_path}...")
        
        if os.path.exists(gtfs_path):
            backup_path = f"{gtfs_path}_backup_{datetime.now().strftime('%Y%m%d')}"
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.copytree(gtfs_path, backup_path)
            _LOGGER.info(f"Backup creado: {backup_path}")
            shutil.rmtree(gtfs_path)
        
        os.makedirs(gtfs_path, exist_ok=True)
        with zipfile.ZipFile(temp_file, 'r') as zip_ref:
            zip_ref.extractall(gtfs_path)
        
        os.remove(temp_file)
        cleanup_old_backups(gtfs_path)
        
        _LOGGER.info("✅ GTFS actualizado correctamente")
        return True
        
    except Exception as e:
        _LOGGER.error(f"❌ Error actualizando GTFS: {e}", exc_info=True)
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
            _LOGGER.info(f"Backup antiguo eliminado: {backup}")
            
    except Exception as e:
        _LOGGER.warning(f"Error limpiando backups: {e}")
