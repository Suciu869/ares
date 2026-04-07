import { useEffect, useMemo, useState } from 'react';
import { UkraineMap } from './components/UkraineMap';
import { RegionDetails } from './components/RegionDetails';
import { fetchAllRegionPredictions } from './api/evaluateRegion';
import { getRegionData } from './data/regions';
import './App.css';

const regionDataById = Object.fromEntries(
  getRegionData().map((r) => [r.id, r])
);

export default function App() {
  const [selectedId, setSelectedId] = useState(null);
  const [aiData, setAiData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadAll() {
      setLoading(true);
      setError(null);
      try {
        const all = await fetchAllRegionPredictions();
        if (cancelled) return;

        // Sort descending by risk so rank 1 is highest risk
        const sorted = [...all].sort((a, b) => b.risk_percent - a.risk_percent);
        const rankById = {};
        sorted.forEach((item, index) => {
          rankById[item.id] = index + 1;
        });

        setAiData({ all, sorted, rankById });
      } catch (err) {
        if (!cancelled) setError(err.message || 'Failed to load AI data');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadAll();
    return () => {
      cancelled = true;
    };
  }, []);

  const selectedRegionData = useMemo(() => {
    if (!selectedId || !aiData?.all) return null;
    return aiData.all.find((item) => item.id === selectedId) || null;
  }, [selectedId, aiData]);

  return (
    <div className="app">
      <header className="header">
        <h1>A.R.E.S. — Advanced Risk Evaluation System</h1>
      </header>
      <div className="main">
        <div className="map-panel">
          <div className="map-panel-inner">
            <h2>Dynamic risk map — Ukraine</h2>
            <p className="subtitle">
              Each region is shaded by its relative strike likelihood. Red indicates the highest-priority oblasts; green the least probable under the current scenario.
            </p>
            <div className="map-wrap">
              <UkraineMap
                selectedId={selectedId}
                onSelectRegion={setSelectedId}
                aiRankById={aiData?.rankById}
              />
            </div>
          </div>
        </div>
        <aside className="sidebar">
          <div className="sidebar-inner">
            <RegionDetails
              regionId={selectedId}
              onSelectRegion={setSelectedId}
              aiData={aiData}
              regionDataById={regionDataById}
              loading={loading}
              error={error}
            />
          </div>
        </aside>
      </div>
    </div>
  );
}
