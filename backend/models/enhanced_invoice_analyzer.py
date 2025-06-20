"""
Enhanced Invoice Analyzer using Real-World Legal Billing Data Models
Integrates the models trained with real-world legal rates and patterns
"""
import numpy as np
import pandas as pd
import joblib
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Setup logging
logger = logging.getLogger(__name__)

class EnhancedInvoiceAnalyzer:
    """Enhanced Invoice Analyzer with real-world legal billing intelligence"""
    
    def __init__(self, models_dir='backend/ml/models'):
        self.models_dir = models_dir
        self.models = {}
        self.scalers = {}
        self.rate_benchmarks = {}
        
        # Load enhanced models
        self._load_enhanced_models()
    
    def _load_enhanced_models(self):
        """Load all enhanced ML models and benchmarks"""
        try:
            # Load enhanced outlier detection model
            outlier_model_path = os.path.join(self.models_dir, 'enhanced_outlier_model.joblib')
            outlier_scaler_path = os.path.join(self.models_dir, 'enhanced_outlier_scaler.joblib')
            
            if os.path.exists(outlier_model_path) and os.path.exists(outlier_scaler_path):
                self.models['outlier'] = joblib.load(outlier_model_path)
                self.scalers['outlier'] = joblib.load(outlier_scaler_path)
                logger.info("Loaded enhanced outlier detection model")
            
            # Load enhanced spend prediction model
            spend_model_path = os.path.join(self.models_dir, 'enhanced_spend_model.joblib')
            spend_scaler_path = os.path.join(self.models_dir, 'enhanced_spend_scaler.joblib')
            
            if os.path.exists(spend_model_path) and os.path.exists(spend_scaler_path):
                self.models['spend'] = joblib.load(spend_model_path)
                self.scalers['spend'] = joblib.load(spend_scaler_path)
                logger.info("Loaded enhanced spend prediction model")
            
            # Load rate benchmarks
            benchmarks_path = os.path.join(self.models_dir, 'rate_benchmarks.json')
            if os.path.exists(benchmarks_path):
                with open(benchmarks_path, 'r') as f:
                    self.rate_benchmarks = json.load(f)
                logger.info(f"Loaded rate benchmarks for {len(self.rate_benchmarks)} practice areas")
                
        except Exception as e:
            logger.error(f"Error loading enhanced models: {str(e)}")
    
    def analyze_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive invoice analysis using enhanced models"""
        try:
            # Extract and normalize invoice data
            processed_data = self._preprocess_invoice_data(invoice_data)
            
            # Perform enhanced outlier detection
            outlier_analysis = self._detect_outliers(processed_data)
            
            # Analyze rates against real-world benchmarks
            rate_analysis = self._analyze_rates(processed_data)
            
            # Predict future spend patterns
            spend_analysis = self._analyze_spend_patterns(processed_data)
            
            # Generate comprehensive insights
            insights = self._generate_insights(
                outlier_analysis,
                rate_analysis, 
                spend_analysis,
                processed_data
            )
            
            return {
                'invoice_id': invoice_data.get('id', 'unknown'),
                'total_amount': processed_data.get('total_amount', 0),
                'currency': processed_data.get('currency', 'USD'),
                'outlier_analysis': outlier_analysis,
                'rate_analysis': rate_analysis,
                'spend_analysis': spend_analysis,
                'insights': insights,
                'recommendations': self._generate_recommendations(outlier_analysis, rate_analysis),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing invoice: {str(e)}")
            return {
                'error': str(e),
                'analysis_timestamp': datetime.now().isoformat()
            }
    
    def _preprocess_invoice_data(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize invoice data for analysis"""
        processed = {
            'total_amount': float(invoice_data.get('amount', 0)),
            'currency': invoice_data.get('currency', 'USD'),
            'date': invoice_data.get('date', datetime.now().isoformat()),
            'vendor': invoice_data.get('vendor', 'Unknown'),
            'line_items': []
        }
        
        # Process line items
        line_items = invoice_data.get('line_items', [])
        if isinstance(line_items, list):
            for item in line_items:
                processed_item = {
                    'description': item.get('description', ''),
                    'hours': float(item.get('hours', 0)),
                    'rate': float(item.get('rate', 0)),
                    'amount': float(item.get('amount', 0)),
                    'attorney': item.get('attorney', 'Unknown'),
                    'practice_area': self._infer_practice_area(item.get('description', '')),
                    'role': self._infer_attorney_role(item.get('attorney', ''))
                }
                processed['line_items'].append(processed_item)
        
        return processed
    
    def _detect_outliers(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect outliers using enhanced model"""
        outlier_results = {
            'has_outliers': False,
            'outlier_scores': [],
            'outlier_items': [],
            'overall_score': 0.0
        }
        
        if 'outlier' not in self.models:
            return outlier_results
        
        try:
            line_items = processed_data.get('line_items', [])
            if not line_items:
                return outlier_results
            
            # Create DataFrame for analysis
            df = pd.DataFrame(line_items)
            
            # Extract features for each line item
            features = []
            for _, item in df.iterrows():
                feature_vector = self._extract_outlier_features(item, df)
                features.append(feature_vector)
            
            if features:
                features_array = np.array(features)
                features_array = np.nan_to_num(features_array, nan=0.0)
                
                # Scale features and predict
                features_scaled = self.scalers['outlier'].transform(features_array)
                outlier_scores = self.models['outlier'].decision_function(features_scaled)
                outlier_predictions = self.models['outlier'].predict(features_scaled)
                
                # Process results
                outlier_results['outlier_scores'] = outlier_scores.tolist()
                outlier_results['has_outliers'] = any(pred == -1 for pred in outlier_predictions)
                outlier_results['overall_score'] = float(np.mean(outlier_scores))
                
                # Identify specific outlier items
                for i, (score, prediction) in enumerate(zip(outlier_scores, outlier_predictions)):
                    if prediction == -1:  # Outlier detected
                        outlier_results['outlier_items'].append({
                            'item_index': i,
                            'description': line_items[i]['description'],
                            'rate': line_items[i]['rate'],
                            'hours': line_items[i]['hours'],
                            'amount': line_items[i]['amount'],
                            'outlier_score': float(score),
                            'reason': self._explain_outlier(line_items[i], score)
                        })
                        
        except Exception as e:
            logger.error(f"Error in outlier detection: {str(e)}")
        
        return outlier_results
    
    def _analyze_rates(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze rates against real-world benchmarks"""
        rate_analysis = {
            'benchmark_comparisons': [],
            'rate_outliers': [],
            'average_rate': 0.0,
            'market_position': 'unknown'
        }
        
        line_items = processed_data.get('line_items', [])
        if not line_items:
            return rate_analysis
        
        total_amount = 0
        total_hours = 0
        
        for item in line_items:
            rate = item['rate']
            hours = item['hours']
            practice_area = item['practice_area']
            role = item['role']
            
            total_amount += item['amount']
            total_hours += hours
            
            # Compare against benchmarks
            benchmark_comparison = self._compare_rate_to_benchmark(rate, practice_area, role)
            if benchmark_comparison:
                rate_analysis['benchmark_comparisons'].append({
                    'item_description': item['description'],
                    'actual_rate': rate,
                    'benchmark_mean': benchmark_comparison['benchmark_mean'],
                    'benchmark_std': benchmark_comparison['benchmark_std'],
                    'deviation_score': benchmark_comparison['deviation_score'],
                    'market_position': benchmark_comparison['market_position']
                })
                
                # Flag significant deviations
                if abs(benchmark_comparison['deviation_score']) > 2:
                    rate_analysis['rate_outliers'].append({
                        'description': item['description'],
                        'rate': rate,
                        'expected_range': f"${benchmark_comparison['benchmark_mean'] - benchmark_comparison['benchmark_std']:.0f} - ${benchmark_comparison['benchmark_mean'] + benchmark_comparison['benchmark_std']:.0f}",
                        'deviation': f"{benchmark_comparison['deviation_score']:.1f} standard deviations"
                    })
        
        if total_hours > 0:
            rate_analysis['average_rate'] = total_amount / total_hours
            
            # Determine overall market position
            if rate_analysis['benchmark_comparisons']:
                avg_deviation = np.mean([comp['deviation_score'] for comp in rate_analysis['benchmark_comparisons']])
                if avg_deviation > 1:
                    rate_analysis['market_position'] = 'above_market'
                elif avg_deviation < -1:
                    rate_analysis['market_position'] = 'below_market'
                else:
                    rate_analysis['market_position'] = 'market_rate'
        
        return rate_analysis
    
    def _analyze_spend_patterns(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze spending patterns and predict future costs"""
        spend_analysis = {
            'pattern_analysis': {},
            'predicted_next_period': 0.0,
            'spending_velocity': 'normal',
            'cost_breakdown': {}
        }
        
        line_items = processed_data.get('line_items', [])
        if not line_items:
            return spend_analysis
        
        # Analyze cost breakdown by practice area and role
        by_practice_area = {}
        by_role = {}
        
        for item in line_items:
            practice_area = item['practice_area']
            role = item['role']
            amount = item['amount']
            
            by_practice_area[practice_area] = by_practice_area.get(practice_area, 0) + amount
            by_role[role] = by_role.get(role, 0) + amount
        
        spend_analysis['cost_breakdown'] = {
            'by_practice_area': by_practice_area,
            'by_role': by_role
        }
        
        return spend_analysis
    
    def _extract_outlier_features(self, item: pd.Series, df: pd.DataFrame) -> List[float]:
        """Extract features for outlier detection"""
        return [
            item['hours'],
            item['rate'], 
            item['amount'],
            item['rate'] / df['rate'].mean() if df['rate'].mean() > 0 else 0,
            item['hours'] * item['rate'],
            0  # Benchmark comparison placeholder
        ]
    
    def _compare_rate_to_benchmark(self, rate: float, practice_area: str, role: str) -> Optional[Dict[str, Any]]:
        """Compare rate to real-world benchmarks"""
        if practice_area not in self.rate_benchmarks:
            return None
        
        if role not in self.rate_benchmarks[practice_area]:
            return None
        
        benchmark = self.rate_benchmarks[practice_area][role]
        
        if isinstance(benchmark, dict) and 'mean' in benchmark:
            mean_rate = float(benchmark['mean'])
            std_rate = float(benchmark.get('std', 0))
            
            deviation_score = (rate - mean_rate) / max(std_rate, 1) if std_rate > 0 else 0
            
            # Determine market position
            if deviation_score > 1:
                market_position = 'above_market'
            elif deviation_score < -1:
                market_position = 'below_market'
            else:
                market_position = 'market_rate'
            
            return {
                'benchmark_mean': mean_rate,
                'benchmark_std': std_rate,
                'deviation_score': deviation_score,
                'market_position': market_position
            }
        
        return None
    
    def _infer_practice_area(self, description: str) -> str:
        """Infer practice area from description"""
        description_lower = description.lower()
        
        practice_area_keywords = {
            'Corporate': ['merger', 'acquisition', 'corporate', 'securities', 'finance', 'due diligence'],
            'Litigation': ['litigation', 'dispute', 'court', 'trial', 'discovery', 'deposition'],
            'IP': ['patent', 'trademark', 'copyright', 'intellectual property', 'ip'],
            'Employment': ['employment', 'labor', 'hr', 'discrimination', 'harassment'],
            'Real Estate': ['real estate', 'property', 'lease', 'zoning', 'title'],
            'Family Law': ['divorce', 'custody', 'family', 'matrimonial'],
            'Criminal': ['criminal', 'defense', 'prosecution', 'plea'],
            'Estate Planning': ['estate', 'will', 'trust', 'probate']
        }
        
        for area, keywords in practice_area_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return area
        
        return 'General'
    
    def _infer_attorney_role(self, attorney: str) -> str:
        """Infer attorney role/level"""
        if not attorney or attorney == 'Unknown':
            return 'Attorney'
        
        attorney_lower = attorney.lower()
        
        if 'partner' in attorney_lower or 'ptr' in attorney_lower:
            return 'Partner'
        elif 'associate' in attorney_lower or 'assoc' in attorney_lower:
            return 'Associate'
        elif 'counsel' in attorney_lower:
            return 'Counsel'
        elif 'paralegal' in attorney_lower:
            return 'Paralegal'
        else:
            return 'Attorney'
    
    def _explain_outlier(self, item: Dict[str, Any], score: float) -> str:
        """Generate explanation for why an item is an outlier"""
        reasons = []
        
        if item['rate'] > 2000:
            reasons.append("Extremely high hourly rate")
        if item['hours'] > 12:
            reasons.append("Very high time entry")
        if item['amount'] > 10000:
            reasons.append("High total amount")
        
        if not reasons:
            reasons.append("Unusual combination of rate, hours, and amount")
        
        return "; ".join(reasons)
    
    def _generate_insights(self, outlier_analysis: Dict, rate_analysis: Dict, 
                          spend_analysis: Dict, processed_data: Dict) -> List[str]:
        """Generate actionable insights"""
        insights = []
        
        # Outlier insights
        if outlier_analysis['has_outliers']:
            insights.append(f"⚠️ {len(outlier_analysis['outlier_items'])} unusual line items detected")
        
        # Rate insights
        if rate_analysis['rate_outliers']:
            insights.append(f"💰 {len(rate_analysis['rate_outliers'])} rates significantly deviate from market")
        
        if rate_analysis['market_position'] == 'above_market':
            insights.append("📈 Overall rates are above market average")
        elif rate_analysis['market_position'] == 'below_market':
            insights.append("📉 Overall rates are below market average")
        
        # Spend insights
        cost_breakdown = spend_analysis.get('cost_breakdown', {})
        if cost_breakdown.get('by_practice_area'):
            top_area = max(cost_breakdown['by_practice_area'].items(), key=lambda x: x[1])
            insights.append(f"🏛️ Highest spend in {top_area[0]} (${top_area[1]:,.2f})")
        
        return insights
    
    def _generate_recommendations(self, outlier_analysis: Dict, rate_analysis: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if outlier_analysis['has_outliers']:
            recommendations.append("Review flagged line items for accuracy and reasonableness")
        
        if rate_analysis['market_position'] == 'above_market':
            recommendations.append("Consider negotiating rates with vendors charging above market")
        
        if rate_analysis['rate_outliers']:
            recommendations.append("Audit vendors with rates significantly outside normal ranges")
        
        recommendations.append("Compare regularly with industry benchmarks")
        recommendations.append("Consider implementing rate guidelines based on market data")
        
        return recommendations

# Integration function for backward compatibility
def analyze_invoice_enhanced(invoice_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced invoice analysis function"""
    analyzer = EnhancedInvoiceAnalyzer()
    return analyzer.analyze_invoice(invoice_data)
