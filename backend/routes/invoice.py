from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import PyPDF2
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime
import pdfplumber
import io
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

invoice_bp = Blueprint('invoice', __name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def analyze_pdf(filepath):
    with pdfplumber.open(filepath) as pdf:
        text = ""
        tables = []
        for page in pdf.pages:
            text += page.extract_text()
            tables.extend(page.extract_tables())
        
        # Extract invoice details
        invoice_data = {
            'vendor': extract_vendor(text),
            'amount': extract_amount(text),
            'date': extract_date(text),
            'lineItems': extract_line_items(tables),
        }
        
        # Calculate risk score and factors
        risk_analysis = analyze_risk(invoice_data)
        invoice_data.update(risk_analysis)
        
        # Add benchmarking data
        invoice_data.update(get_benchmarks(invoice_data))
        
        return invoice_data

def extract_vendor(text):
    # Implement vendor name extraction logic
    # This would use regex or NLP to find company names
    return "Sample Vendor"

def extract_amount(text):
    # Implement amount extraction logic
    # This would use regex to find currency amounts
    return 1000.00

def extract_date(text):
    # Implement date extraction logic
    return datetime.now().strftime("%Y-%m-%d")

def extract_line_items(tables):
    # Implement line item extraction logic
    # This would parse tables to find hours, rates, and descriptions
    return [
        {
            "description": "Legal research",
            "hours": 2.5,
            "rate": 300.00,
            "total": 750.00
        }
    ]

def analyze_risk(invoice_data):
    # Implement risk analysis
    # This would use historical data and ML models to detect anomalies
    return {
        "riskScore": 35,
        "riskFactors": [
            {
                "type": "rate_anomaly",
                "description": "Hourly rate 15% above market average",
                "severity": "medium"
            }
        ]
    }

def get_benchmarks(invoice_data):
    # Implement benchmarking logic
    # This would compare against industry averages
    return {
        "benchmarks": {
            "rateComparison": {
                "avgMarketRate": 285.00,
                "percentDiff": 5.26
            },
            "hoursComparison": {
                "avgMarketHours": 2.3,
                "percentDiff": 8.70
            }
        }
    }

def generate_report_pdf(report_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    story.append(Paragraph("Invoice Analysis Report", title_style))
    story.append(Spacer(1, 12))

    # Summary Section
    story.append(Paragraph("Summary", styles['Heading2']))
    summary_data = [
        ["Total Amount", f"${report_data['summary']['totalAmount']:,.2f}"],
        ["Total Hours", f"{report_data['summary']['totalHours']}"],
        ["Average Rate", f"${report_data['summary']['avgRate']:,.2f}"],
        ["Risk Score", f"{report_data['summary']['riskScore']}%"]
    ]
    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # Analysis Section
    story.append(Paragraph("Analysis", styles['Heading2']))
    for section in ['rateAnalysis', 'timeAnalysis']:
        story.append(Paragraph(section.replace('Analysis', ' Analysis'), styles['Heading3']))
        # Add analysis details here
        story.append(Spacer(1, 12))

    # Recommendations
    story.append(Paragraph("Recommendations", styles['Heading2']))
    for rec in report_data['analysis']['recommendations']:
        story.append(Paragraph(
            f"• {rec['description']} (Priority: {rec['priority']}, "
            f"Potential Savings: ${rec['potentialSavings']:,.2f})",
            styles['Normal']
        ))
        story.append(Spacer(1, 6))

    # Historical Analysis
    story.append(Paragraph("Historical Analysis", styles['Heading2']))
    for trend in report_data['historical']['trends']:
        story.append(Paragraph(
            f"• {trend['metric']}: {trend['change']}% - {trend['interpretation']}",
            styles['Normal']
        ))

    doc.build(story)
    buffer.seek(0)
    return buffer

@invoice_bp.route('/api/invoices/analyze', methods=['POST'])
def analyze_invoice():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            analysis_result = analyze_pdf(filepath)
            os.remove(filepath)  # Clean up
            return jsonify(analysis_result)
        except Exception as e:
            os.remove(filepath)  # Clean up
            return jsonify({'error': str(e)}), 500

@invoice_bp.route('/api/invoices/<invoice_id>/report', methods=['GET'])
def get_invoice_report(invoice_id):
    # In a real app, this would fetch the invoice data from a database
    mock_report = {
        'id': invoice_id,
        'summary': {
            'totalAmount': 10000.00,
            'totalHours': 35.5,
            'avgRate': 285.00,
            'riskScore': 35
        },
        'analysis': {
            'rateAnalysis': {
                'marketComparison': -5,
                'historicalTrend': 2,
                'outliers': [
                    {
                        'timekeeper': 'John Doe',
                        'rate': 350.00,
                        'marketRate': 300.00
                    }
                ]
            },
            'timeAnalysis': {
                'efficiency': 85,
                'duplicateWork': [
                    {
                        'description': 'Document review',
                        'hours': 4.5,
                        'timekeepers': ['John Doe', 'Jane Smith']
                    }
                ],
                'blockBilling': [
                    {
                        'description': 'Research and drafting',
                        'hours': 8.0
                    }
                ]
            },
            'recommendations': [
                {
                    'type': 'rate_optimization',
                    'description': 'Consider rate negotiation for senior associates',
                    'potentialSavings': 1500.00,
                    'priority': 'high'
                }
            ]
        },
        'historical': {
            'monthlyTotals': [
                {'month': '2023-01', 'amount': 9500.00},
                {'month': '2023-02', 'amount': 10000.00}
            ],
            'yearOverYear': [
                {'year': '2022', 'amount': 110000.00},
                {'year': '2023', 'amount': 115000.00}
            ],
            'trends': [
                {
                    'metric': 'Average Rate',
                    'change': 5,
                    'interpretation': 'Gradual increase within market norms'
                }
            ]
        }
    }
    
    return jsonify(mock_report)

@invoice_bp.route('/api/reports/generate', methods=['POST'])
def generate_report():
    report_data = request.json.get('report')
    if not report_data:
        return jsonify({'error': 'No report data provided'}), 400
    
    try:
        pdf_buffer = generate_report_pdf(report_data)
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'invoice_analysis_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
