"""Config flow para FGC Trains."""
import logging
import voluptuous as vol
import os

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, LINES, STATIONS, DEFAULT_GTFS_PATH, DEFAULT_UPDATE_INTERVAL
from .gtfs_updater import update_gtfs

_LOGGER = logging.getLogger(__name__)

class FGCTrainsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow para FGC Trains."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Paso inicial de configuración."""
        errors = {}

        if user_input is not None:
            if user_input.get("origin") == user_input.get("destination"):
                errors["base"] = "same_origin_destination"
            else:
                gtfs_path = user_input.get("gtfs_path", DEFAULT_GTFS_PATH)
                
                if not os.path.exists(os.path.join(gtfs_path, "stops.txt")):
                    _LOGGER.info("GTFS no encontrado, descargando...")
                    success = await self.hass.async_add_executor_job(update_gtfs, gtfs_path)
                    if not success:
                        errors["base"] = "gtfs_download_failed"
                
                if not errors:
                    await self.async_set_unique_id(
                        f"{user_input['line']}_{user_input['origin']}_{user_input['destination']}"
                    )
                    self._abort_if_unique_id_configured()
                    
                    return self.async_create_entry(
                        title=f"FGC {user_input['line']}: {STATIONS.get(user_input['origin'])} → {STATIONS.get(user_input['destination'])}",
                        data=user_input,
                    )

        data_schema = vol.Schema({
            vol.Required("line", default="S1"): vol.In(LINES),
            vol.Required("origin", default="TR"): vol.In(STATIONS),
            vol.Required("destination", default="PC"): vol.In(STATIONS),
            vol.Optional("gtfs_path", default=DEFAULT_GTFS_PATH): str,
            vol.Optional("update_interval", default=DEFAULT_UPDATE_INTERVAL): vol.All(
                vol.Coerce(int), vol.Range(min=30, max=300)
            ),
            vol.Optional("auto_update_gtfs", default=True): bool,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Opciones flow."""
        return FGCTrainsOptionsFlow(config_entry)


class FGCTrainsOptionsFlow(config_entries.OptionsFlow):
    """Options flow para FGC Trains."""

    def __init__(self, config_entry):
        """Inicializar options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Gestionar opciones."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "update_interval",
                    default=self.config_entry.data.get("update_interval", DEFAULT_UPDATE_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=300)),
                vol.Optional(
                    "auto_update_gtfs",
                    default=self.config_entry.data.get("auto_update_gtfs", True),
                ): bool,
            }),
        )
