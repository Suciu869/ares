// In dev, Vite proxies /api to localhost:8000 to avoid CORS
const API_BASE = import.meta.env.DEV ? '' : 'http://localhost:8000';

function normalizeModelResponse(data) {
  const hasNuclearRaw = String(data.has_nuclear ?? data.hasNuclear ?? 'no').toLowerCase();
  const has_nuclear = ['yes', 'true', '1'].includes(hasNuclearRaw) ? 'yes' : 'no';

  return {
    energy_score: Number(data.energy_score ?? data.energyScore ?? 0),
    military_score: Number(data.military_score ?? data.militaryScore ?? 0),
    logistics_score: Number(data.logistics_score ?? data.logisticsScore ?? 0),
    has_nuclear,
    risk_percent: Number(data.risk_percent ?? data.riskPercent ?? 0),
  };
}

/**
 * Calls the AI evaluation API for a region.
 * @param {string} regionId - ISO region code (e.g. "UA63")
 */
export async function evaluateRegion(regionId) {
  const url = `${API_BASE}/api/evalueaza-regiune`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ region_id: regionId }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `API error ${res.status}`);
  }

  const data = await res.json();
  return normalizeModelResponse(data);
}

/**
 * Fetches the model predictions for all regions.
 * This is the preferred method for driving map colors and rankings.
 */
export async function fetchAllRegionPredictions() {
  const url = `${API_BASE}/api/evaluate-all`;
  const res = await fetch(url);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `API error ${res.status}`);
  }

  const data = await res.json();
  return data.map((d) => ({ id: String(d.region_id), ...normalizeModelResponse(d) }));
}
