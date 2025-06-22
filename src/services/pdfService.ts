import { getDashboardMetrics } from './api';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

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
  report_id: string;
  generated_date: string;
  period: string;
  executive_summary: {
    total_spend: number;
    total_invoices: number;
    avg_invoice_amount: number;
    risk_score: number;
  };
  vendor_analysis: Array<{
    vendor_name: string;
    total_spend: number;
    invoice_count: number;
    avg_rate: number;
    risk_score: number;
  }>;
  category_analysis: Array<{
    category: string;
    total_spend: number;
    percentage: number;
  }>;
  recommendations: string[];
}

export interface ComprehensiveReport {
  report_id: string;
  generated_date: string;
  timeframe: string;
  category: string;
  type: string;
  analyticsData: any;
  insights: string[];
  predictions: any;
  recommendations: string[];
}

class PDFService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_URL || '';
  }

  // Helper function to construct API URLs
  private apiUrl(path: string): string {
    return this.baseUrl ? `${this.baseUrl}${path}` : path;
  }

  async uploadAndAnalyze(file: File): Promise<PDFAnalysisResult> {
    // This would be implemented when we have actual PDF analysis capabilities
    throw new Error('PDF analysis not yet implemented - use upload invoice instead');
  }

  private generateReportData(type: string, params?: any): InvoiceReport | ComprehensiveReport {
    const reportId = `LAIT-${type.toUpperCase()}-${Date.now()}`;
    const generatedDate = new Date().toLocaleDateString();
    
    if (type === 'comprehensive') {
      return {
        report_id: reportId,
        generated_date: generatedDate,
        timeframe: params?.timeframe || '12M',
        category: params?.category || 'all',
        type: params?.type || 'comprehensive',
        analyticsData: params?.analyticsData || {},
        insights: [
          'IP litigation spend is trending 23% higher than previous year',
          'Potential savings of $425,000 identified through rate optimization',
          '3 firms account for 62% of total spend; consider diversifying vendor portfolio'
        ],
        predictions: {
          next_month_spend: { amount: 120000, trend: 'increasing', confidence: 0.85 },
          budget_risk: { level: 'medium', probability: 0.65 },
          cost_savings: { potential: 25000, opportunities: ['Rate optimization', 'Vendor consolidation'] }
        },
        recommendations: [
          'Implement rate negotiation strategies with top vendors',
          'Diversify vendor portfolio to reduce concentration risk',
          'Establish budget monitoring alerts for high-risk matters',
          'Consider alternative fee arrangements for routine legal work'
        ]
      };
    }
    
    // Default invoice report
    return {
      report_id: reportId,
      generated_date: generatedDate,
      period: 'Current Period',
      executive_summary: {
        total_spend: 5955755,
        total_invoices: 20,
        avg_invoice_amount: 297787.75,
        risk_score: 54.6
      },
      vendor_analysis: [
        {
          vendor_name: 'Latham & Watkins',
          total_spend: 1850000,
          invoice_count: 5,
          avg_rate: 850,
          risk_score: 45
        },
        {
          vendor_name: 'Skadden Arps',
          total_spend: 1200000,
          invoice_count: 4,
          avg_rate: 780,
          risk_score: 52
        },
        {
          vendor_name: 'White & Case',
          total_spend: 950000,
          invoice_count: 3,
          avg_rate: 720,
          risk_score: 48
        }
      ],
      category_analysis: [
        { category: 'Litigation', total_spend: 2500000, percentage: 42 },
        { category: 'Corporate', total_spend: 1800000, percentage: 30 },
        { category: 'IP', total_spend: 1200000, percentage: 20 },
        { category: 'Employment', total_spend: 455755, percentage: 8 }
      ],
      recommendations: [
        'Negotiate better rates with Latham & Watkins for high-volume work',
        'Consider alternative fee arrangements for routine litigation',
        'Implement stricter budget controls for IP matters',
        'Review vendor performance quarterly and adjust accordingly'
      ]
    };
  }

  async generateReport(type: string, params?: any): Promise<InvoiceReport | ComprehensiveReport> {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return this.generateReportData(type, params);
  }

  async generatePDF(report: InvoiceReport | ComprehensiveReport): Promise<Blob> {
    // Create a temporary div to render the report
    const reportDiv = document.createElement('div');
    reportDiv.style.position = 'absolute';
    reportDiv.style.left = '-9999px';
    reportDiv.style.top = '0';
    reportDiv.style.width = '800px';
    reportDiv.style.backgroundColor = 'white';
    reportDiv.style.padding = '40px';
    reportDiv.style.fontFamily = 'Arial, sans-serif';
    reportDiv.style.fontSize = '12px';
    reportDiv.style.lineHeight = '1.4';
    
    // Generate HTML content based on report type
    if ('analyticsData' in report) {
      // Comprehensive report
      reportDiv.innerHTML = this.generateComprehensiveReportHTML(report as ComprehensiveReport);
    } else {
      // Invoice report
      reportDiv.innerHTML = this.generateInvoiceReportHTML(report as InvoiceReport);
    }
    
    document.body.appendChild(reportDiv);
    
    try {
      // Convert to canvas
      const canvas = await html2canvas(reportDiv, {
        scale: 2,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff'
      });
      
      // Convert canvas to blob
      return new Promise((resolve) => {
        canvas.toBlob((blob) => {
          if (blob) {
            resolve(blob);
          } else {
            throw new Error('Failed to generate PDF blob');
          }
        }, 'application/pdf');
      });
    } finally {
      document.body.removeChild(reportDiv);
    }
  }

  private generateComprehensiveReportHTML(report: ComprehensiveReport): string {
    const analyticsData = report.analyticsData;
    
    return `
      <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
        <!-- Header -->
        <div style="text-align: center; border-bottom: 3px solid #2563eb; padding-bottom: 20px; margin-bottom: 30px;">
          <h1 style="color: #1f2937; margin: 0; font-size: 28px;">LAIT Legal Intelligence Report</h1>
          <p style="color: #6b7280; margin: 5px 0;">${report.type.toUpperCase()} - ${report.timeframe}</p>
          <p style="color: #6b7280; margin: 5px 0;">Report ID: ${report.report_id}</p>
          <p style="color: #6b7280; margin: 5px 0;">Generated: ${report.generated_date}</p>
        </div>

        <!-- Executive Summary -->
        <div style="margin-bottom: 30px;">
          <h2 style="color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">Executive Summary</h2>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
            <div style="background: #f8fafc; padding: 15px; border-radius: 8px;">
              <h3 style="margin: 0 0 10px 0; color: #374151;">Total Spend</h3>
              <p style="font-size: 24px; font-weight: bold; color: #2563eb; margin: 0;">
                $${(analyticsData.summary?.total_spend / 1000000).toFixed(1)}M
              </p>
            </div>
            <div style="background: #f8fafc; padding: 15px; border-radius: 8px;">
              <h3 style="margin: 0 0 10px 0; color: #374151;">Invoice Count</h3>
              <p style="font-size: 24px; font-weight: bold; color: #059669; margin: 0;">
                ${analyticsData.summary?.invoice_count || 0}
              </p>
            </div>
            <div style="background: #f8fafc; padding: 15px; border-radius: 8px;">
              <h3 style="margin: 0 0 10px 0; color: #374151;">Risk Score</h3>
              <p style="font-size: 24px; font-weight: bold; color: #dc2626; margin: 0;">
                ${((analyticsData.summary?.avg_risk_score || 0) * 100).toFixed(1)}%
              </p>
            </div>
            <div style="background: #f8fafc; padding: 15px; border-radius: 8px;">
              <h3 style="margin: 0 0 10px 0; color: #374151;">Active Vendors</h3>
              <p style="font-size: 24px; font-weight: bold; color: #7c3aed; margin: 0;">
                ${analyticsData.summary?.vendor_count || 0}
              </p>
            </div>
          </div>
        </div>

        <!-- AI Insights -->
        <div style="margin-bottom: 30px;">
          <h2 style="color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">AI-Generated Insights</h2>
          <div style="margin-top: 20px;">
            ${report.insights.map((insight, index) => `
              <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin-bottom: 10px; border-radius: 4px;">
                <p style="margin: 0; color: #92400e; font-weight: 500;">${insight}</p>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Predictions -->
        <div style="margin-bottom: 30px;">
          <h2 style="color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">Predictive Analytics</h2>
          <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 20px;">
            <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; border: 1px solid #0ea5e9;">
              <h3 style="margin: 0 0 10px 0; color: #0c4a6e;">Next Month Forecast</h3>
              <p style="font-size: 20px; font-weight: bold; color: #0ea5e9; margin: 5px 0;">
                $${report.predictions.next_month_spend.amount.toLocaleString()}
              </p>
              <p style="margin: 5px 0; color: #64748b;">
                Trend: ${report.predictions.next_month_spend.trend}
              </p>
              <p style="margin: 5px 0; color: #64748b;">
                Confidence: ${(report.predictions.next_month_spend.confidence * 100).toFixed(0)}%
              </p>
            </div>
            <div style="background: #fef3c7; padding: 15px; border-radius: 8px; border: 1px solid #f59e0b;">
              <h3 style="margin: 0 0 10px 0; color: #92400e;">Budget Risk</h3>
              <p style="font-size: 20px; font-weight: bold; color: #f59e0b; margin: 5px 0;">
                ${report.predictions.budget_risk.level.toUpperCase()}
              </p>
              <p style="margin: 5px 0; color: #64748b;">
                Probability: ${(report.predictions.budget_risk.probability * 100).toFixed(0)}%
              </p>
            </div>
            <div style="background: #f0fdf4; padding: 15px; border-radius: 8px; border: 1px solid #22c55e;">
              <h3 style="margin: 0 0 10px 0; color: #166534;">Savings Potential</h3>
              <p style="font-size: 20px; font-weight: bold; color: #22c55e; margin: 5px 0;">
                $${report.predictions.cost_savings.potential.toLocaleString()}
              </p>
              <p style="margin: 5px 0; color: #64748b;">
                ${report.predictions.cost_savings.opportunities.length} opportunities identified
              </p>
            </div>
          </div>
        </div>

        <!-- Recommendations -->
        <div style="margin-bottom: 30px;">
          <h2 style="color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">Strategic Recommendations</h2>
          <div style="margin-top: 20px;">
            ${report.recommendations.map((rec, index) => `
              <div style="background: #f8fafc; padding: 12px; margin-bottom: 8px; border-radius: 4px; border-left: 3px solid #2563eb;">
                <p style="margin: 0; color: #374151;">
                  <strong>${index + 1}.</strong> ${rec}
                </p>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Footer -->
        <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280;">
          <p style="margin: 0;">Generated by LAIT Legal Intelligence Platform</p>
          <p style="margin: 5px 0;">Powered by AI/ML Models and Real-time Data</p>
        </div>
      </div>
    `;
  }

  private generateInvoiceReportHTML(report: InvoiceReport): string {
    return `
      <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
        <!-- Header -->
        <div style="text-align: center; border-bottom: 3px solid #2563eb; padding-bottom: 20px; margin-bottom: 30px;">
          <h1 style="color: #1f2937; margin: 0; font-size: 28px;">Legal Spend Analysis Report</h1>
          <p style="color: #6b7280; margin: 5px 0;">Report ID: ${report.report_id}</p>
          <p style="color: #6b7280; margin: 5px 0;">Period: ${report.period}</p>
          <p style="color: #6b7280; margin: 5px 0;">Generated: ${report.generated_date}</p>
        </div>

        <!-- Executive Summary -->
        <div style="margin-bottom: 30px;">
          <h2 style="color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">Executive Summary</h2>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
            <div style="background: #f8fafc; padding: 15px; border-radius: 8px;">
              <h3 style="margin: 0 0 10px 0; color: #374151;">Total Spend</h3>
              <p style="font-size: 24px; font-weight: bold; color: #2563eb; margin: 0;">
                $${report.executive_summary.total_spend.toLocaleString()}
              </p>
            </div>
            <div style="background: #f8fafc; padding: 15px; border-radius: 8px;">
              <h3 style="margin: 0 0 10px 0; color: #374151;">Total Invoices</h3>
              <p style="font-size: 24px; font-weight: bold; color: #059669; margin: 0;">
                ${report.executive_summary.total_invoices}
              </p>
            </div>
            <div style="background: #f8fafc; padding: 15px; border-radius: 8px;">
              <h3 style="margin: 0 0 10px 0; color: #374151;">Avg Invoice Amount</h3>
              <p style="font-size: 24px; font-weight: bold; color: #dc2626; margin: 0;">
                $${report.executive_summary.avg_invoice_amount.toLocaleString()}
              </p>
            </div>
            <div style="background: #f8fafc; padding: 15px; border-radius: 8px;">
              <h3 style="margin: 0 0 10px 0; color: #374151;">Risk Score</h3>
              <p style="font-size: 24px; font-weight: bold; color: #7c3aed; margin: 0;">
                ${report.executive_summary.risk_score}%
              </p>
            </div>
          </div>
        </div>

        <!-- Vendor Analysis -->
        <div style="margin-bottom: 30px;">
          <h2 style="color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">Vendor Analysis</h2>
          <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            <thead>
              <tr style="background: #f3f4f6;">
                <th style="border: 1px solid #d1d5db; padding: 12px; text-align: left;">Vendor</th>
                <th style="border: 1px solid #d1d5db; padding: 12px; text-align: right;">Total Spend</th>
                <th style="border: 1px solid #d1d5db; padding: 12px; text-align: center;">Invoices</th>
                <th style="border: 1px solid #d1d5db; padding: 12px; text-align: right;">Avg Rate</th>
                <th style="border: 1px solid #d1d5db; padding: 12px; text-align: center;">Risk Score</th>
              </tr>
            </thead>
            <tbody>
              ${report.vendor_analysis.map(vendor => `
                <tr>
                  <td style="border: 1px solid #d1d5db; padding: 12px;">${vendor.vendor_name}</td>
                  <td style="border: 1px solid #d1d5db; padding: 12px; text-align: right;">$${vendor.total_spend.toLocaleString()}</td>
                  <td style="border: 1px solid #d1d5db; padding: 12px; text-align: center;">${vendor.invoice_count}</td>
                  <td style="border: 1px solid #d1d5db; padding: 12px; text-align: right;">$${vendor.avg_rate}</td>
                  <td style="border: 1px solid #d1d5db; padding: 12px; text-align: center;">${vendor.risk_score}%</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        <!-- Category Analysis -->
        <div style="margin-bottom: 30px;">
          <h2 style="color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">Category Analysis</h2>
          <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            <thead>
              <tr style="background: #f3f4f6;">
                <th style="border: 1px solid #d1d5db; padding: 12px; text-align: left;">Category</th>
                <th style="border: 1px solid #d1d5db; padding: 12px; text-align: right;">Total Spend</th>
                <th style="border: 1px solid #d1d5db; padding: 12px; text-align: center;">Percentage</th>
              </tr>
            </thead>
            <tbody>
              ${report.category_analysis.map(category => `
                <tr>
                  <td style="border: 1px solid #d1d5db; padding: 12px;">${category.category}</td>
                  <td style="border: 1px solid #d1d5db; padding: 12px; text-align: right;">$${category.total_spend.toLocaleString()}</td>
                  <td style="border: 1px solid #d1d5db; padding: 12px; text-align: center;">${category.percentage}%</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        <!-- Recommendations -->
        <div style="margin-bottom: 30px;">
          <h2 style="color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">Recommendations</h2>
          <div style="margin-top: 20px;">
            ${report.recommendations.map((rec, index) => `
              <div style="background: #f8fafc; padding: 12px; margin-bottom: 8px; border-radius: 4px; border-left: 3px solid #2563eb;">
                <p style="margin: 0; color: #374151;">
                  <strong>${index + 1}.</strong> ${rec}
                </p>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Footer -->
        <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280;">
          <p style="margin: 0;">Generated by LAIT Legal Intelligence Platform</p>
          <p style="margin: 5px 0;">Powered by AI/ML Models and Real-time Data</p>
        </div>
      </div>
    `;
  }

  async downloadPDF(url: string): Promise<Blob> {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
      }
      return await response.blob();
    } catch (error) {
      console.error('Error downloading PDF:', error);
      throw new Error('Failed to download PDF');
    }
  }
}

export const pdfService = new PDFService();
