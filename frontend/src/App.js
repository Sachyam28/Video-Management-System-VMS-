import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import MonitoringCenter from "./pages/MonitoringCenter";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MonitoringCenter />} />
        <Route path="/monitor" element={<MonitoringCenter />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
