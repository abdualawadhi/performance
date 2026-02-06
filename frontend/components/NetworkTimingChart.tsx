"use client"

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface NetworkTimingChartProps {
  data: any[];
  title: string;
  subtitle?: string;
}

const NetworkTimingChart: React.FC<NetworkTimingChartProps> = ({ data, title, subtitle }) => {
  return (
    <div className="card p-6">
      <h3 className="text-lg font-bold text-grey-900">{title}</h3>
      {subtitle && <p className="text-sm text-grey-600 mt-1">{subtitle}</p>}
      <ResponsiveContainer width="100%" height={100}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" unit="ms" />
          <YAxis type="category" dataKey="stage" />
          <Tooltip />
          <Legend />
          <Bar dataKey="time" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default NetworkTimingChart;
