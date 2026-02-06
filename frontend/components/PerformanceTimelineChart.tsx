"use client"

import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceDot } from 'recharts';

interface PerformanceTimelineChartProps {
  data: any[];
  title: string;
  subtitle?: string;
}

const PerformanceTimelineChart: React.FC<PerformanceTimelineChartProps> = ({ data, title, subtitle }) => {
  return (
    <div className="card p-6">
      <h3 className="text-lg font-bold text-grey-900">{title}</h3>
      {subtitle && <p className="text-sm text-grey-600 mt-1">{subtitle}</p>}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={data}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" type="number" unit="ms" />
          <YAxis dataKey="value" unit="%" />
          <Tooltip labelFormatter={(label) => `${label}ms`} />
          <Legend />
          <Line type="monotone" dataKey="value" stroke="#8884d8" strokeWidth={2} name="Progress" />
          {data.map((entry, index) => (
            <ReferenceDot key={`dot-${index}`} x={entry.time} y={entry.value} r={5} fill="#8884d8" stroke="white" />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PerformanceTimelineChart;
