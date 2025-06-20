import React, { useState } from 'react';
import { Upload, FileText, Check, X, AlertTriangle, Loader2 } from 'lucide-react';

interface DocumentAnalysisResult {
  documentId: string;
  title: string;
  language: string;
  pageCount: number;
  extractedEntities: {
    type: string;
    text: string;
    confidence: number;
  }[];
  keyInformation: {
    category: string;
    text: string;
    relevance: number;
  }[];
  legalCitations: {
    citation: string;
    context: string;
  }[];
  riskAssessment: {
    score: number;
    level: 'low' | 'medium' | 'high';
    factors: string[];
  };
}

const DocumentAnalyzer: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DocumentAnalysisResult | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const selectedFile = event.target.files[0];
      const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      
      if (allowedTypes.includes(selectedFile.type)) {
        setFile(selectedFile);
        setError(null);
      } else {
        setFile(null);
        setError('Please select a PDF or Word document');
      }
    }
  };

  const handleAnalyzeDocument = async () => {
    if (!file) return;
    
    setIsAnalyzing(true);
    setError(null);
    setUploadProgress(0);
    
    // Create a simulated analysis result for demo purposes
    // In a real implementation, this would be an API call to the backend
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('analyzeEntities', 'true');
      formData.append('extractCitations', 'true');
      formData.append('performRiskAssessment', 'true');
      
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 300);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 3000));
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // In a real application, this would be the response from your backend API
      const mockResult: DocumentAnalysisResult = {
        documentId: `doc-${Math.random().toString(36).substr(2, 9)}`,
        title: file.name.split('.')[0],
        language: 'English',
        pageCount: Math.floor(Math.random() * 20) + 1,
        extractedEntities: [
          { type: 'PERSON', text: 'John Smith', confidence: 0.92 },
          { type: 'ORGANIZATION', text: 'Acme Corporation', confidence: 0.89 },
          { type: 'DATE', text: 'January 15, 2025', confidence: 0.95 },
          { type: 'LOCATION', text: 'New York', confidence: 0.87 },
        ],
        keyInformation: [
          { category: 'Contract Term', text: '24 months from signing date', relevance: 0.94 },
          { category: 'Payment Terms', text: 'Net 30 days', relevance: 0.88 },
          { category: 'Governing Law', text: 'State of Delaware', relevance: 0.92 },
        ],
        legalCitations: [
          { citation: 'Smith v. Jones, 123 F.3d 456 (9th Cir. 2024)', context: 'As established in Smith v. Jones, the principle of...' },
          { citation: '17 U.S.C. § 107', context: 'Under fair use provisions of 17 U.S.C. § 107...' },
        ],
        riskAssessment: {
          score: Math.floor(Math.random() * 100),
          level: Math.random() > 0.7 ? 'high' : Math.random() > 0.4 ? 'medium' : 'low',
          factors: [
            'Non-standard liability clause',
            'Missing dispute resolution process',
            'Vague termination terms'
          ],
        }
      };
      
      setResult(mockResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze document');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="p-6">
        <h2 className="text-xl font-semibold mb-4">Document Analysis</h2>
        
        {!result ? (
          <div className="space-y-6">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2 text-sm text-gray-600">
                Upload a legal document (PDF or Word) for AI analysis
              </p>
              
              <div className="mt-4">
                <input
                  type="file"
                  id="file-upload"
                  className="sr-only"
                  onChange={handleFileSelect}
                  accept=".pdf,.doc,.docx"
                />
                <label
                  htmlFor="file-upload"
                  className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 cursor-pointer inline-block"
                >
                  Select Document
                </label>
              </div>
            </div>
            
            {file && (
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <FileText className="h-5 w-5 text-gray-500 mr-2" />
                  <div>
                    <p className="font-medium text-gray-900">{file.name}</p>
                    <p className="text-xs text-gray-500">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setFile(null)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            )}
            
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex items-start">
                <AlertTriangle className="h-5 w-5 mr-2 flex-shrink-0 mt-0.5" />
                <p>{error}</p>
              </div>
            )}
            
            <div className="flex justify-end">
              <button
                onClick={handleAnalyzeDocument}
                disabled={!file || isAnalyzing}
                className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Analyze Document
                  </>
                )}
              </button>
            </div>
            
            {isAnalyzing && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Uploading and analyzing...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div
                    className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-medium">{result.title}</h3>
                <p className="text-sm text-gray-500">
                  {result.pageCount} pages • {result.language}
                </p>
              </div>
              <button
                onClick={() => setResult(null)}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md"
              >
                New Analysis
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h4 className="font-medium text-gray-900">Extracted Entities</h4>
                <div className="space-y-2">
                  {result.extractedEntities.map((entity, index) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded-md">
                      <div className="flex items-center space-x-2">
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-md">
                          {entity.type}
                        </span>
                        <span>{entity.text}</span>
                      </div>
                      <span className="text-sm text-gray-500">
                        {Math.round(entity.confidence * 100)}%
                      </span>
                    </div>
                  ))}
                </div>
                
                <h4 className="font-medium text-gray-900 pt-2">Key Information</h4>
                <div className="space-y-2">
                  {result.keyInformation.map((info, index) => (
                    <div key={index} className="p-2 bg-gray-50 rounded-md">
                      <div className="text-sm font-medium text-gray-700">{info.category}</div>
                      <div className="text-sm mt-1">{info.text}</div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="space-y-4">
                <h4 className="font-medium text-gray-900">Risk Assessment</h4>
                <div className="p-4 bg-gray-50 rounded-md">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">Risk Score:</span>
                    <span className={`px-2 py-1 rounded-full text-sm ${getRiskLevelColor(result.riskAssessment.level)}`}>
                      {result.riskAssessment.score}/100 ({result.riskAssessment.level.toUpperCase()})
                    </span>
                  </div>
                  
                  <h5 className="text-sm font-medium mt-3 mb-2">Risk Factors:</h5>
                  <ul className="space-y-1 text-sm">
                    {result.riskAssessment.factors.map((factor, index) => (
                      <li key={index} className="flex items-baseline">
                        <AlertTriangle className="h-3 w-3 text-yellow-500 mr-2 flex-shrink-0" />
                        {factor}
                      </li>
                    ))}
                  </ul>
                </div>
                
                <h4 className="font-medium text-gray-900 pt-2">Legal Citations</h4>
                <div className="space-y-2">
                  {result.legalCitations.map((citation, index) => (
                    <div key={index} className="p-2 bg-gray-50 rounded-md">
                      <div className="text-sm font-medium text-blue-600">{citation.citation}</div>
                      <div className="text-sm text-gray-600 mt-1 italic">"{citation.context}"</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentAnalyzer;
