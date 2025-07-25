import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  CloudArrowUpIcon, 
  DocumentIcon, 
  XMarkIcon,
  ShieldCheckIcon,
  LockClosedIcon 
} from '@heroicons/react/24/outline';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadedFile } from '../types';
import { formatFileSize } from '../utils/formatters';

interface FileUploadProps {
  onFilesUpload: (files: UploadedFile[]) => void;
  uploadedFiles: UploadedFile[];
  onRemoveFile: (id: string) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFilesUpload, uploadedFiles, onRemoveFile }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      uploadProgress: 100,
      status: 'completed' as const
    }));
    onFilesUpload(newFiles);
  }, [onFilesUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'image/*': ['.png', '.jpg', '.jpeg', '.gif']
    },
    multiple: true
  });

  return (
    <div className="space-y-6">
      <div
        {...getRootProps()}
        className={`relative border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
                    transition-all duration-300 ${
                      isDragActive 
                        ? 'border-lexicon-accent bg-purple-50 scale-105' 
                        : 'border-gray-300 hover:border-lexicon-primary hover:bg-blue-50'
                    }`}
      >
        <input {...getInputProps()} />
        <CloudArrowUpIcon className={`mx-auto h-16 w-16 mb-4 transition-colors ${
          isDragActive ? 'text-lexicon-accent' : 'text-gray-400'
        }`} />
        <p className="text-lg font-medium text-gray-700">
          {isDragActive ? 'Drop files here' : 'Drag & drop case files here'}
        </p>
        <p className="mt-2 text-sm text-gray-500">
          or <span className="text-lexicon-primary font-semibold">browse</span> to select files
        </p>
        <p className="mt-4 text-xs text-gray-400">
          Supported: PDF, DOC, DOCX, TXT, Images (medical records, assessments, court orders)
        </p>
        <div className="mt-4 inline-flex items-center px-3 py-1 bg-green-100 rounded-full">
          <ShieldCheckIcon className="w-4 h-4 text-green-700 mr-2" />
          <span className="text-xs font-medium text-green-700">
            HIPAA-Compliant Anonymization Enabled
          </span>
        </div>
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-lexicon-dark">
            Uploaded Documents ({uploadedFiles.length})
          </h3>
          <AnimatePresence>
            {uploadedFiles.map((file) => (
              <motion.div
                key={file.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -100 }}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg 
                         hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <DocumentIcon className="h-8 w-8 text-lexicon-primary" />
                    <LockClosedIcon className="h-4 w-4 text-green-600 absolute -bottom-1 -right-1 
                                             bg-white rounded-full" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{file.name}</p>
                    <div className="flex items-center space-x-2">
                      <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                      <span className="text-xs text-green-600">• Will be anonymized</span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => onRemoveFile(file.id)}
                  className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
};

export default FileUpload;