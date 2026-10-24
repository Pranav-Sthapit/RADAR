import osmnx as ox
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OSM_FILE = BASE_DIR / "static" / "map.osm"

# Load the graph once when this module is imported.
# Do not reload the file on every routing request.
G = ox.graph_from_xml(
    filepath=OSM_FILE,
    bidirectional=False,
    simplify=False,
    retain_all=True,
)
