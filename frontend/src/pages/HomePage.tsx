import { useEffect } from "react";
import AlertWidget from "../components/AlertWidget";
import MapPicker from "../components/MapPicker";
import { useNavigate } from "react-router-dom";

export default function HomePage() {
    const navigate = useNavigate();

    const showLandingPage = () => {
        const show = localStorage.getItem("already-shown")
        if (!show) {
            navigate('/landing-page');
        }
    }

    useEffect(() => {
        showLandingPage()
    }, [showLandingPage])

    return (
        <main className="grid h-screen w-full grid-cols-2 gap-4 overflow-hidden bg-gray-100 p-4">
            {/* Left: Map */}
            <section className="min-h-0 min-w-0">
                <MapPicker />
            </section>

            {/* Right: Alerts */}
            <section className="flex flex-col min-h-0 min-w-0 overflow-y-auto rounded-xl border border-gray-200 bg-white shadow-sm">
                <AlertWidget />
            </section>
        </main>
    )
}