import { httpDeleteJson, httpPostJson } from "./http"

export type RouteRequest = {
    start_lat: number | null;
    start_lng: number | null;
    end_lat: number | null;
    end_lng: number | null;
};

export type Coordinate = {
    lat: number;
    lng: number;
};

export type RouteResponse = {
    distance_m: number;
    distance_km: number;
    route: Coordinate[];
};

export function getRoute(payload: RouteRequest) {
    return httpPostJson<RouteResponse, RouteRequest>('/api/route', payload);
}

export function deleteDestination(){
    return httpDeleteJson<void>('/api/route');
}