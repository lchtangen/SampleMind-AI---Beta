/**
 * Analysis Dashboard Component
 *
 * Visualize audio analysis data with charts
 */

import {
  BarChart,
  Bar,
  LineChart,
  Line,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import type { AudioAnalysis } from '../store/appStore';

interface AnalysisDashboardProps {
  analysis: AudioAnalysis;
  showCharts?: boolean;
}

export default function AnalysisDashboard({
  analysis,
  showCharts = true,
}: AnalysisDashboardProps) {
  // Prepare chart data
  const metricsData = [
    {
      metric: 'Tempo',
      value: analysis.tempo,
      max: 200,
    },
    {
      metric: 'Energy',
      value: analysis.energy * 100,
      max: 100,
    },
    {
      metric: 'Spectral',
      value: (analysis.spectralCentroid / 10000) * 100,
      max: 100,
    },
  ];

  const radarData = [
    {
      metric: 'Tempo',
      value: (analysis.tempo / 200) * 100,
      fullMark: 100,
    },
    {
      metric: 'Energy',
      value: analysis.energy * 100,
      fullMark: 100,
    },
    {
      metric: 'Brightness',
      value: (analysis.spectralCentroid / 10000) * 100,
      fullMark: 100,
    },
  ];

  // Onset timeline data (if available)
  const onsetData = analysis.onsets?.slice(0, 50).map((time, index) => ({
    index,
    time: time.toFixed(2),
    intensity: 1,
  }));

  return (
    <div className="analysis-dashboard">
      <div className="analysis-header">
        <h2>Audio Analysis</h2>
        <p className="analysis-timestamp">
          Analyzed at {new Date(analysis.timestamp).toLocaleString()}
        </p>
      </div>

      {/* Key Metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <h4>Tempo</h4>
          <div className="metric-big-value">{analysis.tempo.toFixed(1)}</div>
          <div className="metric-unit">BPM</div>
        </div>

        <div className="metric-card">
          <h4>Key</h4>
          <div className="metric-big-value">{analysis.key}</div>
          <div className="metric-unit">Musical Key</div>
        </div>

        <div className="metric-card">
          <h4>Energy</h4>
          <div className="metric-big-value">
            {(analysis.energy * 100).toFixed(0)}%
          </div>
          <div className="metric-unit">Intensity</div>
        </div>

        <div className="metric-card">
          <h4>Brightness</h4>
          <div className="metric-big-value">
            {(analysis.spectralCentroid / 1000).toFixed(1)}k
          </div>
          <div className="metric-unit">Hz</div>
        </div>

        {analysis.pitch && (
          <div className="metric-card">
            <h4>Pitch</h4>
            <div className="metric-big-value">{analysis.pitch.toFixed(1)}</div>
            <div className="metric-unit">Hz</div>
          </div>
        )}

        {analysis.onsets && (
          <div className="metric-card">
            <h4>Onsets</h4>
            <div className="metric-big-value">{analysis.onsets.length}</div>
            <div className="metric-unit">Detected</div>
          </div>
        )}
      </div>

      {/* Charts */}
      {showCharts && (
        <div className="charts-grid">
          {/* Bar Chart - Metrics Comparison */}
          <div className="chart-card">
            <h3>Metrics Overview</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={metricsData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="metric" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '0.5rem',
                  }}
                />
                <Bar dataKey="value" fill="#6366f1" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Radar Chart - Audio Profile */}
          <div className="chart-card">
            <h3>Audio Profile</h3>
            <ResponsiveContainer width="100%" height={250}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="metric" stroke="#94a3b8" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="#94a3b8" />
                <Radar
                  name="Analysis"
                  dataKey="value"
                  stroke="#6366f1"
                  fill="#6366f1"
                  fillOpacity={0.6}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '0.5rem',
                  }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Onset Timeline */}
          {onsetData && onsetData.length > 0 && (
            <div className="chart-card full-width">
              <h3>Onset Detection Timeline</h3>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={onsetData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="time" stroke="#94a3b8" label={{ value: 'Time (s)', position: 'insideBottom', offset: -5 }} />
                  <YAxis stroke="#94a3b8" hide />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      border: '1px solid #334155',
                      borderRadius: '0.5rem',
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="intensity"
                    stroke="#10b981"
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
