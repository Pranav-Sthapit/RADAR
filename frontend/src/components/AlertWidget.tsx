import { useEffect, useState, useCallback } from "react";
import { getDetection } from "../api/getDetection";

const API_BASE_URL = "http://localhost:8000";

type SignConfig = {
    badge: string;
    badgeClasses: string;
    actionNote: string;
    borderColor: string;
};

function getSignConfig(rawClass: string): SignConfig {
    const key = rawClass.toLowerCase().trim();
    if (key.includes("stop")) {
        return {
            badge: "CRITICAL STOP",
            badgeClasses: "bg-red-50 text-red-700 border-red-200",
            actionNote: "Vehicle must come to a complete stop before the designated line.",
            borderColor: "border-red-200/80 shadow-red-100",
        };
    }
    if (key.includes("speed")) {
        return {
            badge: "SPEED REGULATION",
            badgeClasses: "bg-amber-50 text-amber-700 border-amber-200",
            actionNote: "Adjust vehicle throttle to strictly comply with posted speed limits.",
            borderColor: "border-amber-200/80 shadow-amber-100",
        };
    }
    if (key.includes("traffic") || key.includes("light")) {
        return {
            badge: "SIGNAL ADVISORY",
            badgeClasses: "bg-orange-50 text-orange-700 border-orange-200",
            actionNote: "Approach intersection with caution and observe signal indication.",
            borderColor: "border-orange-200/80 shadow-orange-100",
        };
    }
    return {
        badge: "SIGN DETECTED",
        badgeClasses: "bg-indigo-50 text-indigo-700 border-indigo-200",
        actionNote: "Road sign identified ahead. Maintain safe driving vigilance.",
        borderColor: "border-indigo-200/80 shadow-indigo-100",
    };
}

