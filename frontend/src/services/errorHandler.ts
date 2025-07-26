// Enhanced error handling for LEXICON frontend

export interface ErrorDetails {
  code: string;
  message: string;
  userMessage: string;
  recoveryAction?: string;
}

export class ApiError extends Error {
  public code: string;
  public userMessage: string;
  public recoveryAction?: string;
  public statusCode?: number;

  constructor(details: ErrorDetails, statusCode?: number) {
    super(details.message);
    this.name = 'ApiError';
    this.code = details.code;
    this.userMessage = details.userMessage;
    this.recoveryAction = details.recoveryAction;
    this.statusCode = statusCode;
  }
}

export const ErrorCodes = {
  // Authentication errors
  INVALID_API_KEY: 'INVALID_API_KEY',
  MISSING_API_KEY: 'MISSING_API_KEY',
  EXPIRED_API_KEY: 'EXPIRED_API_KEY',
  
  // Document processing errors
  INVALID_DOCUMENT_FORMAT: 'INVALID_DOCUMENT_FORMAT',
  DOCUMENT_TOO_LARGE: 'DOCUMENT_TOO_LARGE',
  DOCUMENT_PROCESSING_FAILED: 'DOCUMENT_PROCESSING_FAILED',
  NO_DOCUMENTS_PROVIDED: 'NO_DOCUMENTS_PROVIDED',
  
  // Brief generation errors
  INVALID_BRIEF_TYPE: 'INVALID_BRIEF_TYPE',
  INVALID_JURISDICTION: 'INVALID_JURISDICTION',
  GENERATION_FAILED: 'GENERATION_FAILED',
  GENERATION_TIMEOUT: 'GENERATION_TIMEOUT',
  
  // Network errors
  NETWORK_ERROR: 'NETWORK_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
  
  // Validation errors
  MISSING_REQUIRED_FIELD: 'MISSING_REQUIRED_FIELD',
  INVALID_INPUT: 'INVALID_INPUT',
  
  // Rate limiting
  RATE_LIMIT_EXCEEDED: 'RATE_LIMIT_EXCEEDED',
  
  // Unknown
  UNKNOWN_ERROR: 'UNKNOWN_ERROR'
};

export const ErrorMessages: Record<string, Omit<ErrorDetails, 'message'>> = {
  [ErrorCodes.INVALID_API_KEY]: {
    code: ErrorCodes.INVALID_API_KEY,
    userMessage: 'The API key provided is invalid. Please check your configuration.',
    recoveryAction: 'Verify your API keys in the .env file and restart the application.'
  },
  [ErrorCodes.MISSING_API_KEY]: {
    code: ErrorCodes.MISSING_API_KEY,
    userMessage: 'One or more required API keys are missing.',
    recoveryAction: 'Please configure all required API keys (Anthropic, OpenAI, Google) in your environment.'
  },
  [ErrorCodes.EXPIRED_API_KEY]: {
    code: ErrorCodes.EXPIRED_API_KEY,
    userMessage: 'Your API key has expired.',
    recoveryAction: 'Please renew your API subscription and update the key.'
  },
  [ErrorCodes.INVALID_DOCUMENT_FORMAT]: {
    code: ErrorCodes.INVALID_DOCUMENT_FORMAT,
    userMessage: 'The uploaded document format is not supported.',
    recoveryAction: 'Please upload documents in PDF, DOCX, or TXT format.'
  },
  [ErrorCodes.DOCUMENT_TOO_LARGE]: {
    code: ErrorCodes.DOCUMENT_TOO_LARGE,
    userMessage: 'The uploaded document exceeds the maximum size limit (100MB).',
    recoveryAction: 'Please reduce the file size or split into multiple documents.'
  },
  [ErrorCodes.DOCUMENT_PROCESSING_FAILED]: {
    code: ErrorCodes.DOCUMENT_PROCESSING_FAILED,
    userMessage: 'Failed to process the uploaded documents.',
    recoveryAction: 'Please check the document format and try again.'
  },
  [ErrorCodes.NO_DOCUMENTS_PROVIDED]: {
    code: ErrorCodes.NO_DOCUMENTS_PROVIDED,
    userMessage: 'No documents were provided for analysis.',
    recoveryAction: 'Please upload at least one document to generate a brief.'
  },
  [ErrorCodes.INVALID_BRIEF_TYPE]: {
    code: ErrorCodes.INVALID_BRIEF_TYPE,
    userMessage: 'The selected brief type is not valid.',
    recoveryAction: 'Please select a valid brief type from the dropdown.'
  },
  [ErrorCodes.INVALID_JURISDICTION]: {
    code: ErrorCodes.INVALID_JURISDICTION,
    userMessage: 'The specified jurisdiction is not valid.',
    recoveryAction: 'Please select a valid jurisdiction.'
  },
  [ErrorCodes.GENERATION_FAILED]: {
    code: ErrorCodes.GENERATION_FAILED,
    userMessage: 'Failed to generate the legal brief.',
    recoveryAction: 'Please try again. If the problem persists, contact support.'
  },
  [ErrorCodes.GENERATION_TIMEOUT]: {
    code: ErrorCodes.GENERATION_TIMEOUT,
    userMessage: 'Brief generation timed out due to high complexity.',
    recoveryAction: 'Try reducing the number of documents or simplifying the request.'
  },
  [ErrorCodes.NETWORK_ERROR]: {
    code: ErrorCodes.NETWORK_ERROR,
    userMessage: 'Network connection error.',
    recoveryAction: 'Please check your internet connection and try again.'
  },
  [ErrorCodes.SERVER_ERROR]: {
    code: ErrorCodes.SERVER_ERROR,
    userMessage: 'An internal server error occurred.',
    recoveryAction: 'Please try again later. If the issue persists, contact support.'
  },
  [ErrorCodes.SERVICE_UNAVAILABLE]: {
    code: ErrorCodes.SERVICE_UNAVAILABLE,
    userMessage: 'The service is temporarily unavailable.',
    recoveryAction: 'Please try again in a few minutes.'
  },
  [ErrorCodes.MISSING_REQUIRED_FIELD]: {
    code: ErrorCodes.MISSING_REQUIRED_FIELD,
    userMessage: 'Required information is missing.',
    recoveryAction: 'Please fill in all required fields.'
  },
  [ErrorCodes.INVALID_INPUT]: {
    code: ErrorCodes.INVALID_INPUT,
    userMessage: 'The provided input is invalid.',
    recoveryAction: 'Please check your input and try again.'
  },
  [ErrorCodes.RATE_LIMIT_EXCEEDED]: {
    code: ErrorCodes.RATE_LIMIT_EXCEEDED,
    userMessage: 'Too many requests. Please slow down.',
    recoveryAction: 'Wait a few minutes before trying again.'
  },
  [ErrorCodes.UNKNOWN_ERROR]: {
    code: ErrorCodes.UNKNOWN_ERROR,
    userMessage: 'An unexpected error occurred.',
    recoveryAction: 'Please try again. If the issue persists, contact support.'
  }
};

