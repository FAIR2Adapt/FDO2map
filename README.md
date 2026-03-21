# FDO2map

Resolve a FAIR Digital Object (FDO) and open it in an interactive map dashboard — automatically.

Given only an RO-Crate persistent identifier (PID), `fdo2map` discovers the dataset and visualization dashboard from the RO-Crate annotations and opens it in the browser. No prior knowledge of the data or dashboard is needed.

## How it works

```
RO-Crate PID
    │
    ▼
┌─────────────────────────┐
│  1. Load from ROHub     │
│  2. Find ViewAction     │
│  3. Resolve dataset URL │
│  4. Apply URL template  │
│  5. Open browser        │
└─────────────────────────┘
    │
    ▼
Interactive map dashboard
```

The script uses [schema.org](https://schema.org) annotations embedded in the RO-Crate:

- **`schema:potentialAction`** — links a dataset to a ViewAction
- **`schema:ViewAction`** — describes how to view the data
- **`schema:urlTemplate`** — the dashboard URL pattern (e.g., `https://dashboard.example.com/#{dataset_url}`)
- **`schema:object`** — the dataset resource to visualize
- **`schema:instrument`** — the dashboard application

## Web interface

The easiest way to use FDO2map is via the web interface — no installation required:

**[https://fair2adapt.github.io/FDO2map/](https://fair2adapt.github.io/FDO2map/)**

1. Paste an RO-Crate PID (or click one of the examples)
2. Enter an API key if the dataset is private (leave empty for public datasets)
3. Click **Resolve and open dashboard**

You can also link directly to a specific RO-Crate:

```
https://fair2adapt.github.io/FDO2map/#https://w3id.org/ro-id/24600867-23ca-4b97-be14-3aa63883c056
```

## Command-line interface

For scripting or automation, use the Python CLI.

### Prerequisites

- Python 3.10 or later
- A [ROHub](https://reliance.rohub.org/) account (free, needed to query RO-Crate metadata)

### Clone the repository

```bash
git clone https://github.com/FAIR2Adapt/FDO2map.git
cd FDO2map
```

### Set up a Python environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install rohub
```

### Configure ROHub credentials

Create `~/rohub_credentials.json` with your ROHub account:

```json
{
  "username": "your-email@example.com",
  "password": "your-password"
}
```

### Run

```bash
python fdo2map.py <RO-Crate PID>
```

For private datasets, the script prompts for an API key. For public datasets, press Enter to skip.

## Examples

### RIOMAR ocean model (public, HEALPix DGGS)

```bash
python fdo2map.py https://w3id.org/ro-id/24600867-23ca-4b97-be14-3aa63883c056
```

Ocean temperature, salinity, and sea surface height from the GAMAR/GLORYS hindcast simulation, regridded to HEALPix level 13. Bay of Biscay, Oct–Dec 2023.

### Sentinel-2 reflectance (public, HEALPix multiscale pyramid)

```bash
python fdo2map.py https://w3id.org/ro-id/fdc1c071-76d7-44df-a565-8217ebcc59fe
```

Sentinel-2 L1C Band 02 (Blue) reflectance on a HEALPix multiscale pyramid (levels 10–20, ~10km to ~10m resolution).

### NorESM2 ARCTIC reanalysis (private, API key required)

```bash
python fdo2map.py https://w3id.org/ro-id/1f0b5044-ae4f-483d-b7a2-48a5a6ac3965
```

Monthly SST and 3D ocean temperature from NorESM2/BLOM (JRA-OC20 reanalysis), 2010–2018. Requires an API key — the script will prompt for it.

## How the RO-Crate is structured

Each RO-Crate contains:

| Resource type | Purpose |
|---------------|---------|
| **Dataset** | URL of the Zarr data store |
| **Web Service** | URL of the dashboard application |
| **ViewAction** (annotation) | Links dataset to dashboard via a URL template |
| **Product** (annotation) | Scientific metadata (variables, spatial/temporal coverage, resolution) |

The ViewAction makes the RO-Crate **machine-actionable**: any tool can discover how to visualize the data without hardcoded knowledge of the dashboard or data format.

## Part of FAIR2Adapt

This tool is part of the [FAIR2Adapt](https://fair2adapt.eu) project, which transforms climate and ocean data into FAIR Digital Objects for climate change adaptation.

The visualization dashboard is [gridlook](https://github.com/FAIR2Adapt/gridlook) / [riomar-dashboard](https://github.com/FAIR2Adapt/riomar-dashboard), a WebGL-based globe viewer supporting HEALPix, curvilinear, regular, and other grid types.

## License

MIT License
