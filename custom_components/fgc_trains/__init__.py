"""Integración FGC Trains para Home Assistant."""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN, PLATFORMS, DEFAULT_GTFS_PATH, DEFAULT_UPDATE_INTERVAL
from .coordinator import FGCDataCoordinator
from .gtfs_updater import update_gtfs

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Configuración del componente."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Configurar desde config entry."""
    _LOGGER.info(f"Configurando FGC Trains: {entry.data}")
    
    coordinator = FGCDataCoordinator(
        hass,
        entry.data.get("gtfs_path", DEFAULT_GTFS_PATH),
        entry.data.get("origin", "TR"),
        entry.data.get("destination", "PC"),
        entry.data.get("line", "S1"),
        entry.data.get("update_interval", DEFAULT_UPDATE_INTERVAL),
        entry.data.get("auto_update", True)  # ← Nuevo parámetro
    )
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    async def update_gtfs_service(call: ServiceCall):
        """Servicio para actualizar GTFS."""
        _LOGGER.info("Actualizando GTFS manualmente...")
        gtfs_path = entry.data.get("gtfs_path", DEFAULT_GTFS_PATH)
        success = await hass.async_add_executor_job(update_gtfs, gtfs_path)
        
        if success:
            coordinator.last_gtfs_update = None  # Forzar nueva descarga en próxima actualización
            await coordinator.async_refresh()
            _LOGGER.info("✅ GTFS actualizado correctamente")
        else:
            _LOGGER.error("❌ Error actualizando GTFS")
    
    if not hass.services.has_service(DOMAIN, "update_gtfs"):
        hass.services.async_register(DOMAIN, "update_gtfs", update_gtfs_service)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Descargar config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok