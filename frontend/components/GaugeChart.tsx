"use client"

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

interface GaugeChartProps {
  value: number;
  maxValue: number;
  label: string;
  unit: string;
}

const GaugeChart: React.FC<GaugeChartProps> = ({ value, maxValue, label, unit }) => {
  const percentage = (value / maxValue) * 100;
  const data = [{ value: percentage }, { value: 100 - percentage }];

  const getColor = (value: number) => {
    if (label === 'LCP') {
      if (value <= 2500) return '#16a34a';
      if (value <= 4000) return '#f59e0b';
      return '#dc2626';
    }
    if (label === 'FID') {
      if (value <= 100) return '#16a34a';
      if (value <= 300) return '#f59e0b';
      return '#dc2626';
    }
    if (label === 'CLS') {
      if (value <= 0.1) return '#16a34a';
      if (value <= 0.25) return '#f59e0b';
      return '#dc2626';
    }
    return '#16a34a';
  };

  const color = getColor(value);

  return (
    <div className="flex flex-col items-center">
      <ResponsiveContainer width="100%" height={120}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="100%"
            startAngle={180}
            endAngle={0}
            innerRadius={60}
            outerRadius={80}
            fill="#8884d8"
            paddingAngle={0}
            dataKey="value"
          >
            <Cell fill={color} />
            <Cell fill="#e2e8f0" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="text-center mt-[-40px]">
        <div className="text-2xl font-bold" style={{ color }}>
          {value}
          <span className="text-lg font-medium text-gray-600">{unit}</span>
        </div>
        <div className="text-sm text-gray-500">{label}</div>
      </div>
    </div>
  );
};

export default GaugeChart;
