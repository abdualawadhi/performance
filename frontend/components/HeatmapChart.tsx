"use client"

import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface HeatmapChartProps {
  data: any[];
  xLabels: string[];
  yLabels: string[];
  title: string;
  subtitle?: string;
}

const HeatmapChart: React.FC<HeatmapChartProps> = ({ data, xLabels, yLabels, title, subtitle }) => {
  const getColor = (value: number) => {
    if (value >= 90) return '#16a34a'; // green
    if (value >= 80) return '#a3e635';
    if (value >= 70) return '#fde047';
    if (value >= 60) return '#f59e0b'; // orange
    return '#dc2626'; // red
  };

  const shapedData = data.map((row, i) =>
    row.map((value: number, j: number) => ({
      x: j,
      y: i,
      z: value,
    }))
  ).flat();

  return (
    <div className="card p-6">
      <h3 className="text-lg font-bold text-grey-900">{title}</h3>
      {subtitle && <p className="text-sm text-grey-600 mt-1">{subtitle}</p>}
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 100 }}>
          <CartesianGrid />
          <XAxis type="number" dataKey="x" name="Category" ticks={xLabels.map((_, i) => i)} formatters={(value: number) => xLabels[value]} />
          <YAxis type="number" dataKey="y" name="Scenario" ticks={yLabels.map((_, i) => i)} formatters={(value: number) => yLabels[value]} />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
          <Scatter name="Performance" data={shapedData} fill="#8884d8" shape="square" >
            {shapedData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.z)} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

export default HeatmapChart;
