"""Plataforma de sensores para FGC Trains."""
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Configurar sensores desde config entry (UI)."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        FGCMainSensor(coordinator, entry),
        FGCIndividualTrainSensor(coordinator, entry, 1),
        FGCIndividualTrainSensor(coordinator, entry, 2),
        FGCIndividualTrainSensor(coordinator, entry, 3),
        FGCIndividualTrainSensor(coordinator, entry, 4),
    ]
    
    async_add_entities(sensors)

class FGCMainSensor(CoordinatorEntity, SensorEntity):
    """Sensor principal de FGC."""

    def __init__(self, coordinator, entry):
        """Inicializar sensor."""
        super().__init__(coordinator)
        self._entry = entry
        line = entry.data["line"]
        origin = entry.data["origin"]
        dest = entry.data["destination"]
        self._attr_name = f"FGC {line} {origin}-{dest}"
        self._attr_unique_id = f"{entry.entry_id}_main"
        self._attr_icon = "mdi:train"

    @property
    def state(self):
        """Estado del sensor."""
        if not self.coordinator.data or "trains" not in self.coordinator.data:
            return None
        
        trains = self.coordinator.data["trains"]
        if trains and len(trains) > 0:
            return trains[0]["time"]
        return "No hay trenes"

    @property
    def extra_state_attributes(self):
        """Atributos del sensor."""
        if not self.coordinator.data or "trains" not in self.coordinator.data:
            return {}
        
        trains = self.coordinator.data["trains"]
        
        attrs = {
            "line": self._entry.data["line"],
            "origin": self._entry.data["origin"],
            "destination": self._entry.data["destination"],
            "origin_name": self.get_station_name(self._entry.data["origin"]),
            "destination_name": self.get_station_name(self._entry.data["destination"]),
            "total_departures_today": self.coordinator.data.get("total", 0),
            "last_update": self.coordinator.data.get("last_update"),
            "trip_duration": "~50 min"
        }
        
        for i in range(min(4, len(trains))):
            train = trains[i]
            num = i + 1
            attrs[f"train_{num}_time"] = train["time"]
            attrs[f"train_{num}_minutes"] = train["minutes_until"]
        
        return attrs
    
    def get_station_name(self, code):
        """Obtener nombre de estación."""
        from .const import STATIONS
        return STATIONS.get(code, code)

class FGCIndividualTrainSensor(CoordinatorEntity, SensorEntity):
    """Sensor individual para cada tren."""

    def __init__(self, coordinator, entry, train_number):
        """Inicializar sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._train_number = train_number
        line = entry.data["line"]
        self._attr_name = f"FGC {line} Tren {train_number}"
        self._attr_unique_id = f"{entry.entry_id}_train_{train_number}"
        self._attr_icon = "mdi:train-car"

    @property
    def state(self):
        """Estado del sensor."""
        if not self.coordinator.data or "trains" not in self.coordinator.data:
            return None
        
        trains = self.coordinator.data["trains"]
        if trains and len(trains) >= self._train_number:
            return trains[self._train_number - 1]["time"]
        return None

    @property
    def extra_state_attributes(self):
        """Atributos del sensor."""
        if not self.coordinator.data or "trains" not in self.coordinator.data:
            return {}
        
        trains = self.coordinator.data["trains"]
        
        attrs = {
            "train_number": self._train_number,
            "line": self._entry.data["line"],
            "origin": self._entry.data["origin"],
            "destination": self._entry.data["destination"],
        }
        
        if trains and len(trains) >= self._train_number:
            train = trains[self._train_number - 1]
            attrs["departure_time"] = train["time"]
            attrs["minutes_until_departure"] = train["minutes_until"]
        
        return attrs

    @property
    def available(self):
        """Disponibilidad del sensor."""
        if not self.coordinator.data or "trains" not in self.coordinator.data:
            return False
        return len(self.coordinator.data["trains"]) >= self._train_number
