import random
import json
from datetime import datetime, timedelta
import faker
import numpy as np
from typing import List, Dict, Any
import os

fake = faker.Faker()

class SampleDataGenerator:
    def __init__(self):
        self.vendors = self._generate_vendors(20)
        self.matters = self._generate_matters(50)
        self.timekeepers = self._generate_timekeepers(100)
        
        self.task_descriptions = [
            "Document review and analysis",
            "Client consultation and communication",
            "Legal research and writing",
            "Court appearance and preparation",
            "Contract drafting and review",
            "Due diligence investigation",
            "Regulatory filing preparation",
            "Settlement negotiation",
            "Motion drafting",
            "Expert witness coordination"
        ]
        
    def _generate_vendors(self, count: int) -> List[Dict[str, Any]]:
        """Generate sample law firms"""
        vendors = []
        law_firm_types = ['Big Law', 'Boutique', 'Regional', 'Specialty']
        
        for i in range(count):
            rate_base = random.choice([400, 500, 600, 700, 800])
            vendors.append({
                'id': i + 1,
                'name': f"{fake.last_name()} & {fake.last_name()} LLP",
                'type': random.choice(law_firm_types),
                'hourly_rate_base': rate_base,
                'rate_range': {
                    'partner': [rate_base * 1.2, rate_base * 1.5],
                    'associate': [rate_base * 0.6, rate_base * 0.9],
                    'paralegal': [rate_base * 0.3, rate_base * 0.4]
                },
                'risk_profile': round(random.uniform(0.1, 0.9), 2),
                'performance_score': round(random.uniform(60, 95), 1)
            })
        return vendors
    
    def _generate_matters(self, count: int) -> List[Dict[str, Any]]:
        """Generate sample legal matters"""
        matter_types = ['Litigation', 'Corporate', 'IP', 'Employment', 'Regulatory']
        matters = []
        
        for i in range(count):
            start_date = fake.date_between(start_date='-2y', end_date='-6m')
            matters.append({
                'id': i + 1,
                'name': f"{random.choice(matter_types)} - {fake.company()}",
                'type': random.choice(matter_types),
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': (start_date + timedelta(days=random.randint(90, 540))).strftime('%Y-%m-%d'),
                'budget': random.randint(50000, 500000)
            })
        return matters
    
    def _generate_timekeepers(self, count: int) -> List[Dict[str, Any]]:
        """Generate sample timekeepers"""
        roles = ['Partner', 'Senior Associate', 'Associate', 'Junior Associate', 'Paralegal']
        timekeepers = []
        
        for i in range(count):
            role = random.choice(roles)
            timekeepers.append({
                'id': i + 1,
                'name': fake.name(),
                'role': role,
                'years_experience': random.randint(1, 25),
                'specialty': random.choice(['Litigation', 'Corporate', 'IP', 'Employment', 'Regulatory'])
            })
        return timekeepers
    
    def generate_invoice(self) -> Dict[str, Any]:
        """Generate a sample invoice with line items"""
        vendor = random.choice(self.vendors)
        matter = random.choice(self.matters)
        invoice_date = fake.date_between(start_date='-1y', end_date='today')
        
        # Generate line items
        line_items = self._generate_line_items(
            vendor,
            invoice_date,
            random.randint(5, 20)
        )
        
        # Calculate totals
        total_hours = sum(item['hours'] for item in line_items)
        total_amount = sum(item['amount'] for item in line_items)
        
        # Add some random anomalies
        anomalies = []
        if random.random() < 0.2:  # 20% chance of anomalies
            if random.random() < 0.5:
                # Add high-rate anomaly
                line_items.append(self._generate_high_rate_item(vendor))
                anomalies.append({
                    'type': 'high_rate',
                    'severity': 'high',
                    'description': 'Unusually high hourly rate detected'
                })
            else:
                # Add block billing anomaly
                line_items.append(self._generate_block_billing_item())
                anomalies.append({
                    'type': 'block_billing',
                    'severity': 'medium',
                    'description': 'Potential block billing detected'
                })
        
        # Calculate risk score based on various factors
        risk_score = self._calculate_risk_score(
            total_amount,
            total_hours,
            line_items,
            vendor['risk_profile'],
            anomalies
        )
        
        return {
            'invoice_number': f"INV-{fake.random_number(digits=8)}",
            'vendor_id': vendor['id'],
            'matter_id': matter['id'],
            'date': invoice_date.strftime('%Y-%m-%d'),
            'amount': total_amount,
            'hours': total_hours,
            'line_items': line_items,
            'anomalies': anomalies,
            'risk_score': risk_score,
            'status': 'pending_review'
        }
    
    def _generate_line_items(self, vendor: Dict, date: datetime, count: int) -> List[Dict[str, Any]]:
        """Generate sample line items for an invoice"""
        line_items = []
        activities = [
            'Review and analyze', 'Draft and prepare', 'Conference with',
            'Research regarding', 'Coordinate with', 'Attend meeting re',
            'Revise and finalize', 'Telephone conference with'
        ]
        
        for _ in range(count):
            timekeeper = random.choice(self.timekeepers)
            role_category = 'partner' if 'Partner' in timekeeper['role'] else \
                          'associate' if 'Associate' in timekeeper['role'] else 'paralegal'
            
            rate_range = vendor['rate_range'][role_category]
            rate = random.uniform(rate_range[0], rate_range[1])
            hours = round(random.uniform(0.5, 4.0), 1)
            
            line_items.append({
                'timekeeper': timekeeper['name'],
                'timekeeper_title': timekeeper['role'],
                'date': date.strftime('%Y-%m-%d'),
                'hours': hours,
                'rate': round(rate, 2),
                'amount': round(hours * rate, 2),
                'description': f"{random.choice(activities)} {random.choice(self.task_descriptions)}"
            })
        
        return line_items
    
    def _generate_high_rate_item(self, vendor: Dict) -> Dict[str, Any]:
        """Generate a line item with an unusually high rate"""
        timekeeper = random.choice([t for t in self.timekeepers if 'Partner' in t['role']])
        base_rate = vendor['rate_range']['partner'][1]
        high_rate = base_rate * random.uniform(1.5, 2.0)
        
        return {
            'timekeeper': timekeeper['name'],
            'timekeeper_title': timekeeper['role'],
            'date': fake.date_between(start_date='-1m', end_date='today').strftime('%Y-%m-%d'),
            'hours': round(random.uniform(1.0, 3.0), 1),
            'rate': round(high_rate, 2),
            'amount': round(high_rate * 2.0, 2),
            'description': 'Emergency consultation and strategic advice regarding critical matter developments'
        }
    
    def _generate_block_billing_item(self) -> Dict[str, Any]:
        """Generate a line item that appears to be block billing"""
        activities = [
            'Review and analyze correspondence and documents;',
            'Conference with client and team members;',
            'Draft and revise motion papers;',
            'Research legal precedents and authorities;',
            'Prepare for and attend court hearing;'
        ]
        
        description = ' '.join(random.sample(activities, k=random.randint(3, 5)))
        hours = round(random.uniform(6.0, 10.0), 1)
        rate = random.uniform(400, 800)
        
        return {
            'timekeeper': fake.name(),
            'timekeeper_title': 'Partner',
            'date': fake.date_between(start_date='-1m', end_date='today').strftime('%Y-%m-%d'),
            'hours': hours,
            'rate': round(rate, 2),
            'amount': round(hours * rate, 2),
            'description': description
        }
    
    def _calculate_risk_score(
        self,
        total_amount: float,
        total_hours: float,
        line_items: List[Dict],
        vendor_risk: float,
        anomalies: List[Dict]
    ) -> float:
        """Calculate a risk score based on various factors"""
        base_score = 50
        
        # Adjust for amount
        if total_amount > 100000:
            base_score += 15
        elif total_amount > 50000:
            base_score += 10
        
        # Adjust for hours
        if total_hours > 100:
            base_score += 10
        
        # Adjust for vendor risk
        base_score += vendor_risk * 20
        
        # Adjust for anomalies
        for anomaly in anomalies:
            if anomaly['severity'] == 'high':
                base_score += 15
            elif anomaly['severity'] == 'medium':
                base_score += 10
            else:
                base_score += 5
        
        # Cap score between 0 and 100
        return min(max(base_score, 0), 100)

def generate_sample_data(count: int = 100) -> None:
    """Generate sample data and save to files"""
    generator = SampleDataGenerator()
    
    # Generate invoices
    invoices = [generator.generate_invoice() for _ in range(count)]
    
    # Save to files
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    with open(os.path.join(data_dir, 'sample_invoices.json'), 'w') as f:
        json.dump(invoices, f, indent=2)
        
    with open(os.path.join(data_dir, 'sample_vendors.json'), 'w') as f:
        json.dump(generator.vendors, f, indent=2)
        
    with open(os.path.join(data_dir, 'sample_matters.json'), 'w') as f:
        json.dump(generator.matters, f, indent=2)
    
    print(f"Generated {count} sample invoices and saved to {data_dir}")

if __name__ == '__main__':
    generate_sample_data()
