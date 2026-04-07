import { useEffect, useMemo, useState } from 'react';
import { getRegionData, getRankedRegions, REGION_IDS } from '../data/regions';
import { evaluateRegion } from '../api/evaluateRegion';

const regionDataById = Object.fromEntries(
  getRegionData().map((r) => [r.id, r])
);
const ranked = getRankedRegions();

export function RegionDetails({ regionId, onSelectRegion, aiData, regionDataById, loading, error }) {
  const baseRegion = regionId ? regionDataById?.[regionId] : null;
  const aiRegion = regionId ? aiData?.all?.find((r) => r.id === regionId) : null;

  const display = useMemo(() => {
    if (!baseRegion) return null;
    const base = {
      energy_score: baseRegion.energy_score,
      military_score: baseRegion.military_score,
      logistics_score: baseRegion.logistics_score,
      has_nuclear: baseRegion.has_nuclear,
      risk_percent: baseRegion.riskPercent,
    };
    return aiRegion ? { ...base, ...aiRegion } : base;
  }, [baseRegion, aiRegion]);

  const top10 = aiData?.sorted?.slice(0, 10) ?? [];

  return (
    <div className="details-panel">
      {baseRegion ? (
        <section className="region-details-section">
          <h3>Selected region</h3>
          <div className="region-details">
            <h4>{baseRegion.name}</h4>
            <div className="risk-badges">
              <span className="risk-badge risk-pct">
                {loading ? '…' : `${display?.risk_percent ?? 0}%`} risk
              </span>
            </div>
            {error ? <p className="error">Error fetching model data: {error}</p> : null}
            <dl>
              <dt>Energy score</dt>
              <dd>{display?.energy_score ?? 0}/10</dd>
              <dt>Military score</dt>
              <dd>{display?.military_score ?? 0}/10</dd>
              <dt>Logistics score</dt>
              <dd>{display?.logistics_score ?? 0}/10</dd>
              <dt>Nuclear</dt>
              <dd>{display?.has_nuclear ?? baseRegion.has_nuclear}</dd>
            </dl>
          </div>
        </section>
      ) : null}

      <section className="ranking-section">
        <h3>Top 10 by AI risk</h3>
        <ul className="ranking-list">
          {top10.map((region, index) => (
            <li
              key={region.id}
              onClick={() => onSelectRegion(region.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && onSelectRegion(region.id)}
              className={regionId === region.id ? 'selected' : ''}
            >
              <span className="rank-num">#{index + 1}</span>
              <span className="rank-name">{regionDataById[region.id]?.name ?? region.id}</span>
              <span className="rank-badge">{region.risk_percent}%</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
