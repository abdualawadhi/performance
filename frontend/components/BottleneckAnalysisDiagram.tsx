"use client"

import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface BottleneckAnalysisDiagramProps {
  data: any[];
  title: string;
  subtitle?: string;
}

const BottleneckAnalysisDiagram: React.FC<BottleneckAnalysisDiagramProps> = ({ data, title, subtitle }) => {
  return (
    <div className="card p-6">
      <h3 className="text-lg font-bold text-grey-900">{title}</h3>
      {subtitle && <p className="text-sm text-grey-600 mt-1">{subtitle}</p>}
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart
          margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
        >
          <CartesianGrid />
          <XAxis type="number" dataKey="x" name="Impact" unit="%" />
          <YAxis type="number" dataKey="y" name="Effort" unit="%" />
          <ZAxis type="number" dataKey="z" range={[100, 1000]} name="Severity" />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
          <Legend />
          <Scatter name="Bottlenecks" data={data} fill="#8884d8" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

export default BottleneckAnalysisDiagram;
