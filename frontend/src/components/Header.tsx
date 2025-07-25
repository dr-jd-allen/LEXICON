import React from 'react';
import { ScaleIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';

const Header: React.FC = () => {
  return (
    <header className="bg-gradient-to-r from-gray-900 via-indigo-900 to-purple-900 shadow-2xl relative overflow-hidden">
      {/* Animated background effect */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 animate-pulse" />
      </div>
      
      <div className="container mx-auto px-4 py-6 max-w-7xl relative z-10">
        <div className="flex items-center justify-between">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center space-x-4"
          >
            <div className="relative">
              <ScaleIcon className="w-12 h-12 text-white" />
              <SparklesIcon className="w-5 h-5 text-yellow-400 absolute -top-1 -right-1 animate-pulse" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-white tracking-tight">LEXICON</h1>
              <p className="text-sm text-gray-300">AI-Powered Legal Brief Generation</p>
            </div>
          </motion.div>
          
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-right"
          >
            <div className="flex items-center space-x-4">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
              </div>
              <div>
                <p className="text-sm text-gray-300">5-Agent Architecture</p>
                <p className="text-xs text-gray-400">Allen Law Group Edition</p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </header>
  );
};

export default Header;