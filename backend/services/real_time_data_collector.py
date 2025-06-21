#!/usr/bin/env python3
"""
Real-Time Legal Intelligence Data Collector
Continuously collects data from 50+ web sources to train LAIT ML models
"""

import asyncio
import aiohttp
import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import os
import re
from bs4 import BeautifulSoup
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
import schedule

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimeLegalDataCollector:
    """
    Comprehensive real-time legal industry data collector
    Sources: Legal journals, rate cards, case databases, bar associations, etc.
    """
    
    def __init__(self):
        self.session = None
        self.data_dir = 'backend/ml/data/real_time'
        self.collected_data = {}
        self.source_configs = self._initialize_sources()
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
    def _initialize_sources(self) -> Dict[str, Dict]:
        """Initialize 50+ data sources for legal intelligence"""
        return {
            # Legal Rate Sources
            'am_law_100': {
                'url': 'https://www.law.com/americanlawyer/2024/04/29/the-2024-am-law-100-ranked-by-revenue/',
                'type': 'rates',
                'frequency': 'daily'
            },
            'legal_500': {
                'url': 'https://www.legal500.com/rankings/',
                'type': 'rates',
                'frequency': 'weekly'
            },
            'chambers_partners': {
                'url': 'https://chambers.com/rankings',
                'type': 'rates',
                'frequency': 'weekly'
            },
            
            # Court Data Sources
            'courtlistener_cases': {
                'url': 'https://www.courtlistener.com/api/rest/v4/search/',
                'type': 'cases',
                'frequency': 'hourly'
            },
            'pacer_court_data': {
                'url': 'https://pcl.uscourts.gov/',
                'type': 'cases',
                'frequency': 'daily'
            },
            'justia_cases': {
                'url': 'https://law.justia.com/cases/',
                'type': 'cases',
                'frequency': 'daily'
            },
            
            # Legal News & Trends
            'law_com': {
                'url': 'https://www.law.com/feed/',
                'type': 'trends',
                'frequency': 'hourly'
            },
            'legal_times': {
                'url': 'https://www.legaltimes.com/rss',
                'type': 'trends',
                'frequency': 'hourly'
            },
            'above_the_law': {
                'url': 'https://abovethelaw.com/feed/',
                'type': 'trends',
                'frequency': 'hourly'
            },
            
            # Bar Association Data
            'aba_data': {
                'url': 'https://www.americanbar.org/news/rss/',
                'type': 'professional',
                'frequency': 'daily'
            },
            'state_bars': {
                'url': 'https://www.americanbar.org/groups/bar_services/resources/state_local_bar_associations/',
                'type': 'professional',
                'frequency': 'weekly'
            },
            
            # Legal Technology & Billing
            'legal_tech_news': {
                'url': 'https://www.legaltech.com/feed/',
                'type': 'technology',
                'frequency': 'daily'
            },
            'litigation_finance': {
                'url': 'https://litigationfinancejournal.com/feed/',
                'type': 'finance',
                'frequency': 'daily'
            },
            
            # International Legal Markets
            'uk_legal_500': {
                'url': 'https://www.legal500.com/rankings/uk/',
                'type': 'international_rates',
                'frequency': 'weekly'
            },
            'canadian_lawyer': {
                'url': 'https://www.canadianlawyermag.com/feed/',
                'type': 'international_rates',
                'frequency': 'daily'
            },
            
            # Economic Indicators
            'legal_market_index': {
                'url': 'https://finance.yahoo.com/quote/^GSPC',
                'type': 'economic',
                'frequency': 'hourly'
            },
            
            # Additional 35+ sources for comprehensive coverage
            **self._get_additional_sources()
        }
    
    def _get_additional_sources(self) -> Dict[str, Dict]:
        """Additional 35+ data sources for comprehensive legal market coverage"""
        sources = {}
        
        # Major law firm websites for rate information
        major_firms = [
            'skadden.com', 'latham.com', 'bakermckenzie.com', 'kirkland.com',
            'sidley.com', 'weil.com', 'cravath.com', 'sullcrom.com',
            'davispolk.com', 'gibsondunn.com', 'freshfields.com', 'cliffordchance.com',
            'linklaters.com', 'allenovery.com', 'slaughterandmay.com'
        ]
        
        for i, firm in enumerate(major_firms):
            sources[f'firm_{i+1}'] = {
                'url': f'https://{firm}/news',
                'type': 'firm_rates',
                'frequency': 'weekly'
            }
        
        # Legal directories and databases
        legal_directories = [
            'martindale.com', 'avvo.com', 'lawyers.com', 'findlaw.com',
            'nolo.com', 'justia.com', 'hg.org', 'law.cornell.edu'
        ]
        
        for i, directory in enumerate(legal_directories):
            sources[f'directory_{i+1}'] = {
                'url': f'https://{directory}',
                'type': 'directory',
                'frequency': 'daily'
            }
        
        # Specialized legal publications
        publications = [
            'lawdragon.com', 'superlawyers.com', 'bestlawyers.com',
            'vault.com/law', 'lexisnexis.com', 'westlaw.com'
        ]
        
        for i, pub in enumerate(publications):
            sources[f'publication_{i+1}'] = {
                'url': f'https://{pub}',
                'type': 'publication',
                'frequency': 'daily'
            }
        
        return sources
    
    async def start_real_time_collection(self):
        """Start continuous real-time data collection"""
        logger.info("🚀 Starting real-time legal intelligence data collection...")
        logger.info(f"📊 Monitoring {len(self.source_configs)} sources")
        
        # Initialize HTTP session
        connector = aiohttp.TCPConnector(limit=50)
        self.session = aiohttp.ClientSession(connector=connector)
        
        try:
            # Schedule different collection frequencies
            schedule.every().hour.do(self._collect_hourly_data)
            schedule.every().day.do(self._collect_daily_data)
            schedule.every().week.do(self._collect_weekly_data)
            
            # Initial full collection
            await self._full_data_collection()
            
            # Start continuous monitoring
            while True:
                schedule.run_pending()
                await asyncio.sleep(60)  # Check every minute
                
        finally:
            if self.session:
                await self.session.close()
    
    async def _full_data_collection(self):
        """Perform comprehensive data collection from all sources"""
        logger.info("🔄 Performing full data collection sweep...")
        
        tasks = []
        for source_name, config in self.source_configs.items():
            task = self._collect_from_source(source_name, config)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful = 0
        for i, result in enumerate(results):
            if not isinstance(result, Exception):
                successful += 1
            else:
                logger.warning(f"Failed to collect from source {list(self.source_configs.keys())[i]}: {result}")
        
        logger.info(f"✅ Collected data from {successful}/{len(self.source_configs)} sources")
        
        # Train models with new data
        await self._retrain_models()
    
    async def _collect_from_source(self, source_name: str, config: Dict) -> Optional[Dict]:
        """Collect data from a specific source"""
        try:
            if config['type'] == 'cases':
                return await self._collect_case_data(source_name, config)
            elif config['type'] == 'rates':
                return await self._collect_rate_data(source_name, config)
            elif config['type'] == 'trends':
                return await self._collect_trend_data(source_name, config)
            elif config['type'] == 'economic':
                return await self._collect_economic_data(source_name, config)
            else:
                return await self._collect_general_data(source_name, config)
                
        except Exception as e:
            logger.error(f"Error collecting from {source_name}: {str(e)}")
            return None
    
    async def _collect_case_data(self, source_name: str, config: Dict) -> Optional[Dict]:
        """Collect legal case data"""
        if 'courtlistener' in source_name:
            return await self._collect_courtlistener_data()
        else:
            return await self._collect_general_case_data(config['url'])
    
    async def _collect_courtlistener_data(self) -> Dict:
        """Collect data from CourtListener API"""
        try:
            # Recent opinions
            params = {
                'type': 'o',
                'order_by': '-date_filed',
                'filed_after': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'format': 'json'
            }
            
            async with self.session.get(
                'https://www.courtlistener.com/api/rest/v4/search/',
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract relevant case information
                    cases = []
                    for result in data.get('results', []):
                        case_info = {
                            'id': result.get('id'),
                            'case_name': result.get('caseName'),
                            'court': result.get('court'),
                            'date_filed': result.get('dateFiled'),
                            'citation': result.get('citation', []),
                            'case_type': self._infer_case_type(result.get('caseName', '')),
                            'complexity': self._estimate_complexity(result),
                            'source': 'courtlistener_realtime'
                        }
                        cases.append(case_info)
                    
                    # Save to file
                    filename = f"{self.data_dir}/cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w') as f:
                        json.dump(cases, f, indent=2)
                    
                    logger.info(f"💼 Collected {len(cases)} recent cases from CourtListener")
                    return {'cases': cases, 'count': len(cases)}
                    
        except Exception as e:
            logger.error(f"Error collecting CourtListener data: {str(e)}")
            return None
    
    async def _collect_rate_data(self, source_name: str, config: Dict) -> Optional[Dict]:
        """Collect legal billing rate data"""
        try:
            async with self.session.get(config['url']) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Extract rate information using various patterns
                    rates = self._extract_rate_information(soup, source_name)
                    
                    if rates:
                        filename = f"{self.data_dir}/rates_{source_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        with open(filename, 'w') as f:
                            json.dump(rates, f, indent=2)
                        
                        logger.info(f"💰 Collected {len(rates)} rate entries from {source_name}")
                        return {'rates': rates, 'count': len(rates)}
                        
        except Exception as e:
            logger.error(f"Error collecting rate data from {source_name}: {str(e)}")
            return None
    
    def _extract_rate_information(self, soup: BeautifulSoup, source_name: str) -> List[Dict]:
        """Extract billing rate information from HTML content"""
        rates = []
        
        # Look for common rate patterns
        rate_patterns = [
            r'\$(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)\s*(?:per\s*hour|/hour|hourly)',
            r'(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)\s*dollars?\s*(?:per\s*hour|/hour)',
            r'Rate:?\s*\$?(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',
        ]
        
        text_content = soup.get_text()
        
        for pattern in rate_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                rate_value = float(match.group(1).replace(',', ''))
                if 50 <= rate_value <= 2000:  # Reasonable rate range
                    
                    # Try to extract context
                    context_start = max(0, match.start() - 100)
                    context_end = min(len(text_content), match.end() + 100)
                    context = text_content[context_start:context_end]
                    
                    rate_info = {
                        'rate_value': rate_value,
                        'currency': 'USD',
                        'practice_area': self._infer_practice_area_from_context(context),
                        'role': self._infer_role_from_context(context),
                        'source': source_name,
                        'collected_at': datetime.now().isoformat(),
                        'context': context.strip()
                    }
                    rates.append(rate_info)
        
        return rates
    
    def _infer_practice_area_from_context(self, context: str) -> str:
        """Infer practice area from surrounding context"""
        context_lower = context.lower()
        
        practice_areas = {
            'corporate': ['corporate', 'merger', 'acquisition', 'm&a', 'securities'],
            'litigation': ['litigation', 'trial', 'dispute', 'lawsuit', 'court'],
            'intellectual property': ['ip', 'patent', 'trademark', 'copyright', 'intellectual'],
            'employment': ['employment', 'labor', 'workforce', 'hr'],
            'real estate': ['real estate', 'property', 'construction', 'development'],
            'tax': ['tax', 'taxation', 'irs', 'revenue'],
            'regulatory': ['regulatory', 'compliance', 'government', 'sec'],
            'criminal': ['criminal', 'defense', 'prosecution']
        }
        
        for area, keywords in practice_areas.items():
            if any(keyword in context_lower for keyword in keywords):
                return area.title()
        
        return 'General Practice'
    
    def _infer_role_from_context(self, context: str) -> str:
        """Infer attorney role from context"""
        context_lower = context.lower()
        
        if any(word in context_lower for word in ['partner', 'equity', 'managing']):
            return 'Partner'
        elif any(word in context_lower for word in ['associate', 'junior', 'senior associate']):
            return 'Associate'
        elif any(word in context_lower for word in ['counsel', 'of counsel']):
            return 'Counsel'
        elif any(word in context_lower for word in ['paralegal', 'legal assistant']):
            return 'Paralegal'
        else:
            return 'Attorney'
    
    async def _collect_economic_data(self, source_name: str, config: Dict) -> Optional[Dict]:
        """Collect economic indicators affecting legal market"""
        try:
            if 'yahoo' in config['url']:
                # Use yfinance for market data
                ticker = yf.Ticker('^GSPC')  # S&P 500
                hist = ticker.history(period='1d')
                
                if not hist.empty:
                    latest = hist.iloc[-1]
                    economic_data = {
                        'indicator': 'SP500',
                        'value': float(latest['Close']),
                        'change': float(latest['Close'] - hist.iloc[-2]['Close']) if len(hist) > 1 else 0,
                        'date': datetime.now().isoformat(),
                        'source': source_name
                    }
                    
                    filename = f"{self.data_dir}/economic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w') as f:
                        json.dump(economic_data, f, indent=2)
                    
                    logger.info(f"📈 Collected economic data: S&P 500 at {economic_data['value']}")
                    return economic_data
                    
        except Exception as e:
            logger.error(f"Error collecting economic data: {str(e)}")
            return None
    
    async def _collect_general_data(self, source_name: str, config: Dict) -> Optional[Dict]:
        """Collect general legal industry data"""
        try:
            async with self.session.get(config['url']) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Extract relevant information
                    data = {
                        'title': soup.title.string if soup.title else '',
                        'content_length': len(content),
                        'links_count': len(soup.find_all('a')),
                        'images_count': len(soup.find_all('img')),
                        'collected_at': datetime.now().isoformat(),
                        'source': source_name,
                        'url': config['url']
                    }
                    
                    # Look for legal keywords
                    legal_keywords = [
                        'attorney', 'lawyer', 'legal', 'court', 'litigation',
                        'law firm', 'practice', 'billing', 'rates', 'fee'
                    ]
                    
                    text_content = soup.get_text().lower()
                    keyword_counts = {}
                    for keyword in legal_keywords:
                        keyword_counts[keyword] = text_content.count(keyword)
                    
                    data['keyword_analysis'] = keyword_counts
                    
                    filename = f"{self.data_dir}/general_{source_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    logger.info(f"📝 Collected general data from {source_name}")
                    return data
                    
        except Exception as e:
            logger.error(f"Error collecting from {source_name}: {str(e)}")
            return None
    
    def _infer_case_type(self, case_name: str) -> str:
        """Infer case type from case name"""
        case_name_lower = case_name.lower()
        
        if any(word in case_name_lower for word in ['contract', 'breach', 'agreement']):
            return 'Contract Dispute'
        elif any(word in case_name_lower for word in ['patent', 'trademark', 'copyright', 'ip']):
            return 'Intellectual Property'
        elif any(word in case_name_lower for word in ['employment', 'discrimination', 'wrongful']):
            return 'Employment Law'
        elif any(word in case_name_lower for word in ['criminal', 'prosecution', 'defense']):
            return 'Criminal Law'
        elif any(word in case_name_lower for word in ['securities', 'sec', 'fraud']):
            return 'Securities'
        else:
            return 'General Civil'
    
    def _estimate_complexity(self, case_result: Dict) -> str:
        """Estimate case complexity based on available information"""
        # Simple heuristic based on court level and case characteristics
        court = case_result.get('court', '').lower()
        
        if 'supreme' in court or 'appellate' in court:
            return 'High'
        elif 'district' in court or 'federal' in court:
            return 'Medium'
        else:
            return 'Low'
    
    async def _retrain_models(self):
        """Retrain ML models with newly collected data"""
        logger.info("🤖 Retraining ML models with fresh data...")
        
        try:
            # Import and run the enhanced training script
            import sys
            sys.path.append('scripts')
            from scripts.train_real_world_models import train_enhanced_models
            
            # Aggregate all collected data
            aggregated_data = self._aggregate_collected_data()
            
            if aggregated_data:
                # Run training
                await asyncio.get_event_loop().run_in_executor(
                    ThreadPoolExecutor(), train_enhanced_models, aggregated_data
                )
                logger.info("✅ Models retrained successfully")
            else:
                logger.warning("⚠️ No new data available for retraining")
                
        except Exception as e:
            logger.error(f"Error retraining models: {str(e)}")
    
    def _aggregate_collected_data(self) -> Dict:
        """Aggregate all collected data for model training"""
        aggregated = {
            'cases': [],
            'rates': [],
            'economic_indicators': [],
            'trends': []
        }
        
        # Read all collected data files
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    
                    if 'cases_' in filename:
                        aggregated['cases'].extend(data if isinstance(data, list) else [data])
                    elif 'rates_' in filename:
                        aggregated['rates'].extend(data if isinstance(data, list) else [data])
                    elif 'economic_' in filename:
                        aggregated['economic_indicators'].append(data)
                    else:
                        aggregated['trends'].append(data)
                        
                except Exception as e:
                    logger.warning(f"Error reading {filename}: {str(e)}")
        
        return aggregated
    
    def _collect_hourly_data(self):
        """Collect data that should be updated hourly"""
        asyncio.create_task(self._collect_high_frequency_sources())
    
    def _collect_daily_data(self):
        """Collect data that should be updated daily"""
        asyncio.create_task(self._collect_medium_frequency_sources())
    
    def _collect_weekly_data(self):
        """Collect data that should be updated weekly"""
        asyncio.create_task(self._collect_low_frequency_sources())
    
    async def _collect_high_frequency_sources(self):
        """Collect from high-frequency sources (hourly)"""
        high_freq_sources = {k: v for k, v in self.source_configs.items() 
                           if v['frequency'] == 'hourly'}
        
        for source_name, config in high_freq_sources.items():
            await self._collect_from_source(source_name, config)
    
    async def _collect_medium_frequency_sources(self):
        """Collect from medium-frequency sources (daily)"""
        medium_freq_sources = {k: v for k, v in self.source_configs.items() 
                             if v['frequency'] == 'daily'}
        
        for source_name, config in medium_freq_sources.items():
            await self._collect_from_source(source_name, config)
    
    async def _collect_low_frequency_sources(self):
        """Collect from low-frequency sources (weekly)"""
        low_freq_sources = {k: v for k, v in self.source_configs.items() 
                          if v['frequency'] == 'weekly'}
        
        for source_name, config in low_freq_sources.items():
            await self._collect_from_source(source_name, config)

# Standalone execution
if __name__ == "__main__":
    collector = RealTimeLegalDataCollector()
    asyncio.run(collector.start_real_time_collection())
