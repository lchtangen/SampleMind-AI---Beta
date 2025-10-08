/**
 * Music Generation Page
 *
 * AI-powered music generation with customizable parameters
 */

import { useState } from 'react';
import { Wand2, Sparkles, Music, Download, Play, RefreshCw } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AIProviderSelector } from '@/components/ai/AIProviderSelector';
import { useAppStore } from '@/store/appStore';

export default function Generate() {
  const { generations, addGeneration } = useAppStore((state) => ({
    generations: state.generations,
    addGeneration: state.addGeneration,
  }));

  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState('');
  const [mood, setMood] = useState('');
  const [tempo, setTempo] = useState(120);
  const [aiProvider, setAiProvider] = useState('anthropic');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = () => {
    if (!prompt.trim()) return;

    const newGeneration = {
      id: `gen-${Date.now()}`,
      prompt,
      style,
      mood,
      tempo,
      status: 'generating' as const,
      generatedAt: new Date(),
    };

    addGeneration(newGeneration);
    setIsGenerating(true);

    // Simulate generation process
    setTimeout(() => {
      setIsGenerating(false);
      // TODO: Update generation status via backend
    }, 5000);
  };

  const styles = [
    'Electronic', 'Hip-Hop', 'Rock', 'Jazz', 'Classical', 'Ambient',
    'House', 'Techno', 'Dubstep', 'Lo-fi', 'Synthwave', 'Drum & Bass'
  ];

  const moods = [
    'Energetic', 'Calm', 'Dark', 'Uplifting', 'Melancholic', 'Aggressive',
    'Dreamy', 'Intense', 'Playful', 'Epic', 'Minimal', 'Cinematic'
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold gradient-text">AI Music Generation</h1>
        <p className="mt-2 text-slate-400">
          Create unique music tracks with AI-powered generation
        </p>
      </div>

      {/* Main Content */}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Generation Controls */}
        <div className="lg:col-span-2 space-y-6">
          {/* Prompt */}
          <Card className="border-white/10 bg-slate-800/50 p-6">
            <h3 className="mb-4 text-lg font-semibold text-white">Describe Your Music</h3>
            <div className="space-y-4">
              <div>
                <label className="mb-2 block text-sm text-slate-400">
                  Prompt (describe the music you want to create)
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="A uplifting electronic track with energetic drums and melodic synths..."
                  className="w-full min-h-[120px] rounded-lg border border-white/10 bg-slate-900/50 p-3 text-white placeholder:text-slate-500 focus:border-cyan-500 focus:outline-none"
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="mb-2 block text-sm text-slate-400">Style (optional)</label>
                  <Input
                    value={style}
                    onChange={(e) => setStyle(e.target.value)}
                    placeholder="e.g., Electronic"
                    className="border-white/10 bg-slate-900/50 text-white"
                  />
                </div>
                <div>
                  <label className="mb-2 block text-sm text-slate-400">Mood (optional)</label>
                  <Input
                    value={mood}
                    onChange={(e) => setMood(e.target.value)}
                    placeholder="e.g., Energetic"
                    className="border-white/10 bg-slate-900/50 text-white"
                  />
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm text-slate-400">
                  Tempo: {tempo} BPM
                </label>
                <input
                  type="range"
                  min="60"
                  max="200"
                  value={tempo}
                  onChange={(e) => setTempo(parseInt(e.target.value))}
                  className="w-full cursor-pointer appearance-none bg-transparent [&::-webkit-slider-runnable-track]:h-2 [&::-webkit-slider-runnable-track]:rounded-full [&::-webkit-slider-runnable-track]:bg-slate-700 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-cyan-500"
                />
              </div>
            </div>
          </Card>

          {/* Quick Style Presets */}
          <Card className="border-white/10 bg-slate-800/50 p-6">
            <h3 className="mb-4 text-lg font-semibold text-white">Quick Style Presets</h3>
            <Tabs defaultValue="styles">
              <TabsList className="grid w-full grid-cols-2 bg-slate-900/50">
                <TabsTrigger value="styles">Styles</TabsTrigger>
                <TabsTrigger value="moods">Moods</TabsTrigger>
              </TabsList>
              <TabsContent value="styles" className="mt-4">
                <div className="flex flex-wrap gap-2">
                  {styles.map((s) => (
                    <Badge
                      key={s}
                      className={`cursor-pointer transition-all ${
                        style === s
                          ? 'bg-cyan-500 text-white'
                          : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                      }`}
                      onClick={() => setStyle(s)}
                    >
                      {s}
                    </Badge>
                  ))}
                </div>
              </TabsContent>
              <TabsContent value="moods" className="mt-4">
                <div className="flex flex-wrap gap-2">
                  {moods.map((m) => (
                    <Badge
                      key={m}
                      className={`cursor-pointer transition-all ${
                        mood === m
                          ? 'bg-purple-500 text-white'
                          : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                      }`}
                      onClick={() => setMood(m)}
                    >
                      {m}
                    </Badge>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </Card>

          {/* AI Provider */}
          <AIProviderSelector selected={aiProvider} onSelect={setAiProvider} />

          {/* Generate Button */}
          <Button
            onClick={handleGenerate}
            disabled={!prompt.trim() || isGenerating}
            className="w-full bg-gradient-to-r from-purple-500 via-blue-500 to-cyan-500 py-6 text-lg font-semibold text-white shadow-lg shadow-purple-500/20 hover:shadow-purple-500/40"
          >
            {isGenerating ? (
              <>
                <RefreshCw className="mr-2 h-5 w-5 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Wand2 className="mr-2 h-5 w-5" />
                Generate Music
              </>
            )}
          </Button>
        </div>

        {/* Generation History */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white">Generation History</h3>
          
          {generations.length === 0 ? (
            <Card className="border-white/10 bg-slate-800/50 p-8">
              <div className="flex flex-col items-center gap-3 text-center">
                <Music className="h-12 w-12 text-slate-400" />
                <p className="text-sm text-slate-400">No generations yet</p>
              </div>
            </Card>
          ) : (
            generations.map((gen) => (
              <Card key={gen.id} className="border-white/10 bg-slate-800/50 p-4">
                <div className="mb-3 flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="truncate text-sm font-medium text-white">{gen.prompt}</p>
                    <div className="mt-1 flex gap-2">
                      {gen.style && <Badge variant="secondary" className="text-xs">{gen.style}</Badge>}
                      {gen.mood && <Badge variant="secondary" className="text-xs">{gen.mood}</Badge>}
                    </div>
                  </div>
                  <Badge
                    className={`flex-shrink-0 ${
                      gen.status === 'completed'
                        ? 'bg-green-500/10 text-green-400'
                        : gen.status === 'generating'
                        ? 'bg-blue-500/10 text-blue-400'
                        : gen.status === 'failed'
                        ? 'bg-red-500/10 text-red-400'
                        : 'bg-slate-500/10 text-slate-400'
                    }`}
                  >
                    {gen.status}
                  </Badge>
                </div>

                {gen.status === 'generating' && (
                  <Progress value={45} className="h-1" />
                )}

                {gen.status === 'completed' && (
                  <div className="mt-3 flex gap-2">
                    <Button size="sm" variant="outline" className="flex-1 border-purple-500/50 text-purple-400">
                      <Play className="mr-1 h-3 w-3" />
                      Play
                    </Button>
                    <Button size="sm" variant="outline" className="border-cyan-500/50 text-cyan-400">
                      <Download className="h-3 w-3" />
                    </Button>
                  </div>
                )}
              </Card>
            ))
          )}
        </div>
      </div>

      {/* Tips */}
      <Card className="border-white/10 bg-gradient-to-r from-purple-500/10 via-blue-500/10 to-cyan-500/10 p-6">
        <div className="flex gap-3">
          <Sparkles className="h-5 w-5 flex-shrink-0 text-cyan-400" />
          <div>
            <h4 className="font-semibold text-white">Pro Tips for Better Results</h4>
            <ul className="mt-2 space-y-1 text-sm text-slate-300">
              <li>• Be specific about instruments, rhythm, and atmosphere</li>
              <li>• Reference existing genres or artists for style guidance</li>
              <li>• Describe the energy level and emotional feel you want</li>
              <li>• Experiment with different AI providers for varied results</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  );
}
