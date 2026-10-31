import osmnx as ox

from pathlib import Path


class OSMGraph:

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.osm_file = self.base_dir / "static" / "map.osm"

        self.graph = None

    def load_graph(self):
        if self.graph is not None:
            return self.graph

        self.graph = ox.graph_from_xml(
            filepath=self.osm_file,
            bidirectional=False,
            simplify=False,
            retain_all=True,
        )

        return self.graph

    def get_graph(self):
        if self.graph is None:
            return self.load_graph()

        return self.graph