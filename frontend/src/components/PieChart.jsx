import React, { useState } from 'react';

/**
 * Interactive SVG Donut / Pie Chart Component
 * Features:
 * - Pure SVG rendering with animated hover states
 * - Center metrics display (total or hovered slice details)
 * - Interactive slice hover with outline glow
 * - Formatted responsive legend with percentage bars
 */
export const PieChart = ({
  data = [],
  title,
  subtitle,
  size = 220,
  donut = true,
  className = ''
}) => {
  const [hoveredIndex, setHoveredIndex] = useState(null);

  // Filter valid data items
  const validData = data.filter((item) => typeof item.value === 'number' && item.value > 0);
  const total = validData.reduce((sum, item) => sum + item.value, 0);

  const radius = size / 2;
  const strokeWidth = donut ? size * 0.22 : radius;
  const innerRadius = radius - strokeWidth / 2;

  // Calculate SVG arc paths
  let cumulativeAngle = -Math.PI / 2; // Start from 12 o'clock

  const slices = validData.map((item, index) => {
    const sliceAngle = total > 0 ? (item.value / total) * 2 * Math.PI : 0;
    const startAngle = cumulativeAngle;
    const endAngle = cumulativeAngle + sliceAngle;
    cumulativeAngle += sliceAngle;

    // Outer & inner arc coordinates
    const x1 = radius + (radius - 12) * Math.cos(startAngle);
    const y1 = radius + (radius - 12) * Math.sin(startAngle);
    const x2 = radius + (radius - 12) * Math.cos(endAngle);
    const y2 = radius + (radius - 12) * Math.sin(endAngle);

    const isLargeArc = sliceAngle > Math.PI ? 1 : 0;

    let pathData = '';
    if (donut) {
      // Donut slice using inner and outer radiuses
      const innerR = radius - strokeWidth;
      const x1Inner = radius + innerR * Math.cos(endAngle);
      const y1Inner = radius + innerR * Math.sin(endAngle);
      const x2Inner = radius + innerR * Math.cos(startAngle);
      const y2Inner = radius + innerR * Math.sin(startAngle);

      pathData = `
        M ${x1} ${y1}
        A ${radius - 12} ${radius - 12} 0 ${isLargeArc} 1 ${x2} ${y2}
        L ${x1Inner} ${y1Inner}
        A ${innerR} ${innerR} 0 ${isLargeArc} 0 ${x2Inner} ${y2Inner}
        Z
      `;
    } else {
      pathData = `
        M ${radius} ${radius}
        L ${x1} ${y1}
        A ${radius - 12} ${radius - 12} 0 ${isLargeArc} 1 ${x2} ${y2}
        Z
      `;
    }

    const percent = total > 0 ? ((item.value / total) * 100).toFixed(1) : 0;

    return {
      ...item,
      pathData,
      percent,
      index
    };
  });

  const activeSlice = hoveredIndex !== null ? slices[hoveredIndex] : null;

  return (
    <div className={`glass-card rounded-3xl p-6 border border-slate-800 flex flex-col justify-between ${className}`}>
      {/* Header */}
      {(title || subtitle) && (
        <div className="mb-4">
          {title && <h3 className="text-sm font-bold text-white tracking-wide">{title}</h3>}
          {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
        </div>
      )}

      {/* Center Chart */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-6 my-2">
        <div className="relative flex items-center justify-center shrink-0">
          {total === 0 ? (
            <div
              style={{ width: size, height: size }}
              className="rounded-full border-4 border-dashed border-slate-800 flex items-center justify-center text-xs text-slate-600 font-medium"
            >
              No Data Recorded
            </div>
          ) : (
            <svg
              width={size}
              height={size}
              viewBox={`0 0 ${size} ${size}`}
              className="transform transition-transform duration-300"
            >
              {/* Drop shadow filter */}
              <defs>
                <filter id="pie-glow" x="-20%" y="-20%" width="140%" height="140%">
                  <feDropShadow dx="0" dy="0" stdDeviation="4" floodOpacity="0.4" />
                </filter>
              </defs>

              {slices.map((slice) => {
                const isHovered = hoveredIndex === slice.index;
                return (
                  <path
                    key={slice.index}
                    d={slice.pathData}
                    fill={slice.color}
                    filter={isHovered ? "url(#pie-glow)" : "none"}
                    className={`cursor-pointer transition-all duration-200 ${
                      isHovered ? 'opacity-100 scale-105 origin-center stroke-white stroke-2' : 'opacity-90 hover:opacity-100'
                    }`}
                    onMouseEnter={() => setHoveredIndex(slice.index)}
                    onMouseLeave={() => setHoveredIndex(null)}
                  />
                );
              })}
            </svg>
          )}

          {/* Donut Center Overlay Text */}
          {donut && total > 0 && (
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none text-center px-4">
              <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">
                {activeSlice ? activeSlice.label : 'Total'}
              </span>
              <span className="text-2xl font-extrabold text-white tracking-tight">
                {activeSlice ? activeSlice.value : total}
              </span>
              <span className="text-[11px] font-semibold text-blue-400">
                {activeSlice ? `${activeSlice.percent}%` : '100%'}
              </span>
            </div>
          )}
        </div>

        {/* Legend Slices List */}
        <div className="flex-1 w-full space-y-2.5">
          {validData.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No entries available</p>
          ) : (
            validData.map((item, idx) => {
              const isHovered = hoveredIndex === idx;
              const percent = total > 0 ? ((item.value / total) * 100).toFixed(0) : 0;
              return (
                <div
                  key={idx}
                  onMouseEnter={() => setHoveredIndex(idx)}
                  onMouseLeave={() => setHoveredIndex(null)}
                  className={`p-2 rounded-xl transition-all cursor-pointer flex items-center justify-between text-xs ${
                    isHovered ? 'bg-slate-800/80 ring-1 ring-slate-700' : 'hover:bg-slate-900/60'
                  }`}
                >
                  <div className="flex items-center space-x-2.5 min-w-0">
                    <span
                      className="w-3 h-3 rounded-full shrink-0 shadow-sm"
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="font-semibold text-slate-300 truncate">{item.label}</span>
                  </div>

                  <div className="flex items-center space-x-3 shrink-0">
                    <span className="font-bold text-white">{item.value}</span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-slate-800 text-slate-400 min-w-[36px] text-right">
                      {percent}%
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

export default PieChart;
