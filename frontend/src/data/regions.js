// Mock region data: energy_score, military_score, logistics_score (1-10), has_nuclear (yes/no)
// Risk rank is computed by sorting on combined score (energy + military + logistics), then colored by rank
export const REGION_IDS = [
  'UA05', 'UA07', 'UA09', 'UA12', 'UA14', 'UA18', 'UA21', 'UA23', 'UA26',
  'UA30', 'UA32', 'UA35', 'UA40', 'UA43', 'UA46', 'UA48', 'UA51', 'UA53',
  'UA56', 'UA59', 'UA61', 'UA63', 'UA65', 'UA68', 'UA71', 'UA74', 'UA77',
];

const names = {
  UA05: 'Vinnytsia', UA07: 'Volyn', UA09: 'Luhansk', UA12: 'Dnipropetrovsk', UA14: 'Donetsk',
  UA18: 'Zhytomyr', UA21: 'Zakarpattia', UA23: 'Zaporizhzhia', UA26: 'Ivano-Frankivsk',
  UA30: 'Kyiv', UA32: 'Kyiv City', UA35: 'Kirovohrad', UA40: 'Sevastopol', UA43: 'Crimea',
  UA46: 'Lviv', UA48: 'Mykolaiv', UA51: 'Odesa', UA53: 'Poltava', UA56: 'Rivne',
  UA59: 'Sumy', UA61: 'Ternopil', UA63: 'Kharkiv', UA65: 'Kherson', UA68: 'Khmelnytskyi',
  UA71: 'Cherkasy', UA74: 'Chernihiv', UA77: 'Chernivtsi',
};

export function getRegionData() {
  const raw = {
    UA05: { energy_score: 4, military_score: 3, logistics_score: 6, has_nuclear: 'no' },
    UA07: { energy_score: 2, military_score: 4, logistics_score: 5, has_nuclear: 'no' },
    UA09: { energy_score: 8, military_score: 9, logistics_score: 7, has_nuclear: 'no' },
    UA12: { energy_score: 9, military_score: 8, logistics_score: 9, has_nuclear: 'no' },
    UA14: { energy_score: 9, military_score: 10, logistics_score: 8, has_nuclear: 'no' },
    UA18: { energy_score: 3, military_score: 4, logistics_score: 5, has_nuclear: 'no' },
    UA21: { energy_score: 2, military_score: 3, logistics_score: 4, has_nuclear: 'no' },
    UA23: { energy_score: 8, military_score: 8, logistics_score: 8, has_nuclear: 'no' },
    UA26: { energy_score: 3, military_score: 4, logistics_score: 5, has_nuclear: 'no' },
    UA30: { energy_score: 7, military_score: 9, logistics_score: 10, has_nuclear: 'no' },
    UA32: { energy_score: 5, military_score: 7, logistics_score: 8, has_nuclear: 'no' },
    UA35: { energy_score: 4, military_score: 4, logistics_score: 6, has_nuclear: 'no' },
    UA40: { energy_score: 6, military_score: 9, logistics_score: 7, has_nuclear: 'no' },
    UA43: { energy_score: 7, military_score: 9, logistics_score: 6, has_nuclear: 'no' },
    UA46: { energy_score: 5, military_score: 6, logistics_score: 7, has_nuclear: 'no' },
    UA48: { energy_score: 6, military_score: 7, logistics_score: 7, has_nuclear: 'no' },
    UA51: { energy_score: 7, military_score: 7, logistics_score: 9, has_nuclear: 'no' },
    UA53: { energy_score: 5, military_score: 5, logistics_score: 7, has_nuclear: 'no' },
    UA56: { energy_score: 3, military_score: 4, logistics_score: 5, has_nuclear: 'no' },
    UA59: { energy_score: 5, military_score: 6, logistics_score: 6, has_nuclear: 'no' },
    UA61: { energy_score: 3, military_score: 4, logistics_score: 5, has_nuclear: 'no' },
    UA63: { energy_score: 9, military_score: 9, logistics_score: 9, has_nuclear: 'no' },
    UA65: { energy_score: 6, military_score: 8, logistics_score: 7, has_nuclear: 'no' },
    UA68: { energy_score: 4, military_score: 4, logistics_score: 6, has_nuclear: 'no' },
    UA71: { energy_score: 5, military_score: 5, logistics_score: 7, has_nuclear: 'no' },
    UA74: { energy_score: 6, military_score: 6, logistics_score: 6, has_nuclear: 'yes' },
    UA77: { energy_score: 2, military_score: 3, logistics_score: 4, has_nuclear: 'no' },
  };

  const withSum = REGION_IDS.map((id) => ({
    id,
    name: names[id] || id,
    ...raw[id],
    _sum: raw[id].energy_score + raw[id].military_score + raw[id].logistics_score,
  }));

  withSum.sort((a, b) => b._sum - a._sum);
  const rankById = {};
  withSum.forEach((r, i) => { rankById[r.id] = i + 1; });

  return REGION_IDS.map((id) => {
    const rank = rankById[id];
    const riskPercent = Math.max(15, 99 - (rank - 1) * 3.5);
    const confidence = Math.min(92, 78 + (28 - rank));
    return {
      id,
      name: names[id] || id,
      ...raw[id],
      riskRank: rank,
      riskPercent: Math.round(riskPercent),
      confidence,
    };
  });
}

export function getRankedRegions() {
  return [...getRegionData()].sort((a, b) => a.riskRank - b.riskRank);
}

export const RISK_COLORS = {
  1: '#8f0e00',   // top 1 dark red
  2: '#c71400',    // top 2-3 red
  3: '#c71400',
  4: '#c75000',   // top 4-5 orange
  5: '#c75000',
  6: '#dfdb00',   // top 6-10 yellow
  7: '#dfdb00',
  8: '#dfdb00',
  9: '#dfdb00',
  10: '#dfdb00',
  default: '#27ae60', // rest green
};

export function getFillForRank(rank) {
  return RISK_COLORS[rank] ?? RISK_COLORS.default;
}
