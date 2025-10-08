import React, { useEffect } from "react";
import ReactDOM from "react-dom";

const AxeDevTools = () => {
  useEffect(() => {
    // Only load in development mode
    if (process.env.NODE_ENV === "development") {
      // Dynamically import axe-core/react only in development
      import("@axe-core/react")
        .then((axe) => {
          axe.default(React, ReactDOM, 1000);
        })
        .catch((err) => {
          console.warn("Failed to load axe-core/react:", err);
        });
    }
  }, []);

  return null;
};

export default AxeDevTools;
