
import { useState, useRef, useCallback, useEffect } from "react";
import L from "leaflet";
import {
  MapContainer,
  Marker,
  TileLayer,
  useMapEvents,
  Popup,
  Polyline,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { deleteDestination, getRoute, RouteRequest, RouteResponse } from "../api/getRoute"
import MapAreaHighlight from "./MapAreaHighlight";

type MapMarker = {
  geoCode: [number, number];
  popUp: string;
};

const destinationIcon = L.icon({
  iconUrl: "/destinationMarker.png",
  iconSize: [38, 38],
  iconAnchor: [19, 38],
});

const locationIcon = L.icon({
  iconUrl: "/locationMarker.png",
  iconSize: [38, 38],
  iconAnchor: [19, 38],
});

type MapClickHandlerProps = {
  onLocationSelect: (position: [number, number]) => void;
};

function MapClickHandler({ onLocationSelect }: MapClickHandlerProps) {
  useMapEvents({
    click(event) {
      onLocationSelect([event.latlng.lat, event.latlng.lng]);
    },
  });

  return null;
}

export default function MapPicker() {
  const [destinationMarker, setDestinationMarker] =
    useState<MapMarker | null>(null);

  const [locationMarker, setLocationMarker] =
    useState<MapMarker | null>(null);

  const [isRouting, setIsRouting] = useState(false);
  const [routeData, setRouteData] = useState<RouteResponse | null>(null);
  const [routeError, setRouteError] = useState<string | null>(null);

  const intervalRef = useRef<number | null>(null);
  const requestInFlightRef = useRef(false);

  const stopRouting = useCallback(() => {
    if (intervalRef.current !== null) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    setIsRouting(false);
  }, []);

  const fetchLatestRoute = useCallback(async () => {
    if (!destinationMarker || requestInFlightRef.current) return;

    requestInFlightRef.current = true;

    const payload: RouteRequest = {
      start_lat: null,
      start_lng: null,
      end_lat: destinationMarker.geoCode[0],
      end_lng: destinationMarker.geoCode[1],
    };

    const result = await getRoute(payload);

    requestInFlightRef.current = false;

    if (!result.ok) {
      setRouteError(result.error);
      return;
    }

    setRouteError(null);
    setRouteData(result.data);

    const firstPoint = result.data.route[0];

    if (firstPoint) {
      setLocationMarker({
        geoCode: [firstPoint.lat, firstPoint.lng],
        popUp: "Current Location (Route Start)",
      });
    }

  }, [destinationMarker]);

  const startRouting = useCallback(() => {
    if (!destinationMarker || intervalRef.current !== null) return;

    setIsRouting(true);
    setRouteError(null);

    void fetchLatestRoute();

    intervalRef.current = window.setInterval(() => {
      void fetchLatestRoute();
    }, 2000);
  }, [destinationMarker, fetchLatestRoute]);

  const clearDestination = useCallback(async () => {
    await deleteDestination();
    stopRouting();
    
    setDestinationMarker(null);
    setLocationMarker(null);
    setRouteData(null);
    setRouteError(null);

  }, [stopRouting]);

  useEffect(() => {
    return () => {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
      }
    };
  }, []);


  return (
    <div className="flex h-full min-h-0 flex-col gap-3">
      {/* Panel 1: Header */}
      <div className="flex h-20 shrink-0 items-center justify-between rounded-xl border border-slate-200 bg-white px-5 shadow-sm">
        <div>
          <h2 className="text-lg font-semibold text-slate-800">
            Interactive Route Selector
          </h2>
          <p className="text-sm text-slate-500">
            {destinationMarker
              ? `Destination: ${destinationMarker.geoCode[0].toFixed(5)}, ${destinationMarker.geoCode[1].toFixed(5)}`
              : "Click on the map to select a destination"}
          </p>
        </div>

        {isRouting && (
          <span className="rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-700">
            Routing Active
          </span>
        )}
      </div>

      {/* Panel 2: Map — temporary */}

      {/* Panel 2: Map */}
      <div className="relative min-h-0 min-w-0 flex-1 overflow-hidden rounded-xl border border-slate-200">
        <MapContainer
          center={[27.7172, 85.324]}
          zoom={13}
          className="h-full w-full"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <MapAreaHighlight />

          <MapClickHandler
            onLocationSelect={(position) => {
              if (isRouting) return;
              setDestinationMarker({
                geoCode: position,
                popUp: "Destination",
              });
            }}
          />

          {destinationMarker && (
            <Marker
              position={destinationMarker.geoCode}
              icon={destinationIcon}
            >
              <Popup>{destinationMarker.popUp}</Popup>
            </Marker>
          )}

          {locationMarker && (
            <Marker
              position={locationMarker.geoCode}
              icon={locationIcon}
            >
              <Popup>{locationMarker.popUp}</Popup>
            </Marker>
          )}

          {routeData && routeData.route.length > 0 && (
            <Polyline
              positions={routeData.route.map(
                ({ lat, lng }) => [lat, lng] as [number, number],
              )}
              pathOptions={{
                color: "#2563eb",
                weight: 6,
                opacity: 0.85,
              }}
            />
          )}

        </MapContainer>
      </div>

      {routeError && (
        <p className="text-sm text-red-600" role="alert">
          {routeError}
        </p>
      )}


      {/* Panel 3: Footer */}
      <div className="flex min-h-20 shrink-0 flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
        <p className="text-sm text-slate-600">
          Select a point on the map to set your destination.
        </p>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={startRouting}
            disabled={!destinationMarker || isRouting}
            className="rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            Start Routing
          </button>

          <button
            type="button"
            onClick={stopRouting}
            disabled={!isRouting}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Stop Routing
          </button>

          <button
            type="button"
            onClick={clearDestination}
            disabled={!destinationMarker}
            className="rounded-lg border border-red-200 bg-white px-4 py-2.5 text-sm font-medium text-red-600 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Clear Destination
          </button>
        </div>
      </div>
    </div>
  );
}
