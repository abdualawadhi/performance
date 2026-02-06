"use client"

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

interface WaterfallChartProps {
  data: any[];
  title: string;
  subtitle?: string;
}

const WaterfallChart: React.FC<WaterfallChartProps> = ({ data, title, subtitle }) => {
  const colors: { [key: string]: string } = {
    script: '#8884d8',
    css: '#82ca9d',
    img: '#ffc658',
    font: '#ff8042',
    other: '#d3d3d3',
  };

  return (
    <div className="card p-6">
      <h3 className="text-lg font-bold text-grey-900">{title}</h3>
      {subtitle && <p className="text-sm text-grey-600 mt-1">{subtitle}</p>}
      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" unit="ms" />
          <YAxis type="category" dataKey="name" width={150} />
          <Tooltip />
          <Legend />
          <Bar dataKey="start" stackId="a" fill="transparent" />
          <Bar dataKey="duration" stackId="a">
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[entry.type] || colors.other} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default WaterfallChart;
