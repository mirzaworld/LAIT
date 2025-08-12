import React, { useState, useCallback, useRef } from 'react';
import { Upload as UploadIcon, FileText, AlertCircle, CheckCircle, Loader2, X, Eye } from 'lucide-react';
import api from '../services/api';

interface UploadResult {
  message: string;
  invoice: {
    id: string;
    filename: string;
    vendor: string;
    amount: number;
    status: string;
    processed_text?: string;
  };
  analysis: {
    risk_score: number;
    risk_level: string;
    category: string;
    confidence: number;
    recommendations: string[];
    key_data: {
      vendor?: string;
      amount?: number;
      date?: string;
      invoice_number?: string;
    };
  };
}

const Upload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showFullResponse, setShowFullResponse] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Check if user is authenticated
  const authenticated = api.auth.isAuthenticated();
  const token = localStorage.getItem('lait_token');

  // Handle drag and drop
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    if (droppedFiles.length > 0) {
      const droppedFile = droppedFiles[0];
      if (validateFile(droppedFile)) {
        setFile(droppedFile);
        setError(null);
      }
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && validateFile(selectedFile)) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const validateFile = (file: File): boolean => {
    const allowedTypes = ['application/pdf', 'text/plain', 'application/msword', 
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().match(/\.(pdf|txt|doc|docx)$/)) {
      setError('Please select a PDF, TXT, DOC, or DOCX file');
      return false;
    }

    if (file.size > maxSize) {
      setError('File size must be less than 10MB');
      return false;
    }

    return true;
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    if (!authenticated) {
      setError('Please log in to upload invoices');
      return;
    }

    setIsUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      console.log('🔄 Uploading file:', file.name, 'with token:', token ? 'present' : 'missing');
      
      // Call the invoices.upload API function
      const result = await api.invoices.upload(file);
      
      console.log('✅ Upload successful:', result);
      setUploadResult(result);
      
      // Clear the file selection
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
    } catch (err: any) {
      console.error('❌ Upload failed:', err);
      setError(err.message || 'Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const clearSelection = () => {
    setFile(null);
    setError(null);
    setUploadResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (!authenticated) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-yellow-500 mb-4" />
          <h2 className="text-xl font-semibold text-yellow-800 mb-2">Authentication Required</h2>
          <p className="text-yellow-700">
            Please log in to upload and analyze invoices.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <UploadIcon className="mx-auto h-12 w-12 text-blue-500 mb-4" />
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Invoice</h1>
        <p className="text-gray-600">
          Upload legal invoices for AI-powered analysis and risk assessment
        </p>
      </div>

      {/* Upload Area */}
      <div className="bg-white rounded-lg shadow-sm border-2 border-dashed border-gray-300 p-8">
        {/* Drag and Drop Zone */}
        <div
          className={`relative transition-all duration-200 ${
            isDragOver 
              ? 'border-blue-500 bg-blue-50' 
              : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
          } border-2 border-dashed rounded-lg p-8 text-center`}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          {file ? (
            // File Selected State
            <div className="space-y-4">
              <FileText className="mx-auto h-12 w-12 text-green-500" />
              <div className="space-y-2">
                <p className="text-lg font-medium text-gray-900">{file.name}</p>
                <p className="text-sm text-gray-500">{formatBytes(file.size)}</p>
                <div className="flex justify-center space-x-3">
                  <button
                    onClick={handleUpload}
                    disabled={isUploading}
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isUploading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <UploadIcon className="mr-2 h-4 w-4" />
                        Upload & Analyze
                      </>
                    )}
                  </button>
                  <button
                    onClick={clearSelection}
                    disabled={isUploading}
                    className="inline-flex items-center px-4 py-2 bg-gray-200 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50"
                  >
                    <X className="mr-2 h-4 w-4" />
                    Clear
                  </button>
                </div>
              </div>
            </div>
          ) : (
            // Empty State
            <div className="space-y-4">
              <UploadIcon className={`mx-auto h-12 w-12 ${isDragOver ? 'text-blue-500' : 'text-gray-400'}`} />
              <div>
                <p className="text-lg font-medium text-gray-700 mb-2">
                  {isDragOver ? 'Drop your file here' : 'Drag and drop your invoice here'}
                </p>
                <p className="text-sm text-gray-500 mb-4">or</p>
                <label className="cursor-pointer inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                  <UploadIcon className="mr-2 h-4 w-4" />
                  Choose File
                  <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    accept=".pdf,.txt,.doc,.docx"
                    onChange={handleFileSelect}
                  />
                </label>
              </div>
              <p className="text-xs text-gray-500">
                Supported formats: PDF, TXT, DOC, DOCX • Max size: 10MB
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-400 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Upload Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Success and Analysis Results */}
      {uploadResult && (
        <div className="space-y-6">
          {/* Success Header */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="text-center">
              <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-4" />
              <h3 className="text-lg font-semibold text-green-800 mb-2">Upload Successful!</h3>
              <p className="text-green-600 mb-4">
                Your invoice "{uploadResult.invoice.filename}" has been uploaded and analyzed.
              </p>
            </div>
          </div>

          {/* Analysis Results */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">AI Analysis Results</h3>
            </div>
            <div className="p-6 space-y-6">
              {/* Invoice Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Invoice Details</h4>
                  <div className="space-y-2 text-sm">
                    <div><span className="font-medium text-gray-600">ID:</span> {uploadResult.invoice.id}</div>
                    <div><span className="font-medium text-gray-600">Vendor:</span> {uploadResult.invoice.vendor}</div>
                    <div><span className="font-medium text-gray-600">Amount:</span> ${uploadResult.invoice.amount.toLocaleString()}</div>
                    <div><span className="font-medium text-gray-600">Status:</span> 
                      <span className="ml-1 px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                        {uploadResult.invoice.status}
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Risk Assessment</h4>
                  <div className="space-y-2 text-sm">
                    <div><span className="font-medium text-gray-600">Risk Score:</span> {uploadResult.analysis.risk_score}/100</div>
                    <div><span className="font-medium text-gray-600">Risk Level:</span>
                      <span className={`ml-1 px-2 py-1 text-xs rounded-full ${getRiskColor(uploadResult.analysis.risk_level)}`}>
                        {uploadResult.analysis.risk_level.toUpperCase()}
                      </span>
                    </div>
                    <div><span className="font-medium text-gray-600">Category:</span> {uploadResult.analysis.category}</div>
                    <div><span className="font-medium text-gray-600">Confidence:</span> {(uploadResult.analysis.confidence * 100).toFixed(1)}%</div>
                  </div>
                </div>
              </div>

              {/* Key Extracted Data */}
              {uploadResult.analysis.key_data && Object.keys(uploadResult.analysis.key_data).length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Extracted Key Data</h4>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      {uploadResult.analysis.key_data.vendor && (
                        <div><span className="font-medium text-gray-600">Vendor:</span> {uploadResult.analysis.key_data.vendor}</div>
                      )}
                      {uploadResult.analysis.key_data.amount && (
                        <div><span className="font-medium text-gray-600">Amount:</span> ${uploadResult.analysis.key_data.amount.toLocaleString()}</div>
                      )}
                      {uploadResult.analysis.key_data.date && (
                        <div><span className="font-medium text-gray-600">Date:</span> {uploadResult.analysis.key_data.date}</div>
                      )}
                      {uploadResult.analysis.key_data.invoice_number && (
                        <div><span className="font-medium text-gray-600">Invoice #:</span> {uploadResult.analysis.key_data.invoice_number}</div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {uploadResult.analysis.recommendations && uploadResult.analysis.recommendations.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">AI Recommendations</h4>
                  <div className="bg-emerald-50 rounded-lg p-4">
                    <ul className="space-y-2">
                      {uploadResult.analysis.recommendations.map((recommendation, index) => (
                        <li key={index} className="text-sm text-emerald-700 flex items-start">
                          <span className="mr-2 mt-1">•</span>
                          <span>{recommendation}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Full JSON Response Toggle */}
              <div className="border-t border-gray-200 pt-4">
                <button
                  onClick={() => setShowFullResponse(!showFullResponse)}
                  className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
                >
                  <Eye className="mr-2 h-4 w-4" />
                  {showFullResponse ? 'Hide' : 'Show'} Full JSON Response
                </button>
                
                {showFullResponse && (
                  <div className="mt-4">
                    <div className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-auto text-xs font-mono">
                      <pre>{JSON.stringify(uploadResult, null, 2)}</pre>
                    </div>
                  </div>
                )}
              </div>

              {/* Action Button */}
              <div className="flex justify-center pt-4">
                <button
                  onClick={() => setUploadResult(null)}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Upload Another Invoice
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Upload;
