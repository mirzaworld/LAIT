import axios from 'axios';

export interface PDFAnalysisResult {
  vendor: string;
  amount: number;
  date: string;
  lineItems: {
    description: string;
    hours: number;
    rate: number;
    total: number;
  }[];
  riskScore: number;
  riskFactors: {
    type: string;
    description: string;
    severity: 'low' | 'medium' | 'high';
  }[];
  metrics: {
    totalHours: number;
    avgRate: number;
    topExpenses: { category: string; amount: number }[];
  };
  benchmarks: {
    rateComparison: {
      avgMarketRate: number;
      percentDiff: number;
    };
    hoursComparison: {
      avgMarketHours: number;
      percentDiff: number;
    };
  };
}

export interface InvoiceReport {
  id: string;
  summary: {
    totalAmount: number;
    totalHours: number;
    avgRate: number;
    riskScore: number;
  };
  analysis: {
    rateAnalysis: {
      marketComparison: number;
      historicalTrend: number;
      outliers: { timekeeper: string; rate: number; marketRate: number }[];
    };
    timeAnalysis: {
      efficiency: number;
      duplicateWork: { description: string; hours: number; timekeepers: string[] }[];
      blockBilling: { description: string; hours: number }[];
    };
    recommendations: {
      type: string;
      description: string;
      potentialSavings: number;
      priority: 'high' | 'medium' | 'low';
    }[];
  };
  historical: {
    monthlyTotals: { month: string; amount: number }[];
    yearOverYear: { year: string; amount: number }[];
    trends: { metric: string; change: number; interpretation: string }[];
  };
}

class PDFService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  }

  async uploadAndAnalyze(file: File): Promise<PDFAnalysisResult> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${this.baseUrl}/api/invoices/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      console.error('Error analyzing PDF:', error);
      throw new Error('Failed to analyze invoice');
    }
  }

  async generateReport(invoiceId: string): Promise<InvoiceReport> {
    try {
      const response = await axios.get(`${this.baseUrl}/api/invoices/${invoiceId}/report`);
      return response.data;
    } catch (error) {
      console.error('Error generating report:', error);
      throw new Error('Failed to generate report');
    }
  }

  async generatePDF(report: InvoiceReport): Promise<Blob> {
    try {
      const response = await axios.post(
        `${this.baseUrl}/api/reports/generate`,
        { report },
        { responseType: 'blob' }
      );
      return response.data;
    } catch (error) {
      console.error('Error generating PDF:', error);
      throw new Error('Failed to generate PDF report');
    }
  }

  async downloadPDF(url: string): Promise<Blob> {
    try {
      const response = await axios.get(url, { responseType: 'blob' });
      return response.data;
    } catch (error) {
      console.error('Error downloading PDF:', error);
      throw new Error('Failed to download PDF');
    }
  }
}

export const pdfService = new PDFService();
