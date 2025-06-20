import { getDashboardMetrics } from './api';

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
    high_risk_invoices: number;
    risk_percentage: number;
    top_vendor: string;
    cost_savings_opportunities: number;
  };
  vendor_analysis: Array<{
    vendor: string;
    total_spend: number;
    invoice_count: number;
    avg_invoice_amount: number;
    avg_risk_score: number;
    performance_grade: string;
    recommendations: string[];
  }>;
  category_analysis: Array<{
    category: string;
    total_spend: number;
    invoice_count: number;
    percentage_of_total: number;
  }>;
  risk_analysis: {
    total_risk_factors: number;
    avg_risk_score: number;
    high_risk_invoices: Array<{
      id: string;
      vendor: string;
      amount: number;
      risk_score: number;
      reason: string;
    }>;
  };
  recommendations: string[];
}

class PDFService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:5003';
  }

  async uploadAndAnalyze(file: File): Promise<PDFAnalysisResult> {
    // This would be implemented when we have actual PDF analysis capabilities
    throw new Error('PDF analysis not yet implemented - use upload invoice instead');
  }

  async generateReport(period: string = 'current'): Promise<InvoiceReport> {
    try {
      console.log('Generating report from:', `${this.baseUrl}/api/reports/generate`);
      
      const response = await fetch(`${this.baseUrl}/api/reports/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ period }),
      });

      if (!response.ok) {
        throw new Error(`Report generation failed: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Report generated successfully:', data);
      return data;
    } catch (error) {
      console.error('Error generating report:', error);
      throw new Error(`Failed to generate report: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async generatePDF(report: InvoiceReport): Promise<Blob> {
    try {
      // Generate HTML content for the PDF
      const htmlContent = this.generateHTMLReport(report);
      
      // Convert HTML to PDF using a simple approach
      // In a real implementation, you might use a PDF library or service
      const blob = new Blob([htmlContent], { type: 'text/html' });
      
      console.log('PDF blob generated successfully');
      return blob;
    } catch (error) {
      console.error('Error generating PDF:', error);
      throw new Error('Failed to generate PDF report');
    }
  }

  private generateHTMLReport(report: InvoiceReport): string {
    return `
<!DOCTYPE html>
<html>
<head>
    <title>LAIT Legal Spend Report - ${report.report_id}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
        .section { margin-bottom: 30px; }
        .section h2 { color: #333; border-bottom: 1px solid #ccc; padding-bottom: 10px; }
        .metric { display: inline-block; margin: 10px 20px; text-align: center; }
        .metric .value { font-size: 24px; font-weight: bold; color: #007bff; }
        .metric .label { font-size: 12px; color: #666; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f5f5f5; }
        .risk-high { color: #dc3545; }
        .risk-medium { color: #ffc107; }
        .risk-low { color: #28a745; }
        .recommendations { background-color: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; }
        .recommendations ul { margin: 0; padding-left: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Legal Spend Analysis Report</h1>
        <p>Report ID: ${report.report_id}</p>
        <p>Generated: ${report.generated_date} | Period: ${report.period}</p>
    </div>

    <div class="section">
        <h2>Executive Summary</h2>
        <div class="metric">
            <div class="value">$${report.executive_summary.total_spend.toLocaleString()}</div>
            <div class="label">Total Spend</div>
        </div>
        <div class="metric">
            <div class="value">${report.executive_summary.total_invoices}</div>
            <div class="label">Total Invoices</div>
        </div>
        <div class="metric">
            <div class="value">$${Math.round(report.executive_summary.avg_invoice_amount).toLocaleString()}</div>
            <div class="label">Avg Invoice Amount</div>
        </div>
        <div class="metric">
            <div class="value">${report.executive_summary.high_risk_invoices}</div>
            <div class="label">High Risk Invoices</div>
        </div>
        <div class="metric">
            <div class="value">${report.executive_summary.risk_percentage}%</div>
            <div class="label">Risk Percentage</div>
        </div>
        <div class="metric">
            <div class="value">$${Math.round(report.executive_summary.cost_savings_opportunities).toLocaleString()}</div>
            <div class="label">Savings Opportunity</div>
        </div>
    </div>

    <div class="section">
        <h2>Vendor Performance Analysis</h2>
        <table>
            <tr>
                <th>Vendor</th>
                <th>Total Spend</th>
                <th>Invoices</th>
                <th>Avg Amount</th>
                <th>Risk Score</th>
                <th>Grade</th>
                <th>Recommendations</th>
            </tr>
            ${report.vendor_analysis.map(vendor => `
            <tr>
                <td>${vendor.vendor}</td>
                <td>$${vendor.total_spend.toLocaleString()}</td>
                <td>${vendor.invoice_count}</td>
                <td>$${Math.round(vendor.avg_invoice_amount).toLocaleString()}</td>
                <td class="risk-${vendor.avg_risk_score > 70 ? 'high' : vendor.avg_risk_score > 40 ? 'medium' : 'low'}">${vendor.avg_risk_score}</td>
                <td>${vendor.performance_grade}</td>
                <td>${vendor.recommendations.join('; ')}</td>
            </tr>
            `).join('')}
        </table>
    </div>

    <div class="section">
        <h2>Category Breakdown</h2>
        <table>
            <tr>
                <th>Category</th>
                <th>Total Spend</th>
                <th>Invoice Count</th>
                <th>% of Total</th>
            </tr>
            ${report.category_analysis.map(category => `
            <tr>
                <td>${category.category}</td>
                <td>$${category.total_spend.toLocaleString()}</td>
                <td>${category.invoice_count}</td>
                <td>${category.percentage_of_total}%</td>
            </tr>
            `).join('')}
        </table>
    </div>

    <div class="section">
        <h2>Risk Analysis</h2>
        <p><strong>Average Risk Score:</strong> ${report.risk_analysis.avg_risk_score}</p>
        <p><strong>Total Risk Factors:</strong> ${report.risk_analysis.total_risk_factors}</p>
        
        ${report.risk_analysis.high_risk_invoices.length > 0 ? `
        <h3>High Risk Invoices</h3>
        <table>
            <tr>
                <th>Invoice ID</th>
                <th>Vendor</th>
                <th>Amount</th>
                <th>Risk Score</th>
                <th>Reason</th>
            </tr>
            ${report.risk_analysis.high_risk_invoices.map(invoice => `
            <tr>
                <td>${invoice.id}</td>
                <td>${invoice.vendor}</td>
                <td>$${invoice.amount.toLocaleString()}</td>
                <td class="risk-high">${invoice.risk_score}</td>
                <td>${invoice.reason}</td>
            </tr>
            `).join('')}
        </table>
        ` : '<p>No high-risk invoices identified.</p>'}
    </div>

    <div class="section recommendations">
        <h2>Recommendations</h2>
        <ul>
            ${report.recommendations.map(rec => `<li>${rec}</li>`).join('')}
        </ul>
    </div>

    <div style="margin-top: 50px; text-align: center; font-size: 12px; color: #666;">
        <p>Generated by LAIT (Legal AI Technology) - Legal Spend Optimization Platform</p>
        <p>This report is confidential and intended for internal use only.</p>
    </div>
</body>
</html>
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
