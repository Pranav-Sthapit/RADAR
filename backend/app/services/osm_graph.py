import osmnx as ox

from pathlib import Path


class OSMGraph:

    def __init__(self):
        self.__base_dir = Path(__file__).resolve().parent.parent.parent
        self.__osm_file = self.__base_dir / "static" / "map.osm"

        self.__graph = None

    def __load_graph(self):
        if self.__graph is not None:
            return self.__graph

        self.__graph = ox.graph_from_xml(
            filepath=self.__osm_file,
            bidirectional=False,
            simplify=False,
            retain_all=True,
        )

        return self.__graph

    def get_graph(self):
        if self.__graph is None:
            return self.__load_graph()

        return self.__graph