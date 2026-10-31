from .osm_graph import OSMGraph
from .map_service import MapService
from .route_service import RouteService

graph_object=OSMGraph()

map_object=MapService(graph_object)

route_object=RouteService(graph_object,map_object)