import React from 'react';
import { motion } from 'framer-motion';
import {
  LightBulbIcon,
  ScaleIcon,
  DocumentTextIcon,
  ShieldCheckIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

interface StrategicRecommendationsProps {
  recommendations: string;
  briefType: string;
}

const StrategicRecommendations: React.FC<StrategicRecommendationsProps> = ({ 
  recommendations, 
  briefType 
}) => {
  // Parse recommendations into sections
  const sections = React.useMemo(() => {
    const parts = recommendations.split(/\d+\.\s+\*\*([^*]+)\*\*/g).filter(Boolean);
    const parsedSections = [];
    
    for (let i = 0; i < parts.length; i += 2) {
      if (parts[i + 1]) {
        parsedSections.push({
          title: parts[i].trim(),
          content: parts[i + 1].trim()
        });
      }
    }
    
    return parsedSections;
  }, [recommendations]);

  const sectionIcons: { [key: string]: any } = {
    'Pre-Trial Strategy': LightBulbIcon,
    'Motion Practice': ScaleIcon,
    'Trial Strategy': DocumentTextIcon,
    'Settlement Considerations': ChartBarIcon,
    'Alternative Approaches': ShieldCheckIcon
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-gray-50 to-blue-50 rounded-2xl shadow-xl p-8"
    >
      <div className="flex items-center mb-6">
        <div className="w-12 h-12 bg-gradient-to-r from-indigo-600 to-purple-600 
                      rounded-xl flex items-center justify-center mr-4">
          <LightBulbIcon className="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Strategic Recommendations
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Tailored strategies for your {briefType}
          </p>
        </div>
      </div>

      <div className="space-y-6">
        {sections.map((section, index) => {
          const Icon = sectionIcons[section.title] || DocumentTextIcon;
          
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg 
                       transition-shadow duration-300"
            >
              <div className="flex items-start">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-500 
                              rounded-lg flex items-center justify-center flex-shrink-0 mr-4">
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">
                    {section.title}
                  </h3>
                  <div className="text-gray-700 space-y-2 recommendations-content">
                    {section.content.split('\n').map((line, idx) => (
                      <p key={idx} className="leading-relaxed">
                        {line.trim()}
                      </p>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="mt-8 p-4 bg-indigo-100 rounded-lg">
        <p className="text-sm text-indigo-800 flex items-center">
          <ShieldCheckIcon className="w-5 h-5 mr-2" />
          These recommendations are based on comprehensive analysis of legal precedents, 
          scientific literature, and case-specific factors.
        </p>
      </div>
    </motion.div>
  );
};

export default StrategicRecommendations;