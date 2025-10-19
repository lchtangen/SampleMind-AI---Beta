import { Brain, Music, Mic, Headphones } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 text-white">
      <main className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <div className="flex justify-center mb-8">
            <div className="p-4 rounded-full bg-white/10 backdrop-blur-sm">
              <Brain className="w-12 h-12 text-purple-400" />
            </div>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-purple-300 via-pink-300 to-blue-300">
            SampleMind AI
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-3xl mx-auto">
            Revolutionizing music production with AI-powered audio processing and quantum-inspired algorithms
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
            <div className="p-6 bg-white/5 rounded-xl backdrop-blur-sm border border-white/10">
              <Music className="w-8 h-8 text-purple-400 mb-4 mx-auto" />
              <h3 className="text-xl font-semibold mb-2">Neural Audio Engine</h3>
              <p className="text-gray-400">Experience next-generation audio processing powered by deep learning</p>
            </div>
            
            <div className="p-6 bg-white/5 rounded-xl backdrop-blur-sm border border-white/10">
              <Mic className="w-8 h-8 text-purple-400 mb-4 mx-auto" />
              <h3 className="text-xl font-semibold mb-2">AI-Assisted Tools</h3>
              <p className="text-gray-400">Enhance your workflow with intelligent music production assistance</p>
            </div>
            
            <div className="p-6 bg-white/5 rounded-xl backdrop-blur-sm border border-white/10">
              <Headphones className="w-8 h-8 text-purple-400 mb-4 mx-auto" />
              <h3 className="text-xl font-semibold mb-2">Immersive Experience</h3>
              <p className="text-gray-400">Multi-dimensional audio visualization for an unparalleled creative experience</p>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/login"
              className="px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full font-medium text-lg hover:opacity-90 transition-opacity"
            >
              Get Started
            </a>
            <a
              href="/demo"
              className="px-8 py-4 bg-white/10 rounded-full font-medium text-lg hover:bg-white/20 transition-colors"
            >
              Try Demo
            </a>
          </div>
        </div>
      </main>
      <footer className="py-8 text-center text-gray-400 text-sm">
        <p>© {new Date().getFullYear()} SampleMind AI. All rights reserved.</p>
      </footer>
    </div>
  );
}
