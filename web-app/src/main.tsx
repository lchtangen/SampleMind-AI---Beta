import { LandingPage } from "@/pages/LandingPage";
import React from "react";
import ReactDOM from "react-dom/client";
import AxeDevTools from "./components/dev/AxeDevTools";
import "./index.css";

console.log("SampleMind AI Landing Page loading...");

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AxeDevTools />
    <LandingPage />
  </React.StrictMode>
);
