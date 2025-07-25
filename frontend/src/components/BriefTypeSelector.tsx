import React from 'react';
import { motion } from 'framer-motion';
import { 
  ShieldCheckIcon, 
  ShieldExclamationIcon, 
  DocumentTextIcon,
  BeakerIcon,
  BuildingLibraryIcon
} from '@heroicons/react/24/outline';
import { BriefType } from '../types';

interface BriefTypeSelectorProps {
  selectedType: BriefType | null;
  onSelectType: (type: BriefType) => void;
  jurisdiction: string;
  onJurisdictionChange: (jurisdiction: string) => void;
}

const briefTypes = [
  {
    id: 'daubert_motion' as BriefType,
    title: 'Daubert Motion',
    description: 'Challenge opposing expert testimony under Federal Rule 702',
    icon: ShieldExclamationIcon,
    color: 'from-red-500 to-orange-500'
  },
  {
    id: 'daubert_response' as BriefType,
    title: 'Response to Daubert',
    description: 'Defend expert testimony against Daubert challenges',
    icon: ShieldCheckIcon,
    color: 'from-green-500 to-emerald-500'
  },
  {
    id: 'frye_motion' as BriefType,
    title: 'Frye Motion',
    description: 'Challenge expert testimony under Frye standard (IL)',
    icon: BeakerIcon,
    color: 'from-purple-500 to-pink-500'
  },
  {
    id: 'frye_response' as BriefType,
    title: 'Response to Frye',
    description: 'Defend expert testimony against Frye challenges',
    icon: DocumentTextIcon,
    color: 'from-blue-500 to-cyan-500'
  },
  {
    id: 'motion_in_limine' as BriefType,
    title: 'Motion in Limine',
    description: 'Exclude evidence or testimony from trial',
    icon: BuildingLibraryIcon,
    color: 'from-indigo-500 to-purple-500'
  }
];

const jurisdictions = ['Federal', 'Illinois', 'Indiana', 'Wisconsin', 'Michigan'];

const BriefTypeSelector: React.FC<BriefTypeSelectorProps> = ({
  selectedType,
  onSelectType,
  jurisdiction,
  onJurisdictionChange
}) => {
  return (
    <div className="space-y-6">
      {/* Jurisdiction Selector */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Jurisdiction
        </label>
        <select
          value={jurisdiction}
          onChange={(e) => onJurisdictionChange(e.target.value)}
          className="w-full md:w-64 px-4 py-2 border border-gray-300 rounded-lg 
                   focus:ring-2 focus:ring-lexicon-primary focus:border-transparent
                   transition-all duration-200"
        >
          {jurisdictions.map(j => (
            <option key={j} value={j}>{j}</option>
          ))}
        </select>
      </div>

      {/* Brief Type Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {briefTypes.map((type) => {
          const Icon = type.icon;
          const isSelected = selectedType === type.id;
          
          return (
            <motion.div
              key={type.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <button
                onClick={() => onSelectType(type.id)}
                className={`relative w-full p-6 rounded-xl border-2 transition-all duration-300
                          ${isSelected 
                            ? 'border-lexicon-accent shadow-lg scale-105' 
                            : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
                          }`}
              >
                {isSelected && (
                  <div className="absolute top-3 right-3">
                    <div className="w-6 h-6 bg-lexicon-accent rounded-full flex items-center justify-center">
                      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  </div>
                )}
                
                <div className={`w-16 h-16 rounded-full bg-gradient-to-r ${type.color} 
                              flex items-center justify-center mb-4 mx-auto`}>
                  <Icon className="w-8 h-8 text-white" />
                </div>
                
                <h3 className="text-lg font-bold text-lexicon-dark mb-2">
                  {type.title}
                </h3>
                <p className="text-sm text-gray-600">
                  {type.description}
                </p>
              </button>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default BriefTypeSelector;