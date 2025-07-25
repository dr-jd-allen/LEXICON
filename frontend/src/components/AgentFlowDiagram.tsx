import React from 'react';
import { motion } from 'framer-motion';

interface AgentFlowDiagramProps {
  activeAgent: string;
  showCommunication: boolean;
}

const AgentFlowDiagram: React.FC<AgentFlowDiagramProps> = ({ 
  activeAgent, 
  showCommunication 
}) => {
  const agents = [
    { 
      id: 'orchestrator',
      name: 'Claude Opus 4',
      position: { x: 200, y: 50 },
      color: 'from-purple-600 to-indigo-600'
    },
    { 
      id: 'legal',
      name: 'o3-pro',
      position: { x: 100, y: 200 },
      color: 'from-blue-600 to-cyan-600'
    },
    { 
      id: 'scientific',
      name: 'o4-mini',
      position: { x: 300, y: 200 },
      color: 'from-green-600 to-emerald-600'
    },
    { 
      id: 'writer',
      name: 'GPT-4.5',
      position: { x: 150, y: 350 },
      color: 'from-orange-600 to-red-600'
    },
    { 
      id: 'editor',
      name: 'Gemini 2.5',
      position: { x: 250, y: 350 },
      color: 'from-pink-600 to-purple-600'
    }
  ];

  const connections = [
    { from: 'orchestrator', to: 'legal' },
    { from: 'orchestrator', to: 'scientific' },
    { from: 'legal', to: 'scientific', bidirectional: true },
    { from: 'orchestrator', to: 'writer' },
    { from: 'writer', to: 'editor' }
  ];

  return (
    <div className="relative w-full h-96 bg-gray-50 rounded-xl overflow-hidden">
      <svg className="absolute inset-0 w-full h-full">
        {/* Connection lines */}
        {connections.map((conn, idx) => {
          const fromAgent = agents.find(a => a.id === conn.from);
          const toAgent = agents.find(a => a.id === conn.to);
          if (!fromAgent || !toAgent) return null;

          return (
            <g key={idx}>
              <line
                x1={fromAgent.position.x}
                y1={fromAgent.position.y}
                x2={toAgent.position.x}
                y2={toAgent.position.y}
                stroke="#e5e7eb"
                strokeWidth="2"
                strokeDasharray={conn.bidirectional ? "5,5" : ""}
              />
              {showCommunication && (
                <motion.circle
                  r="4"
                  fill="#3b82f6"
                  initial={{ 
                    cx: fromAgent.position.x, 
                    cy: fromAgent.position.y 
                  }}
                  animate={{ 
                    cx: toAgent.position.x, 
                    cy: toAgent.position.y 
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    repeatType: "reverse",
                    ease: "easeInOut"
                  }}
                />
              )}
            </g>
          );
        })}
      </svg>

      {/* Agent nodes */}
      {agents.map((agent) => {
        const isActive = activeAgent.includes(agent.name);
        
        return (
          <motion.div
            key={agent.id}
            className={`absolute w-24 h-24 -translate-x-1/2 -translate-y-1/2`}
            style={{ 
              left: agent.position.x, 
              top: agent.position.y 
            }}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: agents.indexOf(agent) * 0.1 }}
          >
            <div className={`relative w-full h-full ${isActive ? 'animate-pulse' : ''}`}>
              <div className={`absolute inset-0 bg-gradient-to-r ${agent.color} 
                            rounded-full opacity-20 ${isActive ? 'scale-150' : ''} 
                            transition-transform duration-300`} />
              <div className={`relative w-full h-full bg-gradient-to-r ${agent.color} 
                            rounded-full flex items-center justify-center shadow-lg
                            ${isActive ? 'shadow-2xl' : ''}`}>
                <span className="text-white text-xs font-medium text-center px-2">
                  {agent.name}
                </span>
              </div>
              {isActive && (
                <div className="absolute -bottom-6 left-1/2 -translate-x-1/2">
                  <span className="text-xs text-gray-700 bg-white px-2 py-1 
                                 rounded-full shadow whitespace-nowrap">
                    Processing...
                  </span>
                </div>
              )}
            </div>
          </motion.div>
        );
      })}

      {/* Legend */}
      <div className="absolute bottom-4 left-4 text-xs text-gray-600">
        <div className="flex items-center space-x-2 mb-1">
          <div className="w-4 h-0.5 bg-gray-400" />
          <span>Data Flow</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-0.5 bg-gray-400" style={{ borderTop: '2px dashed' }} />
          <span>Bidirectional Communication</span>
        </div>
      </div>
    </div>
  );
};

export default AgentFlowDiagram;