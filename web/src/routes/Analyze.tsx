/**
 * Audio Analysis Page
 *
 * Upload and analyze audio files with AI-powered insights
 */

import { useState } from 'react';
import { Sparkles, Upload as UploadIcon } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AudioUploader } from '@/components/audio/AudioUploader';
import { WaveformPlayer } from '@/components/audio/WaveformPlayer';
import { AIProviderSelector } from '@/components/ai/AIProviderSelector';
import { AnalysisDisplay } from '@/components/ai/AnalysisDisplay';
import { useAppStore } from '@/store/appStore';

export default function Analyze() {
  const { selectedFile, selectFile, audioFiles } = useAppStore((state) => ({
    selectedFile: state.selectedFile,
    selectFile: state.selectFile,
    audioFiles: state.audioFiles,
  }));

  const [aiProvider, setAiProvider] = useState('anthropic');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleFilesSelected = (files: File[]) => {
    console.log('Files selected:', files);
    // TODO: Handle file upload to backend
  };

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    // TODO: Trigger AI analysis
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 3000);
  };

  // Mock analysis result for demo
  const mockAnalysis = selectedFile?.analysis || {
    genre: 'Electronic',
    mood: 'Energetic',
    tempo: 128,
    key: 'A Minor',
    energy: 0.85,
    danceability: 0.78,
    acousticness: 0.12,
    instrumentalness: 0.65,
    valence: 0.72,
    spectralCentroid: 2500,
    onsets: [],
    timestamp: Date.now(),
    summary:
      'This track features a driving electronic beat with energetic synth leads and a pulsating bassline. The production showcases modern EDM techniques with crisp percussion and dynamic arrangement. The overall mood is uplifting and dance-oriented, perfect for club environments or workout playlists.',
    suggestions: [
      'Consider adding more variation in the breakdown section to maintain listener engagement',
      'The hi-hats could benefit from subtle pitch modulation for added movement',
      'Experiment with sidechain compression on pads to create more space for the kick',
      'The transition at 2:15 could use a riser or impact for stronger emphasis',
      'Try layering the lead synth with a sub-bass for additional depth',
    ],
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold gradient-text">Audio Analysis</h1>
        <p className="mt-2 text-slate-400">
          Upload and analyze your audio files with AI-powered insights
        </p>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="upload" className="w-full">
        <TabsList className="grid w-full grid-cols-3 bg-slate-800/50">
          <TabsTrigger value="upload">Upload</TabsTrigger>
          <TabsTrigger value="analyze" disabled={!selectedFile}>
            Analyze
          </TabsTrigger>
          <TabsTrigger value="results" disabled={!selectedFile?.analyzed}>
            Results
          </TabsTrigger>
        </TabsList>

        {/* Upload Tab */}
        <TabsContent value="upload" className="space-y-6">
          <AudioUploader onFilesSelected={handleFilesSelected} maxFiles={5} maxSize={100} />

          {/* Recent Files */}
          {audioFiles.length > 0 && (
            <div>
              <h3 className="mb-4 text-lg font-semibold text-white">Your Files</h3>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {audioFiles.map((file) => (
                  <Card
                    key={file.id}
                    className={`cursor-pointer border-2 p-4 transition-all ${
                      selectedFile?.id === file.id
                        ? 'border-cyan-500 bg-cyan-500/10'
                        : 'border-white/10 bg-slate-800/50 hover:border-purple-500/50 hover:bg-slate-800/70'
                    }`}
                    onClick={() => selectFile(file.id)}
                  >
                    <h4 className="truncate font-semibold text-white">{file.name}</h4>
                    <p className="mt-1 text-xs text-slate-400">
                      {file.duration.toFixed(2)}s • {(file.size / 1024 / 1024).toFixed(2)}MB
                    </p>
                    {file.analyzed && (
                      <div className="mt-2 flex gap-2">
                        <span className="rounded bg-green-500/10 px-2 py-0.5 text-xs text-green-400">
                          Analyzed
                        </span>
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            </div>
          )}
        </TabsContent>

        {/* Analyze Tab */}
        <TabsContent value="analyze" className="space-y-6">
          {selectedFile ? (
            <>
              {/* Waveform Player */}
              <div>
                <h3 className="mb-4 text-lg font-semibold text-white">Audio Player</h3>
                <WaveformPlayer
                  audioUrl={selectedFile.path}
                  title={selectedFile.name}
                  artist="Unknown Artist"
                />
              </div>

              {/* AI Provider Selection */}
              <div>
                <AIProviderSelector selected={aiProvider} onSelect={setAiProvider} />
              </div>

              {/* Analysis Action */}
              <Card className="border-white/10 bg-gradient-to-r from-purple-500/10 via-blue-500/10 to-cyan-500/10 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-white">Ready to Analyze</h3>
                    <p className="text-sm text-slate-400">
                      {selectedFile.analyzed
                        ? 'Re-analyze this file with updated AI models'
                        : 'Start AI-powered analysis of your audio file'}
                    </p>
                  </div>
                  <Button
                    onClick={handleAnalyze}
                    disabled={isAnalyzing}
                    className="bg-gradient-to-r from-purple-500 via-blue-500 to-cyan-500 text-white shadow-lg shadow-purple-500/20 hover:shadow-purple-500/40"
                  >
                    {isAnalyzing ? (
                      <>Analyzing...</>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Start Analysis
                      </>
                    )}
                  </Button>
                </div>
              </Card>
            </>
          ) : (
            <Card className="border-white/10 bg-slate-800/50 p-12">
              <div className="flex flex-col items-center gap-4 text-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-700/50">
                  <UploadIcon className="h-8 w-8 text-slate-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">No file selected</h3>
                  <p className="mt-1 text-sm text-slate-400">
                    Select a file from your library or upload a new one to analyze
                  </p>
                </div>
              </div>
            </Card>
          )}
        </TabsContent>

        {/* Results Tab */}
        <TabsContent value="results" className="space-y-6">
          {selectedFile?.analyzed ? (
            <AnalysisDisplay result={mockAnalysis} isLoading={isAnalyzing} />
          ) : (
            <Card className="border-white/10 bg-slate-800/50 p-12">
              <div className="flex flex-col items-center gap-4 text-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-700/50">
                  <Sparkles className="h-8 w-8 text-slate-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">No analysis yet</h3>
                  <p className="mt-1 text-sm text-slate-400">
                    Analyze your audio file to see detailed AI-powered insights
                  </p>
                </div>
              </div>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
