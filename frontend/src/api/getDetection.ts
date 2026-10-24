import { httpGetJson } from "./http";

export type DetectionResponse = {
    detected: boolean;
    class_name: string | null;
    image_path: string | null;
};

export function getDetection() {
    return httpGetJson<DetectionResponse>('/api/detections/new');
}