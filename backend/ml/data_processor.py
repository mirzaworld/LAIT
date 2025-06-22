#!/usr/bin/env python3
"""
ML Data Processing Pipeline for LAIT
Converts real invoice data into processable format for ML models
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class InvoiceDataProcessor:
    """Processes invoice data for ML model consumption"""
    
    def __init__(self):
        self.feature_columns = [
            'amount', 'hours', 'rate', 'vendor_risk_profile',
            'practice_area_encoded', 'time_since_last_invoice',
            'amount_vs_avg', 'rate_vs_avg', 'hours_per_dollar',
            'vendor_invoice_count', 'matter_budget_ratio'
        ]
    
    def process_invoice_data(self, session: Session) -> pd.DataFrame:
        """
        Convert raw invoice data into ML-ready features
        """
        try:
            from db.database import Invoice, Vendor, Matter
            
            # Get all invoices with related data
            invoices_query = session.query(Invoice)\
                .join(Vendor, Invoice.vendor_id == Vendor.id, isouter=True)\
                .join(Matter, Invoice.matter_id == Matter.id, isouter=True)\
                .all()
            
            if not invoices_query:
                logger.warning("No invoice data found for processing")
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = []
            for invoice in invoices_query:
                row = {
                    'id': invoice.id,
                    'amount': float(invoice.amount) if invoice.amount else 0,
                    'hours': float(invoice.total_hours) if invoice.total_hours else 0,
                    'rate': float(invoice.rate) if invoice.rate else 0,
                    'vendor_id': invoice.vendor_id,
                    'vendor_name': invoice.vendor.name if invoice.vendor else 'Unknown',
                    'vendor_risk_profile': float(invoice.vendor.risk_profile) if invoice.vendor and invoice.vendor.risk_profile else 0.5,
                    'practice_area': invoice.practice_area or 'General',
                    'matter_id': invoice.matter_id,
                    'matter_budget': float(invoice.matter.budget) if invoice.matter and invoice.matter.budget else 0,
                    'date': invoice.date,
                    'current_risk_score': float(invoice.risk_score) if invoice.risk_score else 0,
                    'status': invoice.status or 'pending'
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Generate engineered features
            df = self._engineer_features(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing invoice data: {str(e)}")
            return pd.DataFrame()
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create engineered features for ML models
        """
        try:
            # Handle missing values
            df = df.fillna({
                'amount': 0,
                'hours': 0,
                'rate': 0,
                'vendor_risk_profile': 0.5,
                'matter_budget': 0
            })
            
            # Encode practice areas
            practice_areas = df['practice_area'].unique()
            practice_area_map = {area: i for i, area in enumerate(practice_areas)}
            df['practice_area_encoded'] = df['practice_area'].map(practice_area_map)
            
            # Time-based features
            if 'date' in df.columns and not df['date'].isna().all():
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                
                # Time since last invoice for each vendor
                df['time_since_last_invoice'] = df.groupby('vendor_id')['date'].diff().dt.days.fillna(0)
            else:
                df['time_since_last_invoice'] = 0
            
            # Amount-based features
            vendor_avg_amount = df.groupby('vendor_id')['amount'].mean()
            df['amount_vs_avg'] = df.apply(
                lambda row: row['amount'] / vendor_avg_amount.get(row['vendor_id'], 1) if vendor_avg_amount.get(row['vendor_id'], 0) > 0 else 1,
                axis=1
            )
            
            # Rate-based features
            vendor_avg_rate = df.groupby('vendor_id')['rate'].mean()
            df['rate_vs_avg'] = df.apply(
                lambda row: row['rate'] / vendor_avg_rate.get(row['vendor_id'], 1) if vendor_avg_rate.get(row['vendor_id'], 0) > 0 else 1,
                axis=1
            )
            
            # Efficiency features
            df['hours_per_dollar'] = df.apply(
                lambda row: row['hours'] / row['amount'] if row['amount'] > 0 else 0,
                axis=1
            )
            
            # Vendor history features
            vendor_counts = df.groupby('vendor_id').size()
            df['vendor_invoice_count'] = df['vendor_id'].map(vendor_counts)
            
            # Matter budget ratio
            df['matter_budget_ratio'] = df.apply(
                lambda row: row['amount'] / row['matter_budget'] if row['matter_budget'] > 0 else 0,
                axis=1
            )
            
            # Risk indicators (binary features)
            df['is_high_amount'] = (df['amount'] > df['amount'].quantile(0.8)).astype(int)
            df['is_high_rate'] = (df['rate'] > df['rate'].quantile(0.8)).astype(int)
            df['is_weekend_submission'] = 0  # Would need actual submission date
            
            # Anomaly detection features
            df['amount_zscore'] = np.abs((df['amount'] - df['amount'].mean()) / df['amount'].std())
            df['rate_zscore'] = np.abs((df['rate'] - df['rate'].mean()) / df['rate'].std())
            
            return df
            
        except Exception as e:
            logger.error(f"Error engineering features: {str(e)}")
            return df
    
    def prepare_risk_prediction_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for risk prediction model
        """
        try:
            # Select features for risk prediction
            feature_cols = [col for col in self.feature_columns if col in df.columns]
            
            if not feature_cols:
                logger.warning("No feature columns found for risk prediction")
                return np.array([]), np.array([])
            
            X = df[feature_cols].fillna(0).values
            
            # Create target variable (high risk = risk_score > 0.7)
            if 'current_risk_score' in df.columns:
                y = (df['current_risk_score'] > 0.7).astype(int).values
            else:
                # If no existing risk scores, create based on anomalies
                y = ((df.get('amount_zscore', 0) > 2) | 
                     (df.get('rate_zscore', 0) > 2) |
                     (df.get('matter_budget_ratio', 0) > 0.5)).astype(int).values
            
            return X, y
            
        except Exception as e:
            logger.error(f"Error preparing risk prediction data: {str(e)}")
            return np.array([]), np.array([])
    
    def prepare_vendor_performance_data(self, df: pd.DataFrame) -> Dict:
        """
        Prepare data for vendor performance analysis
        """
        try:
            vendor_metrics = {}
            
            for vendor_id in df['vendor_id'].unique():
                if pd.isna(vendor_id):
                    continue
                    
                vendor_data = df[df['vendor_id'] == vendor_id]
                
                metrics = {
                    'total_spend': vendor_data['amount'].sum(),
                    'invoice_count': len(vendor_data),
                    'avg_rate': vendor_data['rate'].mean(),
                    'avg_amount': vendor_data['amount'].mean(),
                    'avg_risk_score': vendor_data['current_risk_score'].mean(),
                    'high_risk_percentage': (vendor_data['current_risk_score'] > 0.7).mean() * 100,
                    'practice_area_diversity': vendor_data['practice_area'].nunique(),
                    'consistency_score': 1 - vendor_data['amount'].std() / vendor_data['amount'].mean() if vendor_data['amount'].mean() > 0 else 0
                }
                
                vendor_metrics[vendor_id] = metrics
            
            return vendor_metrics
            
        except Exception as e:
            logger.error(f"Error preparing vendor performance data: {str(e)}")
            return {}
    
    def calculate_spend_trends(self, df: pd.DataFrame, period: str = 'monthly') -> Dict:
        """
        Calculate spending trends over time
        """
        try:
            if 'date' not in df.columns or df['date'].isna().all():
                return {'labels': [], 'data': []}
            
            df['date'] = pd.to_datetime(df['date'])
            
            if period == 'monthly':
                df['period'] = df['date'].dt.to_period('M')
            elif period == 'quarterly':
                df['period'] = df['date'].dt.to_period('Q')
            else:  # weekly
                df['period'] = df['date'].dt.to_period('W')
            
            trend_data = df.groupby('period')['amount'].sum().reset_index()
            trend_data['period_str'] = trend_data['period'].astype(str)
            
            return {
                'labels': trend_data['period_str'].tolist(),
                'data': trend_data['amount'].tolist()
            }
            
        except Exception as e:
            logger.error(f"Error calculating spend trends: {str(e)}")
            return {'labels': [], 'data': []}

class VendorDataProcessor:
    """Processes vendor data for performance analysis"""
    
    def update_vendor_metrics(self, session: Session):
        """
        Update vendor performance metrics based on invoice data
        """
        try:
            from db.database import Invoice, Vendor
            
            vendors = session.query(Vendor).all()
            
            for vendor in vendors:
                # Calculate metrics from invoices
                vendor_invoices = session.query(Invoice).filter(Invoice.vendor_id == vendor.id).all()
                
                if vendor_invoices:
                    total_spend = sum(float(inv.amount) for inv in vendor_invoices if inv.amount)
                    invoice_count = len(vendor_invoices)
                    avg_rate = np.mean([float(inv.rate) for inv in vendor_invoices if inv.rate])
                    avg_risk = np.mean([float(inv.risk_score) for inv in vendor_invoices if inv.risk_score])
                    
                    # Update vendor metrics
                    vendor.total_spend = total_spend
                    vendor.invoice_count = invoice_count
                    vendor.avg_rate = avg_rate if not np.isnan(avg_rate) else 0
                    vendor.performance_score = max(0, 100 - (avg_risk * 100)) if not np.isnan(avg_risk) else 85
                    
                    # Calculate on-time rate (simplified - would need delivery dates)
                    on_time_count = sum(1 for inv in vendor_invoices if inv.status == 'approved')
                    vendor.on_time_rate = (on_time_count / invoice_count * 100) if invoice_count > 0 else 0
            
            session.commit()
            logger.info(f"Updated metrics for {len(vendors)} vendors")
            
        except Exception as e:
            logger.error(f"Error updating vendor metrics: {str(e)}")
            session.rollback()
