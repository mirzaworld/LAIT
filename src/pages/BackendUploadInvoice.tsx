import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadInvoice } from '../services/api';
import { Upload, FileText, AlertCircle, CheckCircle, Loader2, X } from 'lucide-react';

interface UploadResult {
  id?: string;
  invoice_id?: number;
  filename: string;
  status?: string;
  message?: string;
  amount?: number;
  vendor_name?: string;
  ai_analysis?: {
    confidence_score: number;
    ai_insights: string[];
    extracted_data: {
      amount: number;
      category: string;
      vendor_name: string;
      due_date: string;
      line_items: Array<{
        description: string;
        amount: number;
        quantity: number;
        rate: number;
      }>;
    };
    risk_flags: Array<{
      level: string;
      message: string;
      action: string;
    }>;
    recommendations: string[];
  };
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
    const allowedTypes = ['.pdf', '.txt', '.doc', '.docx', '.jpg', '.jpeg', '.png'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    if (!allowedTypes.includes(fileExtension)) {
      setError('Please select a valid file (PDF, TXT, DOC, DOCX, JPG, PNG)');
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
      <div className="max-w-4xl mx-auto mt-8 space-y-6">
        {/* Success Header */}
        <div className="p-6 bg-green-50 border border-green-200 rounded-lg">
          <div className="text-center">
            <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-4" />
            <h3 className="text-lg font-semibold text-green-800 mb-2">Upload Successful!</h3>
            <p className="text-green-600 mb-4">
              Your invoice "{uploadResult.filename}" has been uploaded and analyzed.
            </p>
            <p className="text-sm text-green-500">
              Invoice ID: {uploadResult.invoice_id}
            </p>
          </div>
        </div>

        {/* AI Analysis Results */}
        {uploadResult.ai_analysis && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-6 flex items-center">
              <FileText className="mr-2 h-5 w-5" />
              AI Analysis Results
            </h3>

            {/* Confidence Score */}
            <div className="mb-6 p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-blue-800">Analysis Confidence</span>
                <span className="text-lg font-bold text-blue-600">
                  {(uploadResult.ai_analysis.confidence_score * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-2 mt-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{ width: `${uploadResult.ai_analysis.confidence_score * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Extracted Data */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold text-gray-700 mb-3">Extracted Information</h4>
                <div className="space-y-2 text-sm">
                  <div><strong>Vendor:</strong> {uploadResult.ai_analysis.extracted_data.vendor_name}</div>
                  <div><strong>Amount:</strong> ${uploadResult.ai_analysis.extracted_data.amount.toFixed(2)}</div>
                  <div><strong>Category:</strong> {uploadResult.ai_analysis.extracted_data.category.replace('_', ' ').toUpperCase()}</div>
                  <div><strong>Due Date:</strong> {uploadResult.ai_analysis.extracted_data.due_date}</div>
                </div>
              </div>

              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold text-gray-700 mb-3">Line Items</h4>
                <div className="space-y-2 text-sm">
                  {uploadResult.ai_analysis.extracted_data.line_items.slice(0, 3).map((item, index) => (
                    <div key={index} className="border-b border-gray-200 pb-1">
                      <div className="font-medium">{item.description}</div>
                      <div className="text-gray-600">${item.amount.toFixed(2)} ({item.quantity} × ${item.rate.toFixed(2)})</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* AI Insights */}
            <div className="mb-6 p-4 bg-indigo-50 rounded-lg">
              <h4 className="font-semibold text-indigo-800 mb-3">AI Insights</h4>
              <ul className="space-y-1">
                {uploadResult.ai_analysis.ai_insights.map((insight, index) => (
                  <li key={index} className="text-sm text-indigo-700 flex items-start">
                    <span className="mr-2">•</span>
                    {insight}
                  </li>
                ))}
              </ul>
            </div>

            {/* Risk Flags */}
            {uploadResult.ai_analysis.risk_flags.length > 0 && (
              <div className="mb-6 p-4 bg-yellow-50 rounded-lg">
                <h4 className="font-semibold text-yellow-800 mb-3 flex items-center">
                  <AlertCircle className="mr-1 h-4 w-4" />
                  Risk Flags
                </h4>
                <ul className="space-y-2">
                  {uploadResult.ai_analysis.risk_flags.map((flag, index) => (
                    <li key={index} className="text-sm">
                      <div className="font-medium text-yellow-700">{flag.message}</div>
                      <div className="text-yellow-600">{flag.action}</div>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommendations */}
            <div className="p-4 bg-emerald-50 rounded-lg">
              <h4 className="font-semibold text-emerald-800 mb-3">Recommendations</h4>
              <ul className="space-y-1">
                {uploadResult.ai_analysis.recommendations.map((recommendation, index) => (
                  <li key={index} className="text-sm text-emerald-700 flex items-start">
                    <span className="mr-2">•</span>
                    {recommendation}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4">
          <button
            onClick={() => navigate('/invoices')}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            View All Invoices
          </button>
          <button
            onClick={() => setUploadResult(null)}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Upload Another
          </button>
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
                accept=".pdf,.txt,.doc,.docx,.jpg,.jpeg,.png"
                onChange={handleFileSelect}
                disabled={uploading}
              />
            </label>
            <p className="text-xs text-gray-400 mt-2">
              Supports PDF, TXT, DOC, DOCX, JPG, PNG files
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
