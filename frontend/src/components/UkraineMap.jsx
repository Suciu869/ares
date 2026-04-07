import { useEffect, useRef } from 'react';
import { getRegionData, getFillForRank } from '../data/regions';

const regionDataById = Object.fromEntries(
  getRegionData().map((r) => [r.id, r])
);

const HIGHLIGHT_FILTER = 'drop-shadow(0 0 12px rgba(255,255,255,0.6)) brightness(1.3)';

function applySelection(el, selectedId, aiRankById) {
  if (!el) return;
  const paths = el.querySelectorAll('path[id^="UA"]');
  paths.forEach((path) => {
    const id = path.getAttribute('id');
    const data = regionDataById[id];
    if (!data) return;
    const isSelected = id === selectedId;
    const rank = (aiRankById && aiRankById[id]) || data.riskRank;
    path.style.fill = getFillForRank(rank);
    path.style.filter = isSelected ? HIGHLIGHT_FILTER : '';
  });
}

export function UkraineMap({ selectedId, onSelectRegion, aiRankById }) {
  const containerRef = useRef(null);
  const onSelectRef = useRef(onSelectRegion);
  const selectedIdRef = useRef(selectedId);
  onSelectRef.current = onSelectRegion;
  selectedIdRef.current = selectedId;

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    fetch('/ua.svg')
      .then((res) => res.text())
      .then((svgText) => {
        el.innerHTML = svgText;
        const svg = el.querySelector('svg');
        if (!svg) return;
        svg.style.width = '100%';
        svg.style.height = 'auto';
        svg.style.display = 'block';
        svg.setAttribute('stroke', '#ffffff');
        svg.setAttribute('stroke-width', '0.5');

        const paths = el.querySelectorAll('path[id^="UA"]');
        paths.forEach((path) => {
          const id = path.getAttribute('id');
          const data = regionDataById[id];
          if (data) {
            path.style.fill = getFillForRank(data.riskRank);
            path.style.cursor = 'pointer';
            path.style.transition = 'filter 0.2s ease, fill 0.2s ease';
            path.addEventListener('mouseenter', () => {
              if (id !== selectedIdRef.current) {
                path.style.filter = 'drop-shadow(0 0 10px rgba(255,255,255,0.5)) brightness(1.25)';
              }
            });
            path.addEventListener('mouseleave', () => {
              if (id !== selectedIdRef.current) path.style.filter = '';
            });
            path.addEventListener('click', () => onSelectRef.current?.(id));
          }
        });
        applySelection(el, selectedId, aiRankById);
      })
      .catch(console.error);

    return () => {
      el.innerHTML = '';
    };
  }, []);

  useEffect(() => {
    applySelection(containerRef.current, selectedId, aiRankById);
  }, [selectedId, aiRankById]);

  return <div ref={containerRef} className="map-container" />;
}
