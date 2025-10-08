/**
 * Minimal Test - Debugging Component Render
 */

import { NeonButton } from "@/components/atoms/NeonButton";
import { CyberpunkBackground } from "@/components/effects/CyberpunkBackground";
import React from "react";

export const MinimalTest: React.FC = () => {
  console.log("MinimalTest component rendering...");

  return (
    <>
      <CyberpunkBackground />

      <div className="min-h-screen p-8 relative">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-6xl font-bold text-white mb-8">Minimal Test</h1>

          <p className="text-2xl text-gray-300 mb-8">
            If you see this text, React is rendering!
          </p>

          <div className="mb-8">
            <NeonButton variant="primary">Test Button</NeonButton>
          </div>

          <div className="bg-purple-500 text-white p-8 rounded-lg">
            This is a purple div with Tailwind bg-purple-500
          </div>
        </div>
      </div>
    </>
  );
};

export default MinimalTest;
