export type BriefType = 
  | 'daubert_motion'
  | 'daubert_response'
  | 'frye_motion'
  | 'frye_response'
  | 'motion_in_limine';

export interface UploadedFile {
  id: string;
  file: File;
  name: string;
  size: number;
  type: string;
  uploadProgress: number;
  status: 'uploading' | 'completed' | 'error';
}

export interface BriefGenerationStatus {
  stage: 'uploading' | 'anonymization' | 'strategic_analysis' | 'legal_research' | 
         'scientific_research' | 'brief_writing' | 'final_review' | 
         'completed' | 'error';
  progress: number;
  currentAgent: string;
  message: string;
  subTasks?: string[];
}

export interface GenerateBriefRequest {
  briefType: BriefType;
  files: UploadedFile[];
  expertName: string;
  jurisdiction: string;
  onProgress: (status: BriefGenerationStatus) => void;
}

export interface GenerateBriefResponse {
  brief: string;
  strategicRecommendations: string;
  metadata: {
    wordCount: number;
    citations: number;
    processingTime: number;
    agentsUsed: string[];
    anonymizedDocuments: number;
  };
}