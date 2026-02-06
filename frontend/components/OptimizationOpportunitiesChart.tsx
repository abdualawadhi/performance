"use client"

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

interface OptimizationOpportunitiesChartProps {
  data: any[];
  title: string;
  subtitle?: string;
}

const OptimizationOpportunitiesChart: React.FC<OptimizationOpportunitiesChartProps> = ({ data, title, subtitle }) => {
  const effortColors: { [key: string]: string } = {
    Low: '#16a34a',
    Medium: '#f59e0b',
    High: '#dc2626',
  };

  return (
    <div className="card p-6">
      <h3 className="text-lg font-bold text-grey-900">{title}</h3>
      {subtitle && <p className="text-sm text-grey-600 mt-1">{subtitle}</p>}
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis type="category" dataKey="category" width={150} />
          <Tooltip />
          <Legend />
          <Bar dataKey="impact_score" name="Impact Score">
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={effortColors[entry.effort_level]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default OptimizationOpportunitiesChart;
