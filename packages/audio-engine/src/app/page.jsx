'use client';
import { useState, useRef } from 'react';
import { Brain as BrainIcon, Settings as SettingsIcon, User as UserIcon } from 'lucide-react';
import { useAudioRecorder } from '../hooks/useAudioRecorder';
export default function Home() {
    const [isPlaying, setIsPlaying] = useState(false);
    const [volume, setVolume] = useState(80);
    const [isMuted, setIsMuted] = useState(false);
    const [activeTab, setActiveTab] = useState('home');
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const audioRef = useRef(null);
    const { isRecording, audioBlob, audioUrl, startRecording, stopRecording, error, audioData, } = useAudioRecorder();
    const togglePlay = () => {
        if (audioRef.current) {
            if (isPlaying) {
                audioRef.current.pause();
            }
            else {
                audioRef.current.play().catch(err => {
                    console.error('Error playing audio:', err);
                });
            }
            setIsPlaying(!isPlaying);
        }
    };
    const toggleMute = () => {
        if (audioRef.current) {
            audioRef.current.muted = !isMuted;
            setIsMuted(!isMuted);
        }
    };
    const handleRecord = async () => {
        if (isRecording) {
            await stopRecording();
        }
        else {
            await startRecording();
        }
    };
    const handleTimeUpdate = () => {
        if (audioRef.current) {
            setCurrentTime(audioRef.current.currentTime);
            if (!isNaN(audioRef.current.duration)) {
                setDuration(audioRef.current.duration);
            }
        }
    };
    const handleSeek = (e) => {
        const target = e.target;
        const newTime = parseFloat(target.value);
        setCurrentTime(newTime);
        if (audioRef.current) {
            audioRef.current.currentTime = newTime;
        }
    };
    const handleVolumeChange = (e) => {
        const target = e.target;
        const newVolume = parseFloat(target.value);
        setVolume(newVolume);
        if (audioRef.current) {
            audioRef.current.volume = newVolume / 100;
            setIsMuted(newVolume === 0);
        }
    };
    const formatTime = (time) => {
        const minutes = Math.floor(time / 60);
        const seconds = Math.floor(time % 60);
        return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    };
    return (<main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
      {/* Navigation */}
      <nav className="border-b border-gray-800 backdrop-blur-sm bg-gray-900/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <div className="flex items-center">
                <BrainIcon className="h-8 w-8 text-cyan-400"/>
                <span className="ml-2 text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                  SampleMind AI
                </span>
              </div>
              <div className="hidden md:flex space-x-1">
                {['home', 'studio', 'library', 'templates'].map((tab) => (<button key={tab} onClick={() => setActiveTab(tab)} className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${activeTab === tab
                ? 'bg-gray-800 text-cyan-400'
                : 'text-gray-300 hover:bg-gray-800 hover:text-white'}`}>
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </button>))}
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button className="p-2 rounded-full hover:bg-gray-800 transition-colors">
                <SettingsIcon className="h-5 w-5 text-gray-400"/>
              </button>
              <button className="p-2 rounded-full hover:bg-gray-800 transition-colors">
                <UserIcon className="h-5 w-5 text-gray-400"/>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 bg-clip-text text-transparent">
            Create Music with AI
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Transform your musical ideas into professional tracks with the power of artificial intelligence.
          </p>
          
          <div className="flex flex-col sm:flex-row justify-center gap-6 mb-16">
            <button onClick={handleRecord} disabled={isPlaying} className={`px-8 py-4 rounded-xl font-medium flex items-center justify-center space-x-2 transition-opacity ${isRecording
            ? 'bg-red-600 hover:bg-red-700 text-white'
            : 'bg-cyan-500 hover:bg-cyan-600 text-white'}`}>
              {isRecording ? (<>
                  <div className="h-4 w-4 bg-white rounded-full animate-pulse"/>
                  <span>Stop Recording</span>
                </>) : (<>
                  <Mic className="h-5 w-5"/>
                  <span>Start Recording</span>
                </>)}
            </button>
            
            <button className="px-8 py-4 border-2 border-cyan-500 text-cyan-400 rounded-xl font-medium flex items-center justify-center space-x-2 hover:bg-cyan-500/10 transition-colors" disabled={!audioBlob}>
              <Upload className="h-5 w-5"/>
              <span>Upload Sample</span>
            </button>
          </div>

          {/* Audio Visualization */}
          <div className="h-40 w-full bg-gray-800/50 rounded-xl p-6 mb-12">
            <div className="flex items-end justify-center h-full space-x-1">
              {audioData.length > 0 ? (Array.from(audioData).map((value, index) => (<div key={index} className="w-1.5 bg-gradient-to-t from-cyan-400 to-blue-500 rounded-full transition-all duration-75" style={{ height: `${value / 2}%` }}/>))) : (<div className="text-gray-500 text-lg">Start recording to see visualization</div>)}
            </div>
          </div>

          {/* Audio Player */}
          {audioUrl && (<div className="max-w-2xl mx-auto bg-gray-800/50 rounded-xl p-6 mb-12">
              <audio ref={audioRef} src={audioUrl} onTimeUpdate={handleTimeUpdate} onLoadedMetadata={() => {
                if (audioRef.current) {
                    setDuration(audioRef.current.duration);
                }
            }} onEnded={() => setIsPlaying(false)} hidden/>
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-gray-400">{formatTime(currentTime)}</span>
                <div className="flex-1 mx-4">
                  <input type="range" min="0" max={duration || 0} value={currentTime} onChange={handleSeek} className="w-full h-1 bg-gray-700 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-cyan-500"/>
                </div>
                <span className="text-sm text-gray-400">
                  {formatTime(duration)}
                </span>
              </div>
              <div className="flex items-center justify-center space-x-6">
                <button onClick={togglePlay} className="p-3 bg-cyan-500 rounded-full hover:bg-cyan-600 transition-colors">
                  {isPlaying ? (<Pause className="h-6 w-6 text-white"/>) : (<Play className="h-6 w-6 text-white"/>)}
                </button>
                <div className="flex items-center space-x-2">
                  <button onClick={toggleMute} className="text-gray-400 hover:text-white">
                    {isMuted ? <VolumeX className="h-5 w-5"/> : <Volume2 className="h-5 w-5"/>}
                  </button>
                  <input type="range" min="0" max="100" value={isMuted ? 0 : volume} onChange={(e) => {
                const newVolume = parseInt(e.target.value);
                setVolume(newVolume);
                if (audioRef.current) {
                    audioRef.current.volume = newVolume / 100;
                    if (newVolume === 0) {
                        setIsMuted(true);
                    }
                    else {
                        setIsMuted(false);
                    }
                }
            }} className="w-24 accent-cyan-500"/>
                </div>
              </div>
            </div>)}

          {error && (<div className="text-red-500 mb-6">
              {error}
            </div>)}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
          <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700 hover:border-cyan-500/50 transition-colors group">
            <div className="bg-cyan-500/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4 group-hover:bg-cyan-500/20 transition-colors">
              <Music className="h-6 w-6 text-cyan-400"/>
            </div>
            <h3 className="text-lg font-semibold mb-2">AI-Powered Composition</h3>
            <p className="text-gray-400">Generate original music using advanced neural networks.</p>
          </div>
          
          <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700 hover:border-blue-500/50 transition-colors group">
            <div className="bg-blue-500/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4 group-hover:bg-blue-500/20 transition-colors">
              <Settings className="h-6 w-6 text-blue-400"/>
            </div>
            <h3 className="text-lg font-semibold mb-2">Smart Sound Design</h3>
            <p className="text-gray-400">Transform sounds with intelligent audio processing.</p>
          </div>
          
          <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700 hover:border-purple-500/50 transition-colors group">
            <div className="bg-purple-500/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4 group-hover:bg-purple-500/20 transition-colors">
              <Brain className="h-6 w-6 text-purple-400"/>
            </div>
            <h3 className="text-lg font-semibold mb-2">Neural Mixing</h3>
            <p className="text-gray-400">Get professional-sounding mixes with AI assistance.</p>
          </div>
        </div>
      </div>

      <footer className="border-t border-gray-800 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-400 text-sm">
            &copy; {new Date().getFullYear()} SampleMind AI. All rights reserved.
          </p>
        </div>
      </footer>
    </main>);
}
//# sourceMappingURL=page.jsx.map