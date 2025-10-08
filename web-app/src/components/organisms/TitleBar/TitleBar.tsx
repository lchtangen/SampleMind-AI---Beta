import React from 'react';
import { motion } from 'framer-motion';

export const TitleBar: React.FC = () => {
  const handleMinimize = () => {
    window.electron.send('minimize-window');
  };

  const handleMaximize = () => {
    window.electron.send('maximize-window');
  };

  const handleClose = () => {
    window.electron.send('close-window');
  };

  return (
    <motion.div
      className="fixed top-0 left-0 right-0 h-10 bg-black bg-opacity-20 backdrop-blur-md border-b border-white border-opacity-10 flex items-center justify-between px-4 z-50"
      style={{ WebkitAppRegion: 'drag' }}
    >
      <div className="flex items-center gap-2">
        <div className="w-3 h-3 rounded-full bg-red-500" onClick={handleClose} />
        <div className="w-3 h-3 rounded-full bg-yellow-500" onClick={handleMinimize} />
        <div className="w-3 h-3 rounded-full bg-green-500" onClick={handleMaximize} />
      </div>
      <div className="text-sm font-semibold text-white">SampleMind AI</div>
    </motion.div>
  );
};
