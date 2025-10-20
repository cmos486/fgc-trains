"""Constantes para FGC Trains."""

DOMAIN = "fgc_trains"
PLATFORMS = ["sensor"]

GTFS_URL = "https://www.fgc.cat/google/google_transit.zip"
DEFAULT_GTFS_PATH = "/config/custom_components/fgc_trains/gtfs_data"
DEFAULT_UPDATE_INTERVAL = 60

LINES = {
    "S1": "Barcelona - Terrassa",
    "S2": "Barcelona - Sabadell", 
    "S5": "Barcelona - Rubí / Manresa",
    "S6": "Barcelona - Reina Elisenda",
    "S7": "Barcelona - Avinguda Tibidabo",
    "S8": "Espanya - Molí Nou",
    "L8": "Espanya - Molí Nou",
    "R5": "Barcelona - Manresa",
    "R6": "Barcelona - Igualada"
}

STATIONS = {
    "PC": "Barcelona - Plaça Catalunya",
    "ES": "Barcelona - Espanya",
    "TR": "Terrassa - Rambla",
    "TN": "Terrassa - Nacions Unides",
    "SR": "Sabadell - Rambla",
    "RE": "Reina Elisenda",
    "TB": "Avinguda Tibidabo",
    "MN": "Molí Nou - Ciutat Cooperativa",
    "UB": "Universitat Autònoma"
}
