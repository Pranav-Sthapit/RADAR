import { Routes,Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import HomePage from "./pages/HomePage";

export default function App() {
  return (
    <Routes>
      <Route path="/landing-page" element={<LandingPage/>}/>
      <Route path="/" element={<HomePage/>}/>
    </Routes>
  )
}
