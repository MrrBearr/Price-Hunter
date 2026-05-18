'use client';

import { PriceHistory } from '@/types';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface PriceChartProps {
  data: PriceHistory[];
}

export default function PriceChart({ data }: PriceChartProps) {
  const chartData = data.map((item) => ({
    date: new Date(item.recorded_at).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
    price: item.price,
    total: item.price + item.shipping_cost,
  }));

  return (
    <div className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="date"
            stroke="#94a3b8"
            tick={{ fontSize: 12 }}
          />
          <YAxis
            stroke="#94a3b8"
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => `R$${value}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '8px',
            }}
            labelStyle={{ color: '#e2e8f0' }}
            formatter={(value: number, name: string) => [
              `R$ ${value.toFixed(2)}`,
              name === 'price' ? 'Preco' : 'Total c/ Frete',
            ]}
          />
          <Legend
            formatter={(value) => (value === 'price' ? 'Preco' : 'Total c/ Frete')}
          />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ fill: '#3b82f6', strokeWidth: 2, r: 3 }}
            activeDot={{ r: 5 }}
          />
          <Line
            type="monotone"
            dataKey="total"
            stroke="#10b981"
            strokeWidth={2}
            dot={{ fill: '#10b981', strokeWidth: 2, r: 3 }}
            activeDot={{ r: 5 }}
            strokeDasharray="5 5"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
