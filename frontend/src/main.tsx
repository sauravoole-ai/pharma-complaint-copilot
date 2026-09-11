import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";

import { store } from "./store";

const root = document.getElementById("root");
if (!root) throw new Error("Application root element is missing");

createRoot(root).render(
  <StrictMode>
    <Provider store={store}>
      <main aria-busy="true">Loading complaint workspace…</main>
    </Provider>
  </StrictMode>,
);
