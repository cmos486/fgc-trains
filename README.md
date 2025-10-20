# FGC Trains - Integración para Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/cmos486/fgc-trains.svg)](https://github.com/cmos486/fgc-trains/releases)
[![License](https://img.shields.io/github/license/cmos486/fgc-trains.svg)](LICENSE)

Integración para Home Assistant que proporciona información en tiempo real de los horarios de trenes de **Ferrocarrils de la Generalitat de Catalunya (FGC)**.

## 🚆 Características

- ✅ **Horarios en tiempo real** desde datos GTFS oficiales
- ✅ **5 sensores por ruta**: sensor principal + 4 trenes individuales
- ✅ **Actualización automática** de datos GTFS semanalmente
- ✅ **Configuración desde UI** (sin YAML)
- ✅ **Soporte para todas las líneas FGC**: S1, S2, S5, S6, S7, S8, L8, R5, R6
- ✅ **Filtrado por dirección** (solo trenes hacia tu destino)

## 📥 Instalación

### Opción 1: HACS (Recomendado)

1. Abre **HACS** en Home Assistant
2. Ve a **Integraciones**
3. Click en el menú (⋮) → **Repositorios personalizados**
4. Añade: `https://github.com/cmos486/fgc-trains`
5. Categoría: **Integration**
6. Busca **FGC Trains** y descarga
7. **Reinicia Home Assistant**

### Opción 2: Manual

1. Descarga desde [releases](https://github.com/cmos486/fgc-trains/releases)
2. Copia `custom_components/fgc_trains` a `/config/custom_components/`
3. Reinicia Home Assistant

## ⚙️ Configuración

1. Ve a **Configuración** → **Dispositivos y servicios**
2. Click **+ Añadir integración**
3. Busca **"FGC Trains"**
4. Configura tu línea, origen y destino

## 📊 Sensores

Crea 5 sensores por configuración:
- `sensor.fgc_[linea]_[origen]_[destino]` - Sensor principal
- `sensor.fgc_[linea]_tren_1` - Próximo tren
- `sensor.fgc_[linea]_tren_2` - Segundo tren
- `sensor.fgc_[linea]_tren_3` - Tercer tren
- `sensor.fgc_[linea]_tren_4` - Cuarto tren

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE)

## ⭐ Créditos

Datos GTFS: [FGC](https://www.fgc.cat)
