import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Icons } from '@/components/icons';
import { motion } from 'framer-motion';
import Link from 'next/link';

// Animation variants
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { 
    opacity: 1, 
    y: 0,
    transition: {
      duration: 0.5,
      ease: "easeOut"
    }
  }
};

export default function Home() {
  const features = [
    {
      icon: <Icons.music className="h-8 w-8" />,
      title: 'Quantum Audio Synthesis',
      description: 'Generate never-before-heard sounds using quantum-inspired algorithms that push the boundaries of digital audio.'
    },
    {
      icon: <Icons.waveform className="h-8 w-8" />,
      title: 'Neural Sample Engine',
      description: 'AI-powered sample manipulation that understands musical context and adapts to your style in real-time.'
    },
    {
      icon: <Icons.brain className="h-8 w-8" />,
      title: 'Cognitive Mixing',
      description: 'Let our AI analyze and enhance your mix with intelligent processing that learns from professional tracks.'
    },
    {
      icon: <Icons.collaborate className="h-8 w-8" />,
      title: 'Holographic Collaboration',
      description: 'Work with artists worldwide in our immersive 3D audio workspace with real-time synchronization.'
    },
    {
      icon: <Icons.music className="h-8 w-8" />,
      title: 'Generative Compositions',
      description: 'Create endless variations of your ideas with AI that understands music theory and your personal style.'
    },
    {
      icon: <Icons.waveform className="h-8 w-8" />,
      title: 'Spatial Audio Design',
      description: 'Design for next-gen audio formats with intuitive 3D sound positioning and movement.'
    }
  ];

  return (
    <div className="flex flex-col min-h-screen overflow-hidden">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute inset-0 bg-grid-pattern opacity-5" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,#4f46e5_0%,transparent_70%)] opacity-20 mix-blend-overlay" />
        
        {/* Animated particles */}
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full bg-gradient-to-r from-neon-cyan to-neon-pink"
            style={{
              width: Math.random() * 10 + 5,
              height: Math.random() * 10 + 5,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              filter: 'blur(1px)',
              opacity: 0.6
            }}
            animate={{
              y: [0, -50, 0],
              x: [0, (Math.random() - 0.5) * 100],
              opacity: [0.3, 0.8, 0.3],
            }}
            transition={{
              duration: 5 + Math.random() * 10,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        ))}
      </div>

      {/* Hero Section */}
      <section className="relative w-full min-h-screen flex items-center justify-center overflow-hidden pt-20">
        <div className="absolute inset-0 bg-gradient-to-b from-black/80 via-black/50 to-transparent z-0" />
        
        <div className="container px-4 md:px-6 relative z-10">
          <motion.div 
            className="grid gap-12 lg:grid-cols-2 lg:gap-24 items-center"
            initial="hidden"
            animate="show"
            variants={container}
          >
            <motion.div className="space-y-6" variants={item}>
              <motion.div className="inline-block px-3 py-1 text-sm font-medium bg-neon-pink/20 text-neon-pink rounded-full mb-4">
                BETA NOW LIVE
              </motion.div>
              
              <motion.h1 
                className="text-5xl md:text-7xl lg:text-8xl font-bold leading-tight"
                variants={item}
              >
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-neon-cyan via-neon-pink to-neon-purple">
                  SampleMind
                </span>
                <span className="block mt-2 text-3xl md:text-5xl text-white/80">
                  The Future of Music Production
                </span>
              </motion.h1>
              
              <motion.p 
                className="text-xl md:text-2xl text-white/70 max-w-2xl"
                variants={item}
              >
                Harness the power of quantum computing and neural networks to create music that transcends boundaries.
              </motion.p>
              
              <motion.div 
                className="flex flex-col sm:flex-row gap-4 pt-4"
                variants={item}
              >
                <Button 
                  size="lg" 
                  className="glass-effect group relative overflow-hidden px-8 py-6 text-lg font-bold"
                >
                  <span className="relative z-10 flex items-center">
                    <Icons.play className="mr-2 h-5 w-5" />
                    Start Creating Free
                  </span>
                  <span className="absolute inset-0 bg-gradient-to-r from-neon-pink to-neon-purple opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </Button>
                
                <Button 
                  variant="outline" 
                  size="lg" 
                  className="glass-effect border-neon-cyan/30 text-neon-cyan hover:bg-neon-cyan/10 hover:text-neon-cyan px-8 py-6 text-lg font-bold"
                >
                  <span className="flex items-center">
                    <Icons.arrowRight className="mr-2 h-5 w-5" />
                    Watch Demo
                  </span>
                </Button>
              </motion.div>
              
              <motion.div 
                className="pt-4 flex items-center space-x-4 text-sm text-white/60"
                variants={item}
              >
                <div className="flex -space-x-2">
                  {[1, 2, 3].map((i) => (
                    <div 
                      key={i}
                      className="h-8 w-8 rounded-full border-2 border-background bg-gradient-to-r from-neon-cyan to-neon-pink"
                      style={{ zIndex: 3 - i }}
                    />
                  ))}
                </div>
                <div>
                  <div className="font-medium text-white/90">Join 10,000+ producers</div>
                  <div className="text-xs">Already creating with SampleMind</div>
                </div>
              </motion.div>
            </motion.div>
            
            <motion.div 
              className="relative"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2, duration: 0.8 }}
            >
              <div className="relative z-10 aspect-square w-full max-w-2xl mx-auto">
                <div className="absolute inset-0 bg-gradient-to-br from-neon-pink/20 via-neon-purple/20 to-neon-cyan/20 rounded-3xl blur-xl opacity-70" />
                <div className="relative z-20 h-full w-full rounded-2xl glass-effect border border-white/10 overflow-hidden">
                  {/* Placeholder for DAW interface */}
                  <div className="h-full w-full bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center">
                    <div className="text-center p-8">
                      <Icons.logo className="h-20 w-20 mx-auto mb-4 text-neon-cyan" />
                      <h3 className="text-xl font-bold text-white mb-2">SampleMind DAW</h3>
                      <p className="text-white/60">Your next hit starts here</p>
                    </div>
                  </div>
                </div>
                
                {/* Floating elements */}
                <motion.div 
                  className="absolute -bottom-6 -left-6 h-32 w-32 rounded-full bg-neon-pink/20 blur-xl"
                  animate={{
                    y: [0, -20, 0],
                  }}
                  transition={{
                    duration: 6,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                />
                <motion.div 
                  className="absolute -top-6 -right-6 h-40 w-40 rounded-full bg-neon-cyan/20 blur-xl"
                  animate={{
                    y: [0, 20, 0],
                  }}
                  transition={{
                    duration: 8,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: 1
                  }}
                />
              </div>
            </motion.div>
          </motion.div>
        </div>
        
        {/* Scroll indicator */}
        <motion.div 
          className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center"
          animate={{
            y: [0, 10, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          <div className="h-8 w-0.5 bg-gradient-to-b from-neon-cyan to-transparent" />
          <span className="mt-2 text-sm text-neon-cyan/80">Scroll to explore</span>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="relative py-24 md:py-32 overflow-hidden">
        <div className="container px-4 md:px-6 relative z-10">
          <motion.div 
            className="text-center max-w-4xl mx-auto mb-20"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <span className="inline-block px-3 py-1 text-sm font-medium bg-neon-cyan/20 text-neon-cyan rounded-full mb-4">
              POWERFUL FEATURES
            </span>
            <h2 className="text-4xl md:text-6xl font-bold mb-6">
              Next-Gen Music Production
            </h2>
            <p className="text-xl text-white/70 max-w-2xl mx-auto">
              Experience the future of music creation with our cutting-edge AI-powered tools and workflows.
            </p>
          </motion.div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ delay: index * 0.1, duration: 0.5 }}
              >
                <Card className="glass-effect border-white/5 hover:border-neon-cyan/30 transition-all duration-300 h-full">
                  <CardHeader className="pb-3">
                    <div className="flex items-center space-x-4">
                      <div className="p-2 rounded-lg bg-neon-cyan/10 text-neon-cyan">
                        {feature.icon}
                      </div>
                      <CardTitle className="text-xl">{feature.title}</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-white/70">{feature.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
        
        {/* Background elements */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/30 to-transparent" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,#4f46e5_0%,transparent_50%)] opacity-20" />
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-24 md:py-32 overflow-hidden">
        <div className="container px-4 md:px-6 relative z-10">
          <motion.div 
            className="max-w-4xl mx-auto text-center"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-4xl md:text-6xl font-bold mb-6">
              Ready to Revolutionize Your Music?
            </h2>
            <p className="text-xl text-white/70 mb-10 max-w-2xl mx-auto">
              Join the future of music production today. No credit card required.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                size="lg" 
                className="glass-effect group relative overflow-hidden px-8 py-6 text-lg font-bold"
              >
                <span className="relative z-10 flex items-center">
                  Start Free Trial
                </span>
                <span className="absolute inset-0 bg-gradient-to-r from-neon-pink to-neon-purple opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </Button>
              <Button 
                variant="outline" 
                size="lg" 
                className="glass-effect border-neon-cyan/30 text-neon-cyan hover:bg-neon-cyan/10 hover:text-neon-cyan px-8 py-6 text-lg font-bold"
              >
                <span className="flex items-center">
                  Schedule Demo
                </span>
              </Button>
            </div>
            <p className="mt-6 text-sm text-white/50">
              14-day free trial • No credit card required • Cancel anytime
            </p>
          </motion.div>
        </div>
        
        {/* Animated background */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/80" />
          <div className="absolute inset-0 bg-[url('/images/grid.svg')] opacity-5" />
          
          {[...Array(15)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute rounded-full"
              style={{
                width: Math.random() * 400 + 100,
                height: Math.random() * 400 + 100,
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                background: `radial-gradient(circle, ${
                  Math.random() > 0.5 ? 'var(--neon-pink)' : 'var(--neon-cyan)'
                }10 0%, transparent 70%)`,
                filter: 'blur(20px)'
              }}
              animate={{
                x: [0, (Math.random() - 0.5) * 100],
                y: [0, (Math.random() - 0.5) * 50],
                opacity: [0.1, 0.3, 0.1],
              }}
              transition={{
                duration: 10 + Math.random() * 20,
                repeat: Infinity,
                repeatType: 'reverse',
                ease: 'easeInOut'
              }}
            />
          ))}
        </div>
      </section>
    </div>
  );
}
