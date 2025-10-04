import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import Badge from '../ui/Badge';
import { Music, Brain, Zap, TrendingUp } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface AnalysisData {
  tempo?: number;
  key?: string;
  energy?: number;
  mood?: string;
  genre?: string;
  instruments?: string[];
  tags?: string[];
  aiInsights?: string;
}

export interface AnalysisCardProps {
  analysis: AnalysisData;
  className?: string;
}

const AnalysisCard: React.FC<AnalysisCardProps> = ({ analysis, className }) => {
  return (
    <Card variant="bordered" className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="text-blue-600" size={24} />
          Analysis Results
        </CardTitle>
      </CardHeader>

      <CardContent>
        <div className="space-y-6">
          {/* Audio Features */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <Music size={16} />
              Audio Features
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {analysis.tempo && (
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Tempo</p>
                  <p className="text-lg font-semibold text-gray-900">{analysis.tempo} BPM</p>
                </div>
              )}
              {analysis.key && (
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Key</p>
                  <p className="text-lg font-semibold text-gray-900">{analysis.key}</p>
                </div>
              )}
              {analysis.energy !== undefined && (
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Energy</p>
                  <div className="flex items-center gap-2">
                    <p className="text-lg font-semibold text-gray-900">
                      {(analysis.energy * 100).toFixed(0)}%
                    </p>
                    <Zap
                      className={cn(
                        'flex-shrink-0',
                        analysis.energy > 0.7 ? 'text-yellow-500' : 'text-gray-400'
                      )}
                      size={16}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Genre & Mood */}
          {(analysis.genre || analysis.mood) && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <TrendingUp size={16} />
                Classification
              </h4>
              <div className="flex flex-wrap gap-2">
                {analysis.genre && (
                  <Badge variant="info" size="md">
                    Genre: {analysis.genre}
                  </Badge>
                )}
                {analysis.mood && (
                  <Badge variant="success" size="md">
                    Mood: {analysis.mood}
                  </Badge>
                )}
              </div>
            </div>
          )}

          {/* Instruments */}
          {analysis.instruments && analysis.instruments.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-3">Detected Instruments</h4>
              <div className="flex flex-wrap gap-2">
                {analysis.instruments.map((instrument, index) => (
                  <Badge key={index} variant="outline" size="sm">
                    {instrument}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Tags */}
          {analysis.tags && analysis.tags.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-3">Tags</h4>
              <div className="flex flex-wrap gap-2">
                {analysis.tags.map((tag, index) => (
                  <Badge key={index} variant="default" size="sm">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* AI Insights */}
          {analysis.aiInsights && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <Brain size={16} />
                AI Insights
              </h4>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-gray-700 whitespace-pre-line">{analysis.aiInsights}</p>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default AnalysisCard;
