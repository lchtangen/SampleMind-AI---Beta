import ReactDOM from "react-dom/client";

// Completely isolated test - NO IMPORTS, NO TAILWIND
console.log("=== DIAGNOSTIC TEST STARTING ===");

const DiagnosticTest = () => {
  console.log("DiagnosticTest component rendering");

  return (
    <div
      style={{
        backgroundColor: "#0A0A0F",
        color: "white",
        minHeight: "100vh",
        padding: "2rem",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1
        style={{
          fontSize: "48px",
          marginBottom: "20px",
          color: "#8B5CF6",
        }}
      >
        🔍 DIAGNOSTIC TEST
      </h1>

      <p
        style={{
          fontSize: "24px",
          marginBottom: "20px",
          color: "#FFFFFF",
        }}
      >
        If you can read this, React is rendering correctly!
      </p>

      <div
        style={{
          backgroundColor: "#8B5CF6",
          color: "white",
          padding: "20px",
          borderRadius: "8px",
          marginTop: "20px",
        }}
      >
        Purple box with inline styles - no Tailwind needed
      </div>

      <div
        style={{
          backgroundColor: "#06B6D4",
          color: "white",
          padding: "20px",
          borderRadius: "8px",
          marginTop: "20px",
        }}
      >
        Cyan box with inline styles
      </div>

      <button
        onClick={() => alert("Button works!")}
        style={{
          backgroundColor: "#EC4899",
          color: "white",
          padding: "12px 24px",
          border: "none",
          borderRadius: "8px",
          fontSize: "16px",
          cursor: "pointer",
          marginTop: "20px",
        }}
      >
        Click Me - Test Interactivity
      </button>
    </div>
  );
};

const root = document.getElementById("root");
console.log("Root element:", root);

if (root) {
  ReactDOM.createRoot(root).render(<DiagnosticTest />);
  console.log("React app mounted successfully");
} else {
  console.error("ROOT ELEMENT NOT FOUND!");
}
