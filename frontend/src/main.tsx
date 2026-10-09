import "./styles/tokens.css";
import "./styles/base.css";
import "./components/ui.css";
import "./styles/classic.css";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./app/App";

const root = document.getElementById("root");
if (!root) throw new Error("The dashboard root element is missing.");

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