export default function AlertWidget() {
    const [className, setClassName] = useState("");
    const [imgPath, setImgPath] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [lastUpdated, setLastUpdated] = useState<string | null>(null);
    const [isRefreshing, setIsRefreshing] = useState(false);

    const checkForDetection = useCallback(async () => {
        setIsRefreshing(true);
        const res = await getDetection();
        setIsRefreshing(false);

        if (res.ok === false) {
            setError("Failed to fetch detection stream.");
            setLoading(false);
            return;
        }

        setError(null);
        setLastUpdated(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }));

        if (res.data.detected === false) {
            setImgPath("");
            setClassName("No Signs Detected");
            setLoading(false);
            return;
        }

        setClassName(res.data.class_name ?? "Unknown Sign");
        setImgPath(res.data.image_path ?? "");
        setLoading(false);
    }, []);

    useEffect(() => {
        let active = true;

        void checkForDetection();

        const intervalId = window.setInterval(() => {
            if (active) {
                void checkForDetection();
            }
        }, 5000);

        return () => {
            active = false;
            window.clearInterval(intervalId);
        };
    }, [checkForDetection]);

    const isDetected = !loading && !error && imgPath && className && className !== "No Signs Detected";
    const signConfig = isDetected ? getSignConfig(className) : null;

    return (
        <div className="flex h-full flex-col justify-between p-5 sm:p-6 bg-white">
            {/* Top Bar: Title & Live Status */}
            <div className="flex items-center justify-between border-b border-slate-100 pb-4 shrink-0">
                <div>
                    <h2 className="text-lg font-semibold tracking-tight text-slate-800">
                        Detection Alerts
                    </h2>
                    <p className="text-xs text-slate-500">
                        Live visual road sign recognition & alerts
                    </p>
                </div>

                <div className="flex items-center gap-2">
                    <span className="relative flex h-2.5 w-2.5">
                        <span className={`absolute inline-flex h-full w-full animate-ping rounded-full ${error ? "bg-red-400 opacity-75" : "bg-emerald-400 opacity-75"}`}></span>
                        <span className={`relative inline-flex h-2.5 w-2.5 rounded-full ${error ? "bg-red-500" : "bg-emerald-500"}`}></span>
                    </span>
                    <span className="text-xs font-medium text-slate-600">
                        {error ? "Offline" : "Live Monitor"}
                    </span>
                </div>
            </div>

            {/* Center Content Section: Centered Text & Elements */}
            <div className="my-auto flex flex-1 flex-col items-center justify-center py-6 text-center">
                {/* 1. Loading State */}
                {loading && (
                    <div className="flex flex-col items-center justify-center space-y-3">
                        <div className="relative flex h-14 w-14 items-center justify-center rounded-full bg-indigo-50 text-indigo-600">
                            <svg className="h-6 w-6 animate-spin" viewBox="0 0 24 24" fill="none">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                        </div>
                        <h3 className="text-sm font-semibold text-slate-700">Connecting to Radar...</h3>
                        <p className="text-xs text-slate-500 max-w-xs">
                            Initializing detection stream and polling queue for new sign data.
                        </p>
                    </div>
                )}

                {/* 2. Error State */}
                {!loading && error && (
                    <div className="flex flex-col items-center justify-center space-y-3 text-center">
                        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-red-50 text-red-600 border border-red-200">
                            <svg className="h-7 w-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <circle cx="12" cy="12" r="10"></circle>
                                <line x1="12" y1="8" x2="12" y2="12"></line>
                                <line x1="12" y1="16" x2="12.01" y2="16"></line>
                            </svg>
                        </div>
                        <h3 className="text-base font-semibold text-red-700">Stream Connection Error</h3>
                        <p className="text-xs text-red-500 max-w-xs">{error}</p>
                        <button
                            type="button"
                            onClick={() => void checkForDetection()}
                            className="mt-2 rounded-lg bg-red-600 px-4 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-red-700 transition"
                        >
                            Retry Connection
                        </button>
                    </div>
                )}

                {/* 3. Empty / Idle State (No Signs Detected) */}
                {!loading && !error && !isDetected && (
                    <div className="flex flex-col items-center justify-center space-y-3 text-center max-w-sm">
                        <div className="relative flex h-16 w-16 items-center justify-center rounded-full bg-slate-50 border border-slate-200 shadow-inner">
                            <div className="absolute h-10 w-10 animate-ping rounded-full bg-emerald-100 opacity-60"></div>
                            <svg className="h-8 w-8 text-emerald-600 relative z-10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                                <polyline points="9 12 11 14 15 10"></polyline>
                            </svg>
                        </div>

                        <div className="space-y-1">
                            <span className="inline-block rounded-full bg-emerald-50 px-2.5 py-0.5 text-[11px] font-semibold tracking-wide text-emerald-700 border border-emerald-200">
                                ROADWAY CLEAR
                            </span>
                            <h3 className="text-base font-bold text-slate-800">
                                No Signs Detected
                            </h3>
                            <p className="text-xs text-slate-500 leading-relaxed">
                                Radar & visual sensors are actively scanning the road ahead. Alerts will trigger automatically when traffic signs are recognized.
                            </p>
                        </div>
                    </div>
                )}

                {/* 4. Active Detection State (Centered & Formatted) */}
                {isDetected && signConfig && (
                    <div className="flex w-full flex-col items-center justify-center space-y-4">
                        {/* Centered Severity / Category Badge */}
                        <div className="flex flex-col items-center gap-1.5">
                            <span className={`rounded-full border px-3 py-1 text-[11px] font-bold tracking-wider uppercase ${signConfig.badgeClasses}`}>
                                {signConfig.badge}
                            </span>
                            <h3 className="text-2xl font-black capitalize tracking-tight text-slate-900">
                                {className.replaceAll("_", " ")}
                            </h3>
                            <p className="text-xs font-medium text-slate-600 max-w-xs leading-snug">
                                {signConfig.actionNote}
                            </p>
                        </div>

                        {/* Centered Image Container with clean frame */}
                        <div className={`relative flex items-center justify-center overflow-hidden rounded-2xl border bg-slate-50 p-2 shadow-sm transition-all duration-300 max-w-xs sm:max-w-sm w-full ${signConfig.borderColor}`}>
                            <img
                                src={`${API_BASE_URL}${imgPath}`}
                                alt={className}
                                className="max-h-56 sm:max-h-64 w-auto rounded-xl object-contain shadow-inner"
                            />
                        </div>

                        {lastUpdated && (
                            <div className="inline-flex items-center gap-1.5 rounded-md bg-slate-100 px-2.5 py-1 text-[11px] text-slate-500">
                                <svg className="h-3.5 w-3.5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <circle cx="12" cy="12" r="10"></circle>
                                    <polyline points="12 6 12 12 16 14"></polyline>
                                </svg>
                                <span>Detected at {lastUpdated}</span>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Bottom Status Bar */}
            <div className="flex items-center justify-between border-t border-slate-100 pt-3 text-xs text-slate-400 shrink-0">
                <span className="flex items-center gap-1.5">
                    <span className="inline-block h-1.5 w-1.5 rounded-full bg-slate-300"></span>
                    <span>Interval: 5s</span>
                </span>

                <button
                    type="button"
                    onClick={() => void checkForDetection()}
                    disabled={isRefreshing}
                    className="flex items-center gap-1 text-xs font-medium text-indigo-600 hover:text-indigo-700 transition disabled:opacity-50"
                >
                    <svg
                        className={`h-3.5 w-3.5 ${isRefreshing ? "animate-spin" : ""}`}
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                    >
                        <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
                    </svg>
                    <span>{isRefreshing ? "Scanning..." : "Scan Now"}</span>
                </button>
            </div>
        </div>
    );
}