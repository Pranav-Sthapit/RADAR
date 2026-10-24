
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const sections = [
  {
    number: "01",
    label: "ROAD NETWORK & ROUTING",
    title: "Route Planning",
    description:
      "RADAR uses OpenStreetMap road-network data and A* pathfinding to calculate routes between locations, helping identify practical paths through the road network.",
    image: "/public/ss1.png",
  },
  {
    number: "02",
    label: "TRAFFIC SIGN ALERTS",
    title: "Safe Driving",
    description:
      "Explore how RADAR shows traffic signs in your screen to aviod mistakes.",
    image: "/public/ss2.png",
  },
];

export default function LandingPage() {
  const navigate = useNavigate();

  const [showIntro, setShowIntro] = useState(
    () => sessionStorage.getItem("radar-intro-shown") !== "yes"
  );

  useEffect(() => {
    if (!showIntro) return;

    const timer = window.setTimeout(() => {
      setShowIntro(false);
      sessionStorage.setItem("radar-intro-shown", "yes");
    }, 2200);

    return () => window.clearTimeout(timer);
  }, [showIntro]);

  const navigateToHome = () => {
    localStorage.setItem("already-shown", "Yes shown");
    navigate("/");
  };

  return (
    <main className="min-h-screen overflow-hidden bg-[#F8FAF7] text-[#17221A]">
      {/* Welcome animation */}
      <div
        className={`fixed inset-0 z-50 flex flex-col items-center justify-center
          bg-[#F8FAF7] transition-opacity duration-700
          ${
            showIntro
              ? "opacity-100"
              : "pointer-events-none opacity-0"
          }`}
        aria-hidden={!showIntro}
      >
        <div className="mb-5 flex items-center gap-3 text-xs tracking-[0.4em] text-lime-700">
          <span className="h-2 w-2 animate-pulse rounded-full bg-lime-600" />
          INTELLIGENT NAVIGATION SYSTEM
        </div>

        <h1 className="animate-pulse text-6xl font-black tracking-[0.18em] sm:text-8xl">
          RADAR<span className="text-lime-600">.</span>
        </h1>

        <p className="mt-6 text-sm tracking-[0.25em] text-gray-500">
          WELCOME TO RADAR
        </p>

        <div className="mt-10 h-1 w-48 overflow-hidden rounded-full bg-gray-200">
          <div className="h-full w-full origin-left animate-[radar-load_2s_ease-in-out_forwards] bg-lime-600" />
        </div>
      </div>

      {/* Hero section */}
      <section className="relative flex min-h-screen flex-col items-center justify-center px-6 text-center">
        {/* Subtle grid */}
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.10]"
          style={{
            backgroundImage:
              "linear-gradient(#65a30d 1px, transparent 1px), linear-gradient(90deg, #65a30d 1px, transparent 1px)",
            backgroundSize: "60px 60px",
          }}
        />

        {/* Soft background glow */}
        <div className="pointer-events-none absolute left-1/2 top-1/2 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-lime-300/20 blur-[120px]" />

        <div className="relative">
          <div className="mb-8 inline-flex items-center gap-3 rounded-full border border-lime-700/20 bg-white/80 px-5 py-2 text-xs tracking-[0.2em] text-lime-700 shadow-sm">
            <span className="h-2 w-2 animate-pulse rounded-full bg-lime-600" />
            ROUTE PLANNING · NAVIGATION
          </div>

          <h1 className="text-6xl font-black tracking-tight sm:text-8xl md:text-9xl">
            RADAR<span className="text-lime-600">.</span>
          </h1>

          <h2 className="mx-auto mt-5 max-w-3xl text-2xl font-semibold leading-tight text-gray-700 sm:text-4xl">
            Navigate smarter.
            <span className="text-lime-700"> Find your way.</span>
          </h2>

          <p className="mx-auto mt-7 max-w-2xl text-base leading-8 text-gray-600 sm:text-xl">
            Intelligent route planning, road-network analysis, and traffic sign alerts — connected in one system.
          </p>

          <div className="mt-10 flex flex-wrap justify-center gap-4">
            <a
              href="#explore"
              className="rounded-xl border border-gray-300 bg-white px-7 py-4 text-sm font-semibold shadow-sm transition hover:border-lime-600 hover:bg-lime-50"
            >
              Explore RADAR ↓
            </a>

            <button
              onClick={navigateToHome}
              className="rounded-xl bg-lime-600 px-8 py-4 font-bold text-white shadow-lg shadow-lime-700/15 transition hover:bg-lime-700"
            >
              Get Started <span className="ml-2">→</span>
            </button>
          </div>
        </div>

        <div className="absolute bottom-8 animate-bounce text-xs tracking-[0.3em] text-gray-400">
          SCROLL TO DISCOVER
        </div>
      </section>

      {/* Project introduction */}
      <section
        id="explore"
        className="mx-auto max-w-7xl px-6 py-24 sm:py-32"
      >
        <div className="mb-20 max-w-2xl">
          <p className="text-xs font-semibold tracking-[0.35em] text-lime-700">
            INSIDE THE PROJECT
          </p>

          <h2 className="mt-5 text-4xl font-bold leading-tight sm:text-6xl">
            How RADAR
            <br />
            <span className="text-gray-400">brings it together.</span>
          </h2>

          <p className="mt-6 text-base leading-8 text-gray-600 sm:text-lg">
            Discover the key components of RADAR through its road-network
            visualization, routing capabilities, and vehicle navigation
            workflow.
          </p>
        </div>

        {/* Screenshot sections */}
        <div className="space-y-24 sm:space-y-36">
          {sections.map((item, index) => (
            <article
              key={item.number}
              className={`grid items-center gap-10 md:grid-cols-2 md:gap-16 ${
                index % 2 === 1
                  ? "md:[&>div:first-child]:order-2"
                  : ""
              }`}
            >
              {/* Screenshot card */}
              <div className="group relative">
                <div className="absolute -inset-3 rounded-3xl bg-lime-300/20 opacity-0 blur-2xl transition duration-500 group-hover:opacity-100" />

                <div className="relative overflow-hidden rounded-2xl border border-gray-200 bg-white p-2 shadow-lg shadow-gray-900/[0.04] transition duration-500 group-hover:-translate-y-1 group-hover:border-lime-600/40 group-hover:shadow-xl">
                  <img
                    src={item.image}
                    alt={item.title}
                    loading="lazy"
                    className="aspect-video w-full rounded-xl bg-gray-50 object-contain"
                  />
                </div>

                <p className="mt-4 text-right text-xs font-medium tracking-widest text-gray-400">
                  RADAR / MODULE {item.number}
                </p>
              </div>

              {/* Description */}
              <div className="py-4">
                <p className="text-xs font-semibold tracking-[0.3em] text-lime-700">
                  {item.label}
                </p>

                <p className="mt-5 text-6xl font-black text-lime-800/10 sm:text-7xl">
                  {item.number}
                </p>

                <h3 className="mt-2 text-3xl font-bold leading-tight text-[#17221A] sm:text-4xl">
                  {item.title}
                </h3>

                <p className="mt-6 text-base leading-8 text-gray-600 sm:text-lg">
                  {item.description}
                </p>

                <div className="mt-8 h-1 w-16 rounded-full bg-lime-600" />
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* Closing call to action */}
      <section className="border-t border-gray-200 bg-white px-6 py-24 text-center sm:py-32">
        <p className="text-xs font-semibold tracking-[0.35em] text-lime-700">
          YOUR JOURNEY STARTS HERE
        </p>

        <h2 className="mx-auto mt-6 max-w-3xl text-4xl font-black sm:text-6xl">
          The road ahead
          <br />
          <span className="text-lime-700">starts with RADAR.</span>
        </h2>

        <p className="mx-auto mt-6 max-w-xl leading-7 text-gray-600">
          Explore the RADAR system and discover the connection between
          intelligent route planning and vehicle navigation.
        </p>

        <button
          onClick={navigateToHome}
          className="mt-10 rounded-xl bg-lime-600 px-9 py-4 font-bold text-white shadow-lg shadow-lime-700/15 transition hover:bg-lime-700"
        >
          Get Started →
        </button>

        <footer className="mt-24 text-xs tracking-widest text-gray-400">
          RADAR PROJECT · {new Date().getFullYear()}
        </footer>
      </section>

      {/* Animation and smooth scrolling */}
      <style>{`
        @keyframes radar-load {
          from {
            transform: scaleX(0);
          }
          to {
            transform: scaleX(1);
          }
        }

        html {
          scroll-behavior: smooth;
        }

        @media (prefers-reduced-motion: reduce) {
          *,
          *::before,
          *::after {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
          }
        }
      `}</style>
    </main>
  );
}
