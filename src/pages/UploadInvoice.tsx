import React, { useState } from 'react';
import { Upload, FileText, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

interface AnalysisResult {
  invoice_data: {
    invoice_number: string;
    date: string;
    amount: number;
    vendor: string;
    hours_billed: number;
    rate: number;
  };
  analysis: {
    risk_score: number;
    anomalies: string[];
    insights: string[];
    recommendations: string[];
  };
}

const UploadInvoice: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});
  const [analysisResults, setAnalysisResults] = useState<Record<string, AnalysisResult>>({});
  const [error, setError] = useState<string | null>(null);

  const handleFileDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const droppedFiles = Array.from(event.dataTransfer.files).filter(
      file => file.type === 'application/pdf' || file.type === 'text/plain' || file.name.endsWith('.pdf')
    );
    setFiles((prevFiles) => [...prevFiles, ...droppedFiles]);
    setError(null);
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || []).filter(
      file => file.type === 'application/pdf' || file.type === 'text/plain' || file.name.endsWith('.pdf')
    );
    setFiles((prevFiles) => [...prevFiles, ...selectedFiles]);
    setError(null);
  };

  const handleUploadAll = async () => {
    const newProgress: Record<string, number> = {};
    const newResults: Record<string, AnalysisResult> = {};
    
    for (const file of files) {
      newProgress[file.name] = 0;
      setUploadProgress({ ...newProgress });

      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('http://localhost:5002/api/upload-invoice', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Failed to upload ${file.name}`);
        }

        const result = await response.json();
        newProgress[file.name] = 100;
        newResults[file.name] = result;
        
        setUploadProgress({ ...newProgress });
        setAnalysisResults({ ...newResults });
      } catch (error) {
        console.error(error);
        newProgress[file.name] = -1; // Indicate failure
        setUploadProgress({ ...newProgress });
        setError(`Failed to process ${file.name}. Please try again.`);
      }
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold text-gray-900">Upload Invoices</h1>

      {error && (
        <div className="bg-danger-50 text-danger-700 p-4 rounded-lg flex items-center">
          <AlertTriangle className="w-5 h-5 mr-2" />
          {error}
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
        </div>
      </div>

      {files.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">Selected Files</h2>
          <div className="space-y-2">
            {files.map((file) => (
              <div key={file.name} className="bg-white p-4 rounded-lg shadow border">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <FileText className="w-5 h-5 text-gray-400 mr-2" />
                    <span className="text-sm text-gray-700">{file.name}</span>
                  </div>
                  <div className="flex items-center">
                    {uploadProgress[file.name] === 100 && (
                      <CheckCircle className="w-5 h-5 text-success-500" />
                    )}
                    {uploadProgress[file.name] === -1 && (
                      <XCircle className="w-5 h-5 text-danger-500" />
                    )}
                    {uploadProgress[file.name] > 0 && uploadProgress[file.name] < 100 && (
                      <span className="text-sm text-gray-500">{uploadProgress[file.name]}%</span>
                    )}
                  </div>
                </div>

                {analysisResults[file.name] && (
                  <div className="mt-4 border-t pt-4">
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">Analysis Results</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">Invoice Number</p>
                        <p className="text-sm font-medium">{analysisResults[file.name].invoice_data.invoice_number}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Amount</p>
                        <p className="text-sm font-medium">
                          ${analysisResults[file.name].invoice_data.amount.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Hours Billed</p>
                        <p className="text-sm font-medium">{analysisResults[file.name].invoice_data.hours_billed}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Risk Score</p>
                        <p className="text-sm font-medium">{analysisResults[file.name].analysis.risk_score}%</p>
                      </div>
                    </div>

                    {analysisResults[file.name].analysis.anomalies.length > 0 && (
                      <div className="mt-4">
                        <p className="text-sm font-semibold text-gray-900 mb-2">Anomalies Detected</p>
                        <ul className="list-disc list-inside text-sm text-danger-600">
                          {analysisResults[file.name].analysis.anomalies.map((anomaly, index) => (
                            <li key={index}>{anomaly}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {analysisResults[file.name].analysis.recommendations.length > 0 && (
                      <div className="mt-4">
                        <p className="text-sm font-semibold text-gray-900 mb-2">Recommendations</p>
                        <ul className="list-disc list-inside text-sm text-primary-600">
                          {analysisResults[file.name].analysis.recommendations.map((rec, index) => (
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
            disabled={files.length === 0}
            className="w-full py-2 px-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Upload and Analyze All Files
          </button>
        </div>
      )}
    </div>
  );
};

export default UploadInvoice;
