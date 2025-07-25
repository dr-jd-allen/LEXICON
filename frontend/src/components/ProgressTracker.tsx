import React from 'react';
import { motion } from 'framer-motion';
import { 
  CpuChipIcon, 
  MagnifyingGlassIcon, 
  BeakerIcon,
  PencilSquareIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { BriefGenerationStatus } from '../types';
import AgentFlowDiagram from './AgentFlowDiagram';

interface ProgressTrackerProps {
  status: BriefGenerationStatus;
}

const agentInfo = {
  'Claude Opus 4': { 
    icon: CpuChipIcon, 
    color: 'from-purple-600 to-indigo-600',
    description: 'Orchestrator - Case Analysis & Coordination',
    capabilities: ['Document Anonymization', 'Case Summary Generation', 'Agent Coordination']
  },
  'o3-pro-deep-research': { 
    icon: MagnifyingGlassIcon, 
    color: 'from-blue-600 to-cyan-600',
    description: 'Legal Research - Precedent & Case Law Analysis',
    capabilities: ['Google Scholar Case Law', 'CourtWhisperer', 'Internal Corpus Search']
  },
  'o4-mini-deep-research': { 
    icon: BeakerIcon, 
    color: 'from-green-600 to-emerald-600',
    description: 'Scientific Research - Medical Literature Analysis',
    capabilities: ['PubMed Search', 'Domain Knowledge Storage', 'Peer Review Validation']
  },
  'gpt-4.5-research-preview': { 
    icon: PencilSquareIcon, 
    color: 'from-orange-600 to-red-600',
    description: 'Brief Writer - Legal Strategy & Drafting',
    capabilities: ['Research Synthesis', 'Strategy Selection', 'Persuasive Writing']
  },
  'Gemini 2.5 Pro': { 
    icon: CheckCircleIcon, 
    color: 'from-pink-600 to-purple-600',
    description: 'Editor - Fact-Checking & MLA Formatting',
    capabilities: ['Google Search Grounding', 'Citation Verification', 'MLA 9th Edition']
  }
};

const stages = [
  { name: 'Document Upload', agent: 'System' },
  { name: 'Anonymization & Analysis', agent: 'Claude Opus 4' },
  { name: 'Legal Research', agent: 'o3-pro-deep-research' },
  { name: 'Scientific Research', agent: 'o4-mini-deep-research' },
  { name: 'Brief Writing', agent: 'gpt-4.5-research-preview' },
  { name: 'Final Review & Polish', agent: 'Gemini 2.5 Pro' }
];

const ProgressTracker: React.FC<ProgressTrackerProps> = ({ status }) => {
  const currentStageIndex = stages.findIndex(s => 
    s.name.toLowerCase().includes(status.stage.toLowerCase())
  );

  const showCommunication = status.stage === 'legal_research' || status.stage === 'scientific_research';

  return (
    <div className="space-y-8">
      {/* Agent Flow Diagram */}
      <div className="bg-white rounded-2xl shadow-xl p-8">
        <h3 className="text-xl font-bold text-gray-900 mb-4">
          AI Agent Orchestration
        </h3>
        <AgentFlowDiagram 
          activeAgent={status.currentAgent} 
          showCommunication={showCommunication}
        />
      </div>

      {/* Progress Details */}
      <div className="bg-white rounded-2xl shadow-xl p-8">
        <h2 className="text-2xl font-bold text-lexicon-dark mb-8">
          Generating Your Brief
        </h2>

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Progress</span>
          <span>{status.progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-lexicon-primary to-lexicon-accent"
            initial={{ width: 0 }}
            animate={{ width: `${status.progress}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>

      {/* Agent Progress */}
      <div className="space-y-4">
        {stages.map((stage, index) => {
          const agent = agentInfo[stage.agent as keyof typeof agentInfo];
          const Icon = agent?.icon || CpuChipIcon;
          const isActive = index === currentStageIndex;
          const isCompleted = index < currentStageIndex;
          
          return (
            <motion.div
              key={stage.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`flex items-center space-x-4 p-4 rounded-lg transition-all
                        ${isActive ? 'bg-blue-50 border-2 border-lexicon-primary' : 
                          isCompleted ? 'bg-green-50' : 'bg-gray-50'}`}
            >
              <div className={`relative ${isActive ? 'animate-pulse' : ''}`}>
                <div className={`w-12 h-12 rounded-full bg-gradient-to-r ${
                  agent?.color || 'from-gray-400 to-gray-500'
                } flex items-center justify-center`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                {isCompleted && (
                  <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-green-500 
                                rounded-full flex items-center justify-center">
                    <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </div>
              
              <div className="flex-1">
                <h3 className={`font-semibold ${
                  isActive ? 'text-lexicon-primary' : 
                  isCompleted ? 'text-green-700' : 'text-gray-600'
                }`}>
                  {stage.name}
                </h3>
                {agent && (
                  <>
                    <p className="text-sm text-gray-500">
                      {agent.description}
                    </p>
                    {isActive && agent.capabilities && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {agent.capabilities.map((cap, idx) => (
                          <span key={idx} className="text-xs px-2 py-1 bg-blue-100 
                                                   text-blue-700 rounded-full">
                            {cap}
                          </span>
                        ))}
                      </div>
                    )}
                  </>
                )}
                {isActive && status.message && (
                  <p className="text-sm text-lexicon-primary mt-2 italic animate-pulse">
                    {status.message}
                  </p>
                )}
              </div>
              
              {isActive && (
                <div className="flex space-x-1">
                  <span className="w-2 h-2 bg-lexicon-primary rounded-full animate-bounce" 
                        style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-lexicon-primary rounded-full animate-bounce" 
                        style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-lexicon-primary rounded-full animate-bounce" 
                        style={{ animationDelay: '300ms' }} />
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Real-time Message */}
      {status.message && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-800">
            <span className="font-semibold">{status.currentAgent}:</span> {status.message}
          </p>
        </div>
      )}
      </div>
    </div>
  );
};

export default ProgressTracker;