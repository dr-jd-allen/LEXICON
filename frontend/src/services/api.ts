import axios from 'axios';
import io from 'socket.io-client';
import { GenerateBriefRequest, GenerateBriefResponse, BriefGenerationStatus } from '../types';
import { parseApiError } from './errorHandler';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';
const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'http://localhost:5001';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const generateBrief = async ({
  briefType,
  files,
  expertName,
  jurisdiction,
  onProgress
}: GenerateBriefRequest): Promise<GenerateBriefResponse> => {
  // Map brief type to backend format
  const briefTypeMapping: Record<string, string> = {
    'daubert_motion': 'Daubert Motion',
    'daubert_response': 'Response to Daubert Challenge',
    'frye_motion': 'Frye Motion',
    'frye_response': 'Response to Frye Challenge',
    'motion_in_limine': 'Motion in Limine'
  };

  // Use the provided expert name

  // Establish WebSocket connection for real-time updates
  console.log('Connecting to WebSocket at:', SOCKET_URL);
  const socket = io(SOCKET_URL, {
    transports: ['websocket', 'polling'],
  });
  
  socket.on('connect', () => {
    console.log('WebSocket connected!', socket.id);
  });
  
  socket.on('connect_error', (error) => {
    console.error('WebSocket connection error:', error);
  });

  return new Promise((resolve, reject) => {
    // Listen for progress updates
    socket.on('progress_update', (data: any) => {
      console.log('Progress update received:', data);
      const progressMap: Record<string, BriefGenerationStatus['stage']> = {
        'Uploading documents': 'uploading',
        'Strategic analysis': 'strategic_analysis',
        'Legal research': 'legal_research',
        'Scientific research': 'scientific_research',
        'Writing brief': 'brief_writing',
        'Finalizing': 'final_review'
      };
      
      onProgress({
        stage: progressMap[data.stage] || 'uploading',
        progress: data.progress,
        currentAgent: data.agent || 'System',
        message: data.stage
      });
    });

    socket.on('brief_complete', (data: any) => {
      socket.disconnect();
      if (data.success) {
        resolve({
          brief: data.brief_excerpt || 'Brief generated successfully',
          metadata: {
            wordCount: data.full_result?.length || 1000,
            citations: 10,
            processingTime: Date.now()
          }
        });
      } else {
        const error = parseApiError({ response: { data: { message: data.error }, status: 500 } });
        reject(error);
      }
    });

    // Send request to generate brief
    api.post('/api/generate-brief', {
      expert_name: expertName,
      strategy: briefType.includes('response') ? 'support' : 'challenge',
      motion_type: briefTypeMapping[briefType] || briefType,
      jurisdiction: jurisdiction
    })
    .then((response) => {
      if (response.data.success) {
        // Server will emit progress via WebSocket
        onProgress({
          stage: 'uploading',
          progress: 10,
          currentAgent: 'System',
          message: 'Processing request...'
        });
      } else {
        throw new Error(response.data.error || 'Failed to start generation');
      }
    })
    .catch((error) => {
      socket.disconnect();
      const parsedError = parseApiError(error);
      reject(parsedError);
    });
  });
};

// Simulate API call for development
export const simulateGenerateBrief = async ({
  briefType,
  files,
  expertName,
  jurisdiction,
  onProgress
}: GenerateBriefRequest): Promise<GenerateBriefResponse> => {
  const stages: BriefGenerationStatus[] = [
    { stage: 'uploading', progress: 20, currentAgent: 'System', message: 'Processing uploaded files...' },
    { stage: 'strategic_analysis', progress: 35, currentAgent: 'Claude Opus 4', message: 'Analyzing case strategy and identifying key arguments...' },
    { stage: 'legal_research', progress: 50, currentAgent: 'O3 Pro Deep Research', message: 'Searching for supporting precedents in legal databases...' },
    { stage: 'scientific_research', progress: 65, currentAgent: 'GPT-4.1', message: 'Reviewing medical literature and expert methodologies...' },
    { stage: 'brief_writing', progress: 80, currentAgent: 'GPT-4.5', message: 'Drafting comprehensive legal arguments...' },
    { stage: 'final_review', progress: 95, currentAgent: 'Gemini 2.5 Pro', message: 'Fact-checking and polishing final brief...' },
    { stage: 'completed', progress: 100, currentAgent: 'System', message: 'Brief generation complete!' }
  ];

  // Simulate progress updates
  for (const status of stages) {
    await new Promise(resolve => setTimeout(resolve, 2000));
    onProgress(status);
  }

  // Return simulated brief
  const sampleBrief = `UNITED STATES DISTRICT COURT
${jurisdiction.toUpperCase()} DISTRICT

Case No. XX-XXXX

PLAINTIFF,
v.
DEFENDANT.

${briefType.replace(/_/g, ' ').toUpperCase()}

NOW COMES the Plaintiff, by and through undersigned counsel, and respectfully submits this ${briefType.replace(/_/g, ' ')} and states as follows:

I. INTRODUCTION

This motion seeks to ${briefType.includes('daubert') ? 'exclude the testimony of opposing expert witness pursuant to Federal Rule of Evidence 702 and Daubert v. Merrell Dow Pharmaceuticals, Inc.' : 'exclude certain evidence from trial'}.

II. STATEMENT OF FACTS

[Generated facts based on uploaded documents...]

III. LEGAL STANDARD

${briefType.includes('daubert') ? 'Under Daubert, trial judges serve as gatekeepers to ensure expert testimony is both relevant and reliable...' : 'The court has broad discretion to exclude evidence under Federal Rules of Evidence...'}

IV. ARGUMENT

A. The Expert's Methodology Lacks Scientific Validity
   1. No peer review or general acceptance
   2. Unknown error rate
   3. Failure to follow standard protocols

B. The Testimony Will Not Assist the Trier of Fact
   1. Confusing and misleading conclusions
   2. Prejudicial impact outweighs probative value

V. CONCLUSION

For the foregoing reasons, Plaintiff respectfully requests that this Court grant this motion and exclude the challenged testimony.

Respectfully submitted,

[Law Firm Name]
[Attorney Name]
[Bar Number]
[Address]
[Phone]
[Email]

Generated by LEXICON v0.1.5
AI Agents: Claude Opus 4, O3 Pro Deep Research, GPT-4.1, GPT-4.5, Gemini 2.5 Pro`;

  return {
    brief: sampleBrief,
    metadata: {
      wordCount: sampleBrief.split(/\s+/).length,
      citations: 15,
      processingTime: 14000
    }
  };
};