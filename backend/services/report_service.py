import os
import io
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from db.database import get_db_session, Invoice, Vendor, LineItem, RiskFactor, Matter
from sqlalchemy import func, desc, asc, and_

class ReportService:
    """Service for generating reports on legal spend data"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'Title',
            parent=self.styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        self.heading_style = ParagraphStyle(
            'Heading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=10
        )
        self.normal_style = self.styles['Normal']
        
    def generate_monthly_report(self):
        """Generate monthly spend analysis report"""
        session = get_db_session()
        try:
            # Define time range for report (previous month)
            today = datetime.now().date()
            first_day_current_month = datetime(today.year, today.month, 1)
            last_day_previous_month = first_day_current_month - timedelta(days=1)
            first_day_previous_month = datetime(last_day_previous_month.year, last_day_previous_month.month, 1)
            
            # Format dates for display
            report_month = first_day_previous_month.strftime("%B %Y")
            
            # Get spend summary
            total_spend = self._get_total_spend(session, first_day_previous_month, last_day_previous_month)
            previous_month_spend = self._get_total_spend(
                session, 
                first_day_previous_month - timedelta(days=31), 
                first_day_previous_month - timedelta(days=1)
            )
            
            # Calculate change percentages
            if previous_month_spend > 0:
                spend_change_pct = ((total_spend - previous_month_spend) / previous_month_spend) * 100
            else:
                spend_change_pct = 0
                
            # Get top vendors by spend
            top_vendors = self._get_top_vendors(session, first_day_previous_month, last_day_previous_month)
            
            # Get top matters by spend
            top_matters = self._get_top_matters(session, first_day_previous_month, last_day_previous_month)
            
            # Get hourly rate analysis
            hourly_rate_stats = self._get_hourly_rate_analysis(session, first_day_previous_month, last_day_previous_month)
            
            # Get risk factor summary
            risk_summary = self._get_risk_summary(session, first_day_previous_month, last_day_previous_month)
            
            # Generate report data
            report_data = {
                'title': f'Legal Spend Analysis Report: {report_month}',
                'generated_date': today.strftime("%Y-%m-%d"),
                'period': {
                    'start': first_day_previous_month.strftime("%Y-%m-%d"),
                    'end': last_day_previous_month.strftime("%Y-%m-%d")
                },
                'summary': {
                    'total_spend': total_spend,
                    'previous_period_spend': previous_month_spend,
                    'change_percentage': spend_change_pct,
                    'invoices_count': self._get_invoice_count(session, first_day_previous_month, last_day_previous_month),
                    'avg_invoice_amount': self._get_avg_invoice_amount(session, first_day_previous_month, last_day_previous_month)
                },
                'top_vendors': top_vendors,
                'top_matters': top_matters,
                'hourly_rates': hourly_rate_stats,
                'risk_summary': risk_summary,
                'charts': self._generate_chart_data(session, first_day_previous_month, last_day_previous_month)
            }
            
            return report_data
            
        finally:
            session.close()
            
    def generate_pdf_report(self, report_data):
        """Generate PDF report from report data"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Title
        elements.append(Paragraph(report_data['title'], self.title_style))
        elements.append(Paragraph(f"Generated: {report_data['generated_date']}", self.normal_style))
        elements.append(Paragraph(f"Period: {report_data['period']['start']} to {report_data['period']['end']}", self.normal_style))
        elements.append(Spacer(1, 20))
        
        # Summary section
        elements.append(Paragraph("Executive Summary", self.heading_style))
        elements.append(Paragraph(f"Total Legal Spend: ${report_data['summary']['total_spend']:,.2f}", self.normal_style))
        
        change_txt = f"Change from previous period: {report_data['summary']['change_percentage']:+.2f}%"
        elements.append(Paragraph(change_txt, self.normal_style))
        
        elements.append(Paragraph(f"Invoices Processed: {report_data['summary']['invoices_count']}", self.normal_style))
        elements.append(Paragraph(f"Average Invoice Amount: ${report_data['summary']['avg_invoice_amount']:,.2f}", self.normal_style))
        
        elements.append(Spacer(1, 20))
        
        # Top vendors section
        elements.append(Paragraph("Top Vendors by Spend", self.heading_style))
        vendor_data = [['Vendor', 'Spend', '% of Total']]
        for vendor in report_data['top_vendors']:
            vendor_data.append([
                vendor['name'],
                f"${vendor['spend']:,.2f}",
                f"{vendor['percentage']:.2f}%"
            ])
            
        vendor_table = Table(vendor_data, colWidths=[250, 100, 100])
        vendor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(vendor_table)
        elements.append(Spacer(1, 20))
        
        # Generate charts
        if 'charts' in report_data:
            for chart_data in report_data['charts']:
                # Here we would generate the chart image and add it to elements
                # For sake of implementation, we'd add a placeholder paragraph
                elements.append(Paragraph(f"Chart: {chart_data['title']}", self.normal_style))
                elements.append(Spacer(1, 10))
        
        # Risk summary
        elements.append(Paragraph("Risk Analysis", self.heading_style))
        risk_data = [['Risk Factor', 'Count', 'Impact']]
        for risk in report_data['risk_summary']:
            risk_data.append([
                risk['factor_type'],
                risk['count'],
                risk['severity']
            ])
            
        risk_table = Table(risk_data, colWidths=[250, 100, 100])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(risk_table)
        
        # Build PDF
        doc.build(elements)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
    
    def _get_total_spend(self, session, start_date, end_date):
        """Get total spend for the given period"""
        total = session.query(func.sum(Invoice.amount))\
            .filter(Invoice.date >= start_date, Invoice.date <= end_date)\
            .scalar()
        return total or 0
    
    def _get_invoice_count(self, session, start_date, end_date):
        """Get count of invoices for the given period"""
        count = session.query(func.count(Invoice.id))\
            .filter(Invoice.date >= start_date, Invoice.date <= end_date)\
            .scalar()
        return count or 0
    
    def _get_avg_invoice_amount(self, session, start_date, end_date):
        """Get average invoice amount for the given period"""
        avg = session.query(func.avg(Invoice.amount))\
            .filter(Invoice.date >= start_date, Invoice.date <= end_date)\
            .scalar()
        return avg or 0
    
    def _get_top_vendors(self, session, start_date, end_date, limit=5):
        """Get top vendors by spend for the given period"""
        total_spend = self._get_total_spend(session, start_date, end_date)
        
        result = session.query(
            Vendor.name,
            func.sum(Invoice.amount).label('total_spend')
        ).join(Invoice, Invoice.vendor_id == Vendor.id)\
         .filter(Invoice.date >= start_date, Invoice.date <= end_date)\
         .group_by(Vendor.name)\
         .order_by(desc('total_spend'))\
         .limit(limit)\
         .all()
         
        vendors = []
        for row in result:
            spend = row.total_spend or 0
            percentage = (spend / total_spend * 100) if total_spend > 0 else 0
            vendors.append({
                'name': row.name,
                'spend': spend,
                'percentage': percentage
            })
            
        return vendors
        
    def _get_top_matters(self, session, start_date, end_date, limit=5):
        """Get top matters by spend for the given period"""
        result = session.query(
            Matter.name,
            func.sum(Invoice.amount).label('total_spend')
        ).join(Invoice, Invoice.matter_id == Matter.id)\
         .filter(Invoice.date >= start_date, Invoice.date <= end_date)\
         .group_by(Matter.name)\
         .order_by(desc('total_spend'))\
         .limit(limit)\
         .all()
         
        matters = []
        for row in result:
            matters.append({
                'name': row.name,
                'spend': row.total_spend or 0
            })
            
        return matters
    
    def _get_hourly_rate_analysis(self, session, start_date, end_date):
        """Get hourly rate analysis for the given period"""
        result = session.query(
            func.avg(LineItem.rate).label('avg_rate'),
            func.min(LineItem.rate).label('min_rate'),
            func.max(LineItem.rate).label('max_rate')
        ).join(Invoice, LineItem.invoice_id == Invoice.id)\
         .filter(Invoice.date >= start_date, Invoice.date <= end_date)\
         .one()
         
        return {
            'avg_rate': result.avg_rate or 0,
            'min_rate': result.min_rate or 0,
            'max_rate': result.max_rate or 0
        }
    
    def _get_risk_summary(self, session, start_date, end_date):
        """Get risk factor summary for the given period"""
        result = session.query(
            RiskFactor.factor_type,
            func.count(RiskFactor.id).label('count'),
            func.avg(RiskFactor.impact_score).label('avg_impact')
        ).join(Invoice, RiskFactor.invoice_id == Invoice.id)\
         .filter(Invoice.date >= start_date, Invoice.date <= end_date)\
         .group_by(RiskFactor.factor_type)\
         .order_by(desc('count'))\
         .all()
         
        risk_summary = []
        for row in result:
            impact_score = row.avg_impact or 0
            severity = 'Low'
            if impact_score >= 7:
                severity = 'High'
            elif impact_score >= 4:
                severity = 'Medium'
                
            risk_summary.append({
                'factor_type': row.factor_type,
                'count': row.count,
                'impact_score': impact_score,
                'severity': severity
            })
            
        return risk_summary
    
    def _generate_chart_data(self, session, start_date, end_date):
        """Generate chart data for the report"""
        # In a real implementation, we would generate actual charts here
        # For this implementation, we'll just return the chart data
        
        # Spend by vendor chart data
        vendor_data = self._get_top_vendors(session, start_date, end_date, limit=5)
        
        # Spend by matter chart data
        matter_data = self._get_top_matters(session, start_date, end_date, limit=5)
        
        return [
            {
                'title': 'Spend by Vendor',
                'type': 'pie',
                'data': vendor_data
            },
            {
                'title': 'Spend by Matter',
                'type': 'bar',
                'data': matter_data
            }
        ]