export function parseApiError(error: any): ApiError {
  // Handle axios errors
  if (error.response) {
    const status = error.response.status;
    const data = error.response.data;
    
    // Check for specific error codes from backend
    if (data?.error_code) {
      const errorDetails = ErrorMessages[data.error_code];
      if (errorDetails) {
        return new ApiError({
          ...errorDetails,
          message: data.message || error.message
        }, status);
      }
    }
    
    // Handle status codes
    switch (status) {
      case 400:
        if (data?.message?.includes('API key')) {
          return new ApiError({
            ...ErrorMessages[ErrorCodes.INVALID_API_KEY],
            message: data.message
          }, status);
        }
        return new ApiError({
          ...ErrorMessages[ErrorCodes.INVALID_INPUT],
          message: data.message || 'Bad request'
        }, status);
        
      case 401:
        return new ApiError({
          ...ErrorMessages[ErrorCodes.INVALID_API_KEY],
          message: 'Authentication failed'
        }, status);
        
      case 403:
        return new ApiError({
          ...ErrorMessages[ErrorCodes.EXPIRED_API_KEY],
          message: 'Access forbidden'
        }, status);
        
      case 413:
        return new ApiError({
          ...ErrorMessages[ErrorCodes.DOCUMENT_TOO_LARGE],
          message: 'Payload too large'
        }, status);
        
      case 429:
        return new ApiError({
          ...ErrorMessages[ErrorCodes.RATE_LIMIT_EXCEEDED],
          message: 'Rate limit exceeded'
        }, status);
        
      case 500:
      case 502:
      case 503:
        return new ApiError({
          ...ErrorMessages[ErrorCodes.SERVER_ERROR],
          message: data?.message || 'Server error'
        }, status);
        
      case 504:
        return new ApiError({
          ...ErrorMessages[ErrorCodes.GENERATION_TIMEOUT],
          message: 'Request timeout'
        }, status);
        
      default:
        return new ApiError({
          ...ErrorMessages[ErrorCodes.UNKNOWN_ERROR],
          message: data?.message || error.message
        }, status);
    }
  }
  
  // Handle network errors
  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
    return new ApiError({
      ...ErrorMessages[ErrorCodes.GENERATION_TIMEOUT],
      message: 'Request timed out'
    });
  }
  
  if (error.code === 'ERR_NETWORK' || !navigator.onLine) {
    return new ApiError({
      ...ErrorMessages[ErrorCodes.NETWORK_ERROR],
      message: 'Network connection lost'
    });
  }
  
  // Default error
  return new ApiError({
    ...ErrorMessages[ErrorCodes.UNKNOWN_ERROR],
    message: error.message || 'Unknown error occurred'
  });
}