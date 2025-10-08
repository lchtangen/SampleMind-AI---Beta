/**
 * AIProviderSelector Component
 * 
 * Select and configure AI provider for audio analysis
 */

import { useState } from 'react';
import { Brain, Sparkles, Zap, Check } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface AIProvider {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  features: string[];
  speed: 'fast' | 'medium' | 'slow';
  quality: 'high' | 'medium' | 'low';
  available: boolean;
}

const providers: AIProvider[] = [
  {
    id: 'openai',
    name: 'OpenAI GPT-4',
    description: 'Advanced language model for detailed audio analysis',
    icon: Sparkles,
    features: ['Genre Detection', 'Mood Analysis', 'Detailed Descriptions'],
    speed: 'medium',
    quality: 'high',
    available: true,
  },
  {
    id: 'anthropic',
    name: 'Claude 3.5',
    description: 'Sophisticated audio understanding and recommendations',
    icon: Brain,
    features: ['Technical Analysis', 'Production Tips', 'Sound Design'],
    speed: 'fast',
    quality: 'high',
    available: true,
  },
  {
    id: 'google',
    name: 'Google Gemini',
    description: 'Multimodal AI for comprehensive audio processing',
    icon: Zap,
    features: ['Real-time Processing', 'Multi-track Analysis', 'Mix Feedback'],
    speed: 'fast',
    quality: 'high',
    available: true,
  },
];

interface AIProviderSelectorProps {
  selected?: string;
  onSelect?: (providerId: string) => void;
}

export function AIProviderSelector({ selected, onSelect }: AIProviderSelectorProps) {
  const [selectedProvider, setSelectedProvider] = useState(selected || 'anthropic');

  const handleSelect = (providerId: string) => {
    setSelectedProvider(providerId);
    onSelect?.(providerId);
  };

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-white">Choose AI Provider</h3>
        <p className="text-sm text-slate-400">
          Select the AI engine to power your audio analysis
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {providers.map((provider) => {
          const Icon = provider.icon;
          const isSelected = selectedProvider === provider.id;

          return (
            <Card
              key={provider.id}
              className={cn(
                'cursor-pointer border-2 transition-all duration-300',
                isSelected
                  ? 'border-cyan-500 bg-cyan-500/10 shadow-lg shadow-cyan-500/20'
                  : 'border-white/10 bg-slate-800/50 hover:border-purple-500/50 hover:bg-slate-800/70',
                !provider.available && 'opacity-50 cursor-not-allowed'
              )}
              onClick={() => provider.available && handleSelect(provider.id)}
            >
              <div className="p-6">
                {/* Header */}
                <div className="mb-4 flex items-start justify-between">
                  <div className={cn(
                    'flex h-12 w-12 items-center justify-center rounded-lg',
                    isSelected
                      ? 'bg-gradient-to-br from-cyan-500 to-blue-600'
                      : 'bg-gradient-to-br from-purple-500 to-blue-600'
                  )}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  {isSelected && (
                    <div className="flex h-6 w-6 items-center justify-center rounded-full bg-cyan-500">
                      <Check className="h-4 w-4 text-white" />
                    </div>
                  )}
                </div>

                {/* Title */}
                <h4 className="mb-2 text-lg font-semibold text-white">{provider.name}</h4>
                <p className="mb-4 text-sm text-slate-400">{provider.description}</p>

                {/* Badges */}
                <div className="mb-4 flex gap-2">
                  <Badge
                    className={cn(
                      'text-xs',
                      provider.speed === 'fast' && 'bg-green-500/10 text-green-400',
                      provider.speed === 'medium' && 'bg-yellow-500/10 text-yellow-400',
                      provider.speed === 'slow' && 'bg-red-500/10 text-red-400'
                    )}
                  >
                    {provider.speed} speed
                  </Badge>
                  <Badge
                    className={cn(
                      'text-xs',
                      provider.quality === 'high' && 'bg-purple-500/10 text-purple-400',
                      provider.quality === 'medium' && 'bg-blue-500/10 text-blue-400'
                    )}
                  >
                    {provider.quality} quality
                  </Badge>
                </div>

                {/* Features */}
                <div className="space-y-2">
                  {provider.features.map((feature, index) => (
                    <div key={index} className="flex items-center gap-2 text-sm text-slate-300">
                      <div className="h-1.5 w-1.5 rounded-full bg-cyan-400" />
                      {feature}
                    </div>
                  ))}
                </div>

                {/* Status */}
                {!provider.available && (
                  <div className="mt-4">
                    <Badge variant="secondary" className="bg-slate-700 text-slate-400">
                      Coming Soon
                    </Badge>
                  </div>
                )}
              </div>
            </Card>
          );
        })}
      </div>

      {/* Selected Provider Info */}
      {selectedProvider && (
        <Card className="border-white/10 bg-gradient-to-r from-purple-500/10 via-blue-500/10 to-cyan-500/10 p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-purple-500 to-cyan-500">
              <Check className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-white">
                Using {providers.find(p => p.id === selectedProvider)?.name}
              </p>
              <p className="text-xs text-slate-400">
                AI provider configured and ready for analysis
              </p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="text-cyan-400 hover:bg-cyan-500/10"
            >
              Configure
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}