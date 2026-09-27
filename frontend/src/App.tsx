import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Shell } from "./components/layout/Shell";
import { ThemeProvider } from "./theme/ThemeProvider";
import { Workbench } from "./pages/Workbench";
import { Alerts } from "./pages/Alerts";
import { Events } from "./pages/Events";
import { Signatures } from "./pages/Signatures";
import { Runs } from "./pages/Runs";

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Shell />}>
            <Route index element={<Workbench />} />
            <Route path="alerts" element={<Alerts />} />
            <Route path="events" element={<Events />} />
            <Route path="signatures" element={<Signatures />} />
            <Route path="runs" element={<Runs />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}