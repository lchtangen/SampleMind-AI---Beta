/**
 * SampleMind AI - Main Application Component
 *
 * React PWA for audio analysis and music generation
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppShell } from '@/components/layout';
import Dashboard from '@/routes/Dashboard';
import Analyze from '@/routes/Analyze';
import Library from '@/routes/Library';
import Generate from '@/routes/Generate';
import Streaming from '@/routes/Streaming';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppShell />}>
          <Route index element={<Dashboard />} />
          <Route path="analyze" element={<Analyze />} />
          <Route path="library" element={<Library />} />
          <Route path="generate" element={<Generate />} />
          <Route path="streaming" element={<Streaming />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
