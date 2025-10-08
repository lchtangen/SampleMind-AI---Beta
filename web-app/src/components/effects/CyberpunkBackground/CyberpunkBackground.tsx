import React from "react";
import { ScanlineOverlay } from "../ScanlineOverlay";

export const CyberpunkBackground: React.FC = () => {
  return (
    <div className="fixed inset-0 -z-10 bg-bg-primary">
      {/* Cyberpunk grid pattern */}
      <div className="absolute inset-0 opacity-30">
        <div
          className="w-full h-full"
          style={{
            backgroundImage: `
              linear-gradient(rgba(6, 182, 212, 0.15) 1px, transparent 1px),
              linear-gradient(90deg, rgba(6, 182, 212, 0.15) 1px, transparent 1px)
            `,
            backgroundSize: "40px 40px",
          }}
        />
      </div>
      {/* Purple gradient glow */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-accent-cyan/10" />
      <ScanlineOverlay />
    </div>
  );
};
