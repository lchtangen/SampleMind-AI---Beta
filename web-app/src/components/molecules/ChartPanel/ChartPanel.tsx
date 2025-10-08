import { FC } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { motion } from 'framer-motion';

interface ChartPanelProps {
  data: any[];
  title: string;
}

export const ChartPanel: FC<ChartPanelProps> = ({ data, title }) => {
  return (
    <motion.div
      className="glass-card p-6 rounded-2xl"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h3 className="font-heading text-xl text-text-primary mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis dataKey="name" stroke="rgba(255, 255, 255, 0.4)" />
          <YAxis stroke="rgba(255, 255, 255, 0.4)" />
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(10, 10, 15, 0.8)',
              borderColor: '#8B5CF6',
              color: '#fff',
            }}
          />
          <Area
            type="monotone"
            dataKey="uv"
            stroke="#8B5CF6"
            fillOpacity={1}
            fill="url(#colorUv)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </motion.div>
  );
};
