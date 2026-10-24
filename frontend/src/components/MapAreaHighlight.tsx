import { useEffect, useState } from "react";
import { Polygon, Rectangle, useMap } from "react-leaflet";
import {httpGetJson} from "../api/http"

type MapBounds = {
    south: number;
    west: number;
    north: number;
    east: number;
};

export default function MapAreaHighlight() {
    const map = useMap();
    const [bounds, setBounds] = useState<MapBounds | null>(null);

    useEffect(() => {
        let cancelled = false;

        async function loadBounds() {
            const result = await httpGetJson<MapBounds>("/api/map/bounds");

            if (cancelled) return;

            if (!result.ok) {
                console.error("Could not load OSM map bounds:", result.error);
                return;
            }

            const data = result.data;

            setBounds(data);
            map.fitBounds([
                [data.south, data.west],
                [data.north, data.east],
            ]);
        }

        void loadBounds();

        return () => {
            cancelled = true;
        };
    }, [map]);

    if (!bounds) return null;

    return (
        <Rectangle
            bounds={[
                [bounds.south, bounds.west],
                [bounds.north, bounds.east],
            ]}
            pathOptions={{
                color: "#2563eb",
                weight: 2,
                fillColor: "#3b82f6",
                fillOpacity: 0.18,
            }}
        />
    );
}