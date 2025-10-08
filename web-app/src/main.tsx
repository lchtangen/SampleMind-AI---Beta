import { ComponentShowcase } from "@/pages/ComponentShowcase";
import React from "react";
import ReactDOM from "react-dom/client";
import AxeDevTools from "./components/dev/AxeDevTools";
import "./index.css";

console.log("SampleMind AI Component Showcase loading...");

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AxeDevTools />
    <ComponentShowcase />
  </React.StrictMode>
);
