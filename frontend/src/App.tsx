import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import FileUpload from './components/FileUpload';
import BriefTypeSelector from './components/BriefTypeSelector';
import ExpertSelector from './components/ExpertSelector';
import ProgressTracker from './components/ProgressTracker';
import GeneratedBrief from './components/GeneratedBrief';
import StrategicRecommendations from './components/StrategicRecommendations';
import Header from './components/Header';
import { BriefType, UploadedFile, BriefGenerationStatus, GenerateBriefResponse } from './types';
import { generateBrief, simulateGenerateBrief } from './services/api';
import './App.css';

function App() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [selectedBriefType, setSelectedBriefType] = useState<BriefType | null>(null);
  const [selectedExpert, setSelectedExpert] = useState<string>('');
  const [jurisdiction, setJurisdiction] = useState<string>('Federal');
  const [generationStatus, setGenerationStatus] = useState<BriefGenerationStatus | null>(null);
  const [generatedBrief, setGeneratedBrief] = useState<string | null>(null);
  const [strategicRecommendations, setStrategicRecommendations] = useState<string | null>(null);
  const [briefMetadata, setBriefMetadata] = useState<GenerateBriefResponse['metadata'] | null>(null);

  const handleFilesUpload = (files: UploadedFile[]) => {
    setUploadedFiles(prev => [...prev, ...files]);
  };

  const handleRemoveFile = (id: string) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== id));
  };

  const handleGenerateBrief = async () => {
    if (!selectedBriefType || uploadedFiles.length === 0 || !selectedExpert) return;

    setGenerationStatus({
      stage: 'uploading',
      progress: 0,
      currentAgent: 'System',
      message: 'Uploading case files...'
    });

    try {
      // Use real API now that backend will be running
      const result = await generateBrief({
        briefType: selectedBriefType,
        files: uploadedFiles,
        expertName: selectedExpert,
        jurisdiction,
        onProgress: (status) => setGenerationStatus(status)
      });

      setGeneratedBrief(result.brief);
      setStrategicRecommendations(result.strategicRecommendations);
      setBriefMetadata(result.metadata);
      setGenerationStatus({
        stage: 'completed',
        progress: 100,
        currentAgent: 'System',
        message: 'Brief generation complete!'
      });
    } catch (error) {
      setGenerationStatus({
        stage: 'error',
        progress: 0,
        currentAgent: 'System',
        message: 'Error generating brief. Please try again.'
      });
    }
  };

  const handleReset = () => {
    setUploadedFiles([]);
    setSelectedBriefType(null);
    setGenerationStatus(null);
    setGeneratedBrief(null);
    setStrategicRecommendations(null);
    setBriefMetadata(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-lexicon-light to-gray-100">
      <Toaster position="top-right" />
      <Header />
      
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {!generationStatus ? (
          <div className="space-y-8 animate-fade-in">
            {/* File Upload Section */}
            <section className="bg-white rounded-2xl shadow-xl p-8">
              <h2 className="text-2xl font-bold text-lexicon-dark mb-6">
                Upload Case Documents
              </h2>
              <FileUpload 
                onFilesUpload={handleFilesUpload}
                uploadedFiles={uploadedFiles}
                onRemoveFile={handleRemoveFile}
              />
            </section>

            {/* Brief Type Selection */}
            {uploadedFiles.length > 0 && (
              <section className="bg-white rounded-2xl shadow-xl p-8 animate-slide-up">
                <h2 className="text-2xl font-bold text-lexicon-dark mb-6">
                  Select Brief Type
                </h2>
                <BriefTypeSelector
                  selectedType={selectedBriefType}
                  onSelectType={setSelectedBriefType}
                  jurisdiction={jurisdiction}
                  onJurisdictionChange={setJurisdiction}
                />
              </section>
            )}

            {/* Expert Selection */}
            {uploadedFiles.length > 0 && selectedBriefType && (
              <section className="bg-white rounded-2xl shadow-xl p-8 animate-slide-up">
                <h2 className="text-2xl font-bold text-lexicon-dark mb-6">
                  Identify Target Expert
                </h2>
                <ExpertSelector
                  selectedExpert={selectedExpert}
                  onSelectExpert={setSelectedExpert}
                  uploadedFiles={uploadedFiles}
                />
                
                {selectedExpert && (
                  <div className="mt-8 flex justify-center">
                    <button
                      onClick={handleGenerateBrief}
                      className="px-8 py-4 bg-gradient-to-r from-lexicon-primary to-lexicon-secondary 
                               text-white font-semibold rounded-lg shadow-lg hover:shadow-xl 
                               transform hover:scale-105 transition-all duration-200"
                    >
                      Generate Brief
                    </button>
                  </div>
                )}
              </section>
            )}
          </div>
        ) : (
          <div className="space-y-8">
            {/* Progress Tracking */}
            {generationStatus.stage !== 'completed' && (
              <ProgressTracker status={generationStatus} />
            )}

            {/* Generated Brief and Recommendations */}
            {generatedBrief && (
              <div className="space-y-8">
                <GeneratedBrief 
                  content={generatedBrief}
                  briefType={selectedBriefType!}
                  onReset={handleReset}
                />
                
                {strategicRecommendations && (
                  <StrategicRecommendations
                    recommendations={strategicRecommendations}
                    briefType={selectedBriefType!}
                  />
                )}
                
                {briefMetadata && (
                  <div className="bg-white rounded-2xl shadow-xl p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Generation Metrics
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center">
                        <p className="text-3xl font-bold text-indigo-600">
                          {briefMetadata.wordCount.toLocaleString()}
                        </p>
                        <p className="text-sm text-gray-600">Words</p>
                      </div>
                      <div className="text-center">
                        <p className="text-3xl font-bold text-green-600">
                          {briefMetadata.citations}
                        </p>
                        <p className="text-sm text-gray-600">Citations</p>
                      </div>
                      <div className="text-center">
                        <p className="text-3xl font-bold text-purple-600">
                          {briefMetadata.agentsUsed.length}
                        </p>
                        <p className="text-sm text-gray-600">AI Agents</p>
                      </div>
                      <div className="text-center">
                        <p className="text-3xl font-bold text-blue-600">
                          {briefMetadata.anonymizedDocuments}
                        </p>
                        <p className="text-sm text-gray-600">Docs Anonymized</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;