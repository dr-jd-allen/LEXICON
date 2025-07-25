import React, { useState } from 'react';
import { UserIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';

interface ExpertSelectorProps {
  selectedExpert: string;
  onSelectExpert: (expert: string) => void;
  uploadedFiles: Array<{ name: string }>;
}

const ExpertSelector: React.FC<ExpertSelectorProps> = ({ 
  selectedExpert, 
  onSelectExpert,
  uploadedFiles 
}) => {
  const [customExpert, setCustomExpert] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  // Extract potential expert names from uploaded files
  const suggestedExperts = uploadedFiles
    .map(file => {
      const name = file.name.toLowerCase();
      // Look for patterns like "Dr_Name", "Name_MD", "expert_Name"
      const patterns = [
        /dr[._\s]+(\w+)/i,
        /(\w+)[._\s]+(?:md|phd|psyd)/i,
        /expert[._\s]+(\w+)/i,
        /(\w+)[._\s]+report/i,
        /(\w+)[._\s]+deposition/i
      ];
      
      for (const pattern of patterns) {
        const match = name.match(pattern);
        if (match) {
          return match[1].charAt(0).toUpperCase() + match[1].slice(1);
        }
      }
      return null;
    })
    .filter((name): name is string => name !== null)
    .filter((name, index, self) => self.indexOf(name) === index);

  const commonExperts = [
    'Dr. Smith',
    'Dr. Johnson',
    'Dr. Williams',
    'Dr. Brown',
    'Dr. Davis'
  ];

  const allExperts = Array.from(new Set([...suggestedExperts, ...commonExperts]));
  const filteredExperts = allExperts.filter(expert =>
    expert.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Target Expert for Motion
        </label>
        
        {/* Search/Custom Input */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            value={customExpert || selectedExpert}
            onChange={(e) => {
              const value = e.target.value;
              setCustomExpert(value);
              setSearchTerm(value);
              onSelectExpert(value);
            }}
            placeholder="Enter expert name or select from list..."
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg
                     focus:ring-2 focus:ring-lexicon-primary focus:border-transparent
                     transition-all duration-200"
          />
        </div>
      </div>

      {/* Expert Suggestions */}
      {suggestedExperts.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 mb-2">Experts found in uploaded files:</p>
          <div className="flex flex-wrap gap-2">
            {suggestedExperts.map((expert) => (
              <button
                key={expert}
                onClick={() => {
                  onSelectExpert(expert);
                  setCustomExpert('');
                  setSearchTerm('');
                }}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-all
                         ${selectedExpert === expert
                           ? 'bg-lexicon-primary text-white'
                           : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                         }`}
              >
                <UserIcon className="w-4 h-4 inline mr-1" />
                {expert}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Common Expert Names */}
      {searchTerm && filteredExperts.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 mb-2">Select expert:</p>
          <div className="flex flex-wrap gap-2">
            {filteredExperts.map((expert) => (
              <button
                key={expert}
                onClick={() => {
                  onSelectExpert(expert);
                  setCustomExpert('');
                  setSearchTerm('');
                }}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-all
                         ${selectedExpert === expert
                           ? 'bg-lexicon-primary text-white'
                           : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                         }`}
              >
                {expert}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Expert Role Selector */}
      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
        <p className="text-sm font-medium text-blue-900 mb-2">Expert Role:</p>
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="radio"
              name="expertSide"
              value="opposing"
              defaultChecked
              className="text-lexicon-primary focus:ring-lexicon-primary"
            />
            <span className="ml-2 text-sm text-gray-700">
              Opposing Expert (we are challenging)
            </span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="expertSide"
              value="our"
              className="text-lexicon-primary focus:ring-lexicon-primary"
            />
            <span className="ml-2 text-sm text-gray-700">
              Our Expert (we are defending)
            </span>
          </label>
        </div>
      </div>
    </div>
  );
};

export default ExpertSelector;