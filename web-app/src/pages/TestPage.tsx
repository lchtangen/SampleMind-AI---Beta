import React from "react";

export const TestPage: React.FC = () => {
  console.log("TestPage rendering...");

  return (
    <div className="min-h-screen bg-bg-primary p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-4">
          Test Page - Simple Render
        </h1>
        <p className="text-gray-300 mb-8">
          If you can see this, React is rendering correctly.
        </p>

        <div className="glass-card p-6 rounded-xl mb-4">
          <h2 className="text-2xl text-primary mb-2">Glass Card Test</h2>
          <p className="text-text-secondary">
            This should have a glassmorphic background.
          </p>
        </div>

        <div className="bg-primary text-white p-4 rounded">
          This div uses bg-primary Tailwind class
        </div>

        <div
          className="mt-4 p-4"
          style={{ backgroundColor: "#8B5CF6", color: "white" }}
        >
          This div uses inline styles
        </div>
      </div>
    </div>
  );
};
