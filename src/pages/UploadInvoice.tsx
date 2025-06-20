import React, { useState } from 'react';
import { Upload, FileText, AlertTriangle, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { uploadInvoice } from '../services/api';

interface UploadResult {
  invoice_id: string;
  invoice_added: boolean;
  analysis: {
    risk_score: number;
    risk_level: string;
    recommendations: string[];
  };
}

const UploadInvoice: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});
  const [uploadResults, setUploadResults] = useState<Record<string, UploadResult>>({});
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  
  // Constants
  const MAX_FILES = 5; // Maximum number of files that can be uploaded at once

  // Max file size: 10MB
  const MAX_FILE_SIZE = 10 * 1024 * 1024;
  
  const validateFile = (file: File): boolean => {
    // Check file type
    const isValidType = file.type === 'application/pdf' || 
                       file.type === 'text/plain' || 
                       file.name.endsWith('.pdf');
                       
    // Check file size
    const isValidSize = file.size <= MAX_FILE_SIZE;
    
    if (!isValidType) {
      setError('Only PDF and text files are allowed');
      return false;
    }
    
    if (!isValidSize) {
      setError(`File size exceeds the limit of ${MAX_FILE_SIZE / (1024 * 1024)}MB`);
      return false;
    }
    
    return true;
  };
  
  // Check if adding files would exceed the maximum allowed
  const checkMaxFiles = (newFilesCount: number): boolean => {
    if (files.length + newFilesCount > MAX_FILES) {
      setError(`Cannot upload more than ${MAX_FILES} files at once`);
      return false;
    }
    return true;
  };

  const handleFileDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setError(null);
    
    const filesToProcess = Array.from(event.dataTransfer.files);
    
    // Check if adding these files would exceed the maximum
    if (!checkMaxFiles(filesToProcess.length)) {
      return;
    }
    
    const validFiles = filesToProcess.filter(validateFile);
    if (validFiles.length > 0) {
      setFiles((prevFiles) => [...prevFiles, ...validFiles]);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    
    const filesToProcess = Array.from(event.target.files || []);
    
    // Check if adding these files would exceed the maximum
    if (!checkMaxFiles(filesToProcess.length)) {
      return;
    }
    
    const validFiles = filesToProcess.filter(validateFile);
    if (validFiles.length > 0) {
      setFiles((prevFiles) => [...prevFiles, ...validFiles]);
    }
  };

  const handleUploadAll = async () => {
    setIsUploading(true);
    setError(null);
    
    // Process files one by one to avoid memory issues
    for (const file of files) {
      try {
        setUploadProgress(prev => ({ ...prev, [file.name]: 0 }));
        console.log(`Uploading file: ${file.name}`);
        
        // Simulate progress to give feedback
        const progressInterval = setInterval(() => {
          setUploadProgress(prev => {
            const currentProgress = prev[file.name] || 0;
            if (currentProgress < 90) {
              return { ...prev, [file.name]: currentProgress + 10 };
            }
            return prev;
          });
        }, 300);
        
        // Use the API service function
        const result = await uploadInvoice(
          file,
          'Unknown Vendor', // Default vendor
          undefined, // Amount will be extracted from file
          undefined, // Date will be extracted from file
          'Legal Services', // Default category
          `Uploaded via web interface: ${file.name}`
        );
        
        clearInterval(progressInterval);
        setUploadProgress(prev => ({ ...prev, [file.name]: 100 }));
        setUploadResults(prev => ({ ...prev, [file.name]: result }));
        
        // Add a small delay between file uploads to prevent overwhelming the server
        await new Promise(resolve => setTimeout(resolve, 500));
        
        console.log(`Successfully uploaded ${file.name}:`, result);
      } catch (error) {
        console.error(`Error uploading ${file.name}:`, error);
        setUploadProgress(prev => ({ ...prev, [file.name]: -1 }));
        setError(`Failed to process ${file.name}: ${error instanceof Error ? error.message : 'Unknown error'}`);
        break; // Stop uploading on first error
      }
    }
    
    setIsUploading(false);
  };

  const handleRemoveFile = (fileName: string) => {
    setFiles(files.filter(file => file.name !== fileName));
    const newProgress = { ...uploadProgress };
    const newResults = { ...uploadResults };
    delete newProgress[fileName];
    delete newResults[fileName];
    setUploadProgress(newProgress);
    setUploadResults(newResults);
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'high':
        return 'text-danger-600';
      case 'medium':
        return 'text-warning-600';
      case 'low':
        return 'text-success-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upload Invoices</h1>
        <p className="mt-1 text-sm text-gray-500">
          Upload legal invoices for automatic analysis and risk assessment
        </p>
      </div>

      {error && (
        <div className="bg-danger-50 text-danger-700 p-4 rounded-lg flex items-center">
          <AlertTriangle className="w-5 h-5 mr-2 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div
        onDrop={handleFileDrop}
        onDragOver={handleDragOver}
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-500 transition-colors"
      >
        <div className="flex flex-col items-center justify-center">
          <Upload className="w-12 h-12 text-gray-400 mb-4" />
          <p className="text-gray-600 mb-2">Drag and drop PDF invoices here, or</p>
          <label className="cursor-pointer text-primary-600 hover:text-primary-700">
            browse to upload
            <input
              type="file"
              className="hidden"
              multiple
              accept=".pdf,.txt"
              onChange={handleFileSelect}
            />
          </label>
          <p className="text-xs text-gray-500 mt-2">Supported formats: PDF, TXT</p>
        </div>
      </div>

      {files.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Selected Files ({files.length})</h2>
            <button
              onClick={() => {
                setFiles([]);
                setUploadProgress({});
                setUploadResults({});
                setError(null);
              }}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Clear All
            </button>
          </div>
          
          <div className="space-y-3">
            {files.map((file) => (
              <div key={file.name} className="bg-white p-4 rounded-lg shadow border">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <FileText className="w-5 h-5 text-gray-400 mr-2" />
                    <div>
                      <span className="text-sm text-gray-700 font-medium">{file.name}</span>
                      <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {uploadProgress[file.name] === 100 && (
                      <CheckCircle className="w-5 h-5 text-success-500" />
                    )}
                    {uploadProgress[file.name] === -1 && (
                      <XCircle className="w-5 h-5 text-danger-500" />
                    )}
                    {uploadProgress[file.name] === 0 && isUploading && (
                      <RefreshCw className="w-4 h-4 text-primary-500 animate-spin" />
                    )}
                    <button
                      onClick={() => handleRemoveFile(file.name)}
                      className="text-xs text-gray-400 hover:text-danger-500 disabled:opacity-50"
                      disabled={isUploading}
                    >
                      Remove
                    </button>
                  </div>
                </div>

                {uploadResults[file.name] && (
                  <div className="mt-4 border-t pt-4">
                    <h3 className="text-sm font-semibold text-gray-900 mb-3">Upload Results</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">Invoice ID</p>
                        <p className="text-sm font-medium">{uploadResults[file.name].invoice_id}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Status</p>
                        <p className="text-sm font-medium">
                          {uploadResults[file.name].invoice_added ? (
                            <span className="text-success-600">✓ Successfully Added</span>
                          ) : (
                            <span className="text-danger-600">✗ Failed to Add</span>
                          )}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Risk Level</p>
                        <p className={`text-sm font-medium capitalize ${getRiskLevelColor(uploadResults[file.name].analysis.risk_level)}`}>
                          {uploadResults[file.name].analysis.risk_level}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Risk Score</p>
                        <p className="text-sm font-medium">{uploadResults[file.name].analysis.risk_score}%</p>
                      </div>
                    </div>

                    {uploadResults[file.name].analysis.recommendations && uploadResults[file.name].analysis.recommendations.length > 0 && (
                      <div className="mt-4">
                        <p className="text-sm font-semibold text-gray-900 mb-2">AI Recommendations</p>
                        <ul className="list-disc list-inside text-sm text-primary-600 space-y-1">
                          {uploadResults[file.name].analysis.recommendations.map((rec, index) => (
                            <li key={index}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>

          <button
            onClick={handleUploadAll}
            disabled={files.length === 0 || isUploading}
            className="w-full py-3 px-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isUploading ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Uploading and Analyzing...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4 mr-2" />
                Upload and Analyze All Files
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default UploadInvoice;
