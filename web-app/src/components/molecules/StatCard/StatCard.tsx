import { FC } from 'react';
import { motion } from 'framer-motion';
import { IconType } from 'react-icons';

interface StatCardProps {
  icon: IconType;
  label: string;
  value: string;
  trend: string;
  trendDirection: 'up' | 'down';
}

export const StatCard: FC<StatCardProps> = ({
  icon: Icon,
  label,
  value,
  trend,
  trendDirection,
}) => {
  const trendColor = trendDirection === 'up' ? 'text-green-400' : 'text-red-400';

  return (
    <motion.div
      className="glass-card-heavy p-6 rounded-2xl flex flex-col gap-4 hover-lift hover-glow-purple"
      whileHover={{ scale: 1.02 }}
    >
      <div className="flex items-center justify-between">
        <h3 className="font-heading text-lg text-text-secondary">{label}</h3>
        <Icon className="text-3xl text-primary" />
      </div>
      <div>
        <p className="text-4xl font-display text-text-primary">{value}</p>
        <p className={`text-sm ${trendColor}`}>{trend}</p>
      </div>
    </motion.div>
  );
};
