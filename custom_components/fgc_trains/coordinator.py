"""Coordinador de datos para FGC Trains."""
import os
import csv
import logging
from datetime import datetime, timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class FGCDataCoordinator(DataUpdateCoordinator):
    """Coordinador para gestionar datos GTFS."""

    def __init__(self, hass: HomeAssistant, gtfs_path: str, origin: str, 
                 destination: str, line: str, update_interval: int):
        """Inicializar coordinador."""
        self.gtfs_path = gtfs_path
        self.origin = origin
        self.destination = destination
        self.line = line
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self):
        """Actualizar datos del GTFS."""
        try:
            return await self.hass.async_add_executor_job(self._read_gtfs_schedules)
        except Exception as err:
            raise UpdateFailed(f"Error actualizando datos: {err}")

    def _read_gtfs_schedules(self):
        """Leer horarios del GTFS."""
        try:
            today = datetime.now().strftime('%Y%m%d')
            service_ids = []
            
            calendar_file = os.path.join(self.gtfs_path, 'calendar_dates.txt')
            if not os.path.exists(calendar_file):
                _LOGGER.error(f"No se encuentra: {calendar_file}")
                return {"trains": [], "total": 0, "error": "GTFS not found"}
            
            with open(calendar_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['date'] == today and row['exception_type'] == '1':
                        service_ids.append(row['service_id'])
            
            if not service_ids:
                _LOGGER.warning(f"No hay servicios para hoy: {today}")
                return {"trains": [], "total": 0, "error": "No service today"}
            
            trip_ids = []
            trips_file = os.path.join(self.gtfs_path, 'trips.txt')
            
            with open(trips_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    headsign = row.get('trip_headsign', '')
                    if (row['route_id'] == self.line and 
                        row['service_id'] in service_ids and
                        self._destination_in_headsign(headsign)):
                        trip_ids.append(row['trip_id'])
            
            stop_times_file = os.path.join(self.gtfs_path, 'stop_times.txt')
            departures_set = set()
            
            with open(stop_times_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['trip_id'] in trip_ids and row['stop_id'] == self.origin:
                        departure_time = row['departure_time']
                        parts = departure_time.split(':')
                        hours = int(parts[0])
                        minutes = int(parts[1])
                        total_minutes = hours * 60 + minutes
                        
                        if hours >= 24:
                            hours -= 24
                            total_minutes = hours * 60 + minutes
                        
                        time_str = f"{hours:02d}:{minutes:02d}"
                        departures_set.add((total_minutes, time_str))
            
            departures = [
                {'minutes': m, 'time': t} 
                for m, t in sorted(departures_set)
            ]
            
            now = datetime.now()
            current_minutes = now.hour * 60 + now.minute
            
            upcoming_trains = []
            for dep in departures:
                if dep['minutes'] > current_minutes:
                    minutes_until = dep['minutes'] - current_minutes
                    upcoming_trains.append({
                        'time': dep['time'],
                        'minutes': dep['minutes'],
                        'minutes_until': minutes_until
                    })
                    if len(upcoming_trains) >= 6:
                        break
            
            _LOGGER.info(f"Cargados {len(departures)} horarios. Próximos: {len(upcoming_trains)}")
            
            return {
                "trains": upcoming_trains,
                "total": len(departures),
                "last_update": datetime.now().isoformat()
            }
            
        except Exception as e:
            _LOGGER.error(f"Error leyendo GTFS: {e}", exc_info=True)
            return {"trains": [], "total": 0, "error": str(e)}
    
    def _destination_in_headsign(self, headsign):
        """Verificar si el destino está en el headsign."""
        destination_map = {
            "PC": "Barcelona",
            "ES": "Espanya",
            "TR": "Terrassa",
            "SR": "Sabadell"
        }
        
        dest_name = destination_map.get(self.destination, self.destination)
        return dest_name in headsign
