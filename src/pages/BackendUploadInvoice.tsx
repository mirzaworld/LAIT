import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadInvoice } from '../services/api';
import { Upload, FileText, AlertCircle, CheckCircle, Loader2, X } from 'lucide-react';

interface UploadResult {
  id: string;
  filename: string;
  status: string;
}

const BackendUploadInvoice: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  
  const navigate = useNavigate();

  const handleFileUpload = async (file: File) => {
    if (!file) return;

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please select a PDF file');
      return;
    }

    setUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      console.log('🔄 Uploading file:', file.name);
      const result = await uploadInvoice(file);
      console.log('✅ Upload successful:', result);
      
      setUploadResult(result);
      
      // Auto-redirect to invoices page after successful upload
      setTimeout(() => {
        navigate('/invoices');
      }, 2000);
      
    } catch (err: any) {
      console.error('❌ Upload failed:', err);
      setError(err.message || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileUpload(file);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  if (uploadResult) {
    return (
      <div className="max-w-md mx-auto mt-8 p-6 bg-green-50 border border-green-200 rounded-lg">
        <div className="text-center">
          <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-4" />
          <h3 className="text-lg font-semibold text-green-800 mb-2">Upload Successful!</h3>
          <p className="text-green-600 mb-4">
            Your invoice "{uploadResult.filename}" has been uploaded and is being processed.
          </p>
          <p className="text-sm text-green-500">
            Invoice ID: {uploadResult.id}
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Redirecting to invoices page...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="text-center mb-8">
        <Upload className="mx-auto h-12 w-12 text-blue-500 mb-4" />
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Invoice</h1>
        <p className="text-gray-600">
          Upload legal invoices for AI-powered analysis and risk assessment
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-400 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Upload Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-400 hover:text-red-600"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      <div
        className={`
          border-2 border-dashed rounded-lg p-8 text-center transition-colors
          ${dragOver ? 'border-blue-400 bg-blue-50' : 'border-gray-300'}
          ${uploading ? 'opacity-50 pointer-events-none' : 'hover:border-blue-400 hover:bg-blue-50'}
        `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        {uploading ? (
          <div className="flex flex-col items-center">
            <Loader2 className="h-12 w-12 text-blue-500 animate-spin mb-4" />
            <p className="text-lg font-medium text-gray-700">Uploading...</p>
            <p className="text-sm text-gray-500">Please wait while we process your invoice</p>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <FileText className="h-12 w-12 text-gray-400 mb-4" />
            <p className="text-lg font-medium text-gray-700 mb-2">
              Drag and drop your PDF here
            </p>
            <p className="text-sm text-gray-500 mb-4">or</p>
            <label className="cursor-pointer">
              <span className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                Choose File
              </span>
              <input
                type="file"
                className="hidden"
                accept=".pdf"
                onChange={handleFileSelect}
                disabled={uploading}
              />
            </label>
            <p className="text-xs text-gray-400 mt-2">
              Only PDF files are supported
            </p>
          </div>
        )}
      </div>

      <div className="mt-8 bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">What happens next?</h3>
        <div className="space-y-3">
          <div className="flex items-start">
            <div className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white text-xs font-bold rounded-full flex items-center justify-center mr-3 mt-0.5">
              1
            </div>
            <div>
              <p className="font-medium text-gray-700">AI Analysis</p>
              <p className="text-sm text-gray-500">Our ML models analyze the invoice for risk factors and anomalies</p>
            </div>
          </div>
          <div className="flex items-start">
            <div className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white text-xs font-bold rounded-full flex items-center justify-center mr-3 mt-0.5">
              2
            </div>
            <div>
              <p className="font-medium text-gray-700">Data Extraction</p>
              <p className="text-sm text-gray-500">Vendor, amount, dates, and other key information is extracted</p>
            </div>
          </div>
          <div className="flex items-start">
            <div className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white text-xs font-bold rounded-full flex items-center justify-center mr-3 mt-0.5">
              3
            </div>
            <div>
              <p className="font-medium text-gray-700">Dashboard Update</p>
              <p className="text-sm text-gray-500">Your analytics and dashboard are updated with the new data</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BackendUploadInvoice;
