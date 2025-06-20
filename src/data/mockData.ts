import { Invoice, Vendor, DashboardMetrics } from '../services/api';

// Mock data for development
export const mockInvoices: Invoice[] = [
  {
    id: 'INV-2024-001',
    vendor: 'Morrison & Foerster LLP',
    amount: 45750,
    status: 'approved',
    date: '2024-01-15',
    dueDate: '2024-02-15',
    matter: 'IP Litigation - TechCorp',
    riskScore: 25,
    category: 'Litigation',
    description: 'Monthly legal services for patent litigation matter',
    hours: 65,
    rate: 950,
    total: 45750
  },
  {
    id: 'INV-2024-002',
    vendor: 'Baker McKenzie',
    amount: 23400,
    status: 'pending',
    date: '2024-01-14',
    dueDate: '2024-02-14',
    matter: 'M&A Advisory',
    riskScore: 45,
    category: 'Corporate',
    description: 'Due diligence services for potential acquisition',
    hours: 32,
    rate: 850,
    total: 23400
  },
  {
    id: 'INV-2024-003',
    vendor: 'Latham & Watkins',
    amount: 67800,
    status: 'flagged',
    date: '2024-01-13',
    dueDate: '2024-02-13',
    matter: 'Regulatory Compliance',
    riskScore: 85,
    category: 'Compliance',
    description: 'Regulatory compliance review and implementation',
    hours: 78,
    rate: 1100,
    total: 67800
  },
  {
    id: 'INV-2024-004',
    vendor: 'Skadden Arps',
    amount: 34200,
    status: 'processing',
    date: '2024-01-12',
    dueDate: '2024-02-12',
    matter: 'Employment Law',
    riskScore: 15,
    category: 'Labor',
    description: 'Employee handbook updates and compliance review',
    hours: 38,
    rate: 1050,
    total: 34200
  },
  {
    id: 'INV-2024-005',
    vendor: 'White & Case',
    amount: 52300,
    status: 'approved',
    date: '2024-01-11',
    dueDate: '2024-02-11',
    matter: 'International Trade',
    riskScore: 35,
    category: 'Trade',
    description: 'International trade agreement compliance review',
    hours: 62,
    rate: 900,
    total: 52300
  }
];

export const mockVendors: Vendor[] = [
  {
    id: 'V001',
    name: 'Morrison & Foerster LLP',
    category: 'Am Law 100',
    spend: 342800,
    matter_count: 8,
    avg_rate: 950,
    performance_score: 85,
    diversity_score: 72,
    on_time_rate: 94
  },
  {
    id: 'V002',
    name: 'Baker McKenzie',
    category: 'Global',
    spend: 218400,
    matter_count: 6,
    avg_rate: 850,
    performance_score: 78,
    diversity_score: 80,
    on_time_rate: 91
  },
  {
    id: 'V003',
    name: 'Latham & Watkins',
    category: 'Am Law 100',
    spend: 567800,
    matter_count: 12,
    avg_rate: 1100,
    performance_score: 90,
    diversity_score: 68,
    on_time_rate: 96
  },
  {
    id: 'V004',
    name: 'Skadden Arps',
    category: 'Am Law 100',
    spend: 435200,
    matter_count: 7,
    avg_rate: 1050,
    performance_score: 88,
    diversity_score: 65,
    on_time_rate: 92
  },
  {
    id: 'V005',
    name: 'White & Case',
    category: 'Global',
    spend: 312500,
    matter_count: 9,
    avg_rate: 900,
    performance_score: 82,
    diversity_score: 75,
    on_time_rate: 90
  }
];

export const mockDashboardMetrics: DashboardMetrics = {
  total_spend: 2847392,
  spend_change_percentage: 12.5,
  invoice_count: 234,
  active_matters: 156,
  risk_factors_count: 18,
  high_risk_invoices_count: 15,
  avg_processing_time: 3.2,
  date_range: {
    from: '2024-01-01',
    to: '2024-12-31'
  },
  trend_data: {
    monthly_spend: [
      { period: '2024-01', amount: 235000 },
      { period: '2024-02', amount: 242000 },
      { period: '2024-03', amount: 238000 },
      { period: '2024-04', amount: 251000 },
      { period: '2024-05', amount: 247000 },
      { period: '2024-06', amount: 258000 },
      { period: '2024-07', amount: 265000 },
      { period: '2024-08', amount: 271000 },
      { period: '2024-09', amount: 269000 },
      { period: '2024-10', amount: 278000 },
      { period: '2024-11', amount: 284000 },
      { period: '2024-12', amount: 292000 }
    ]
  }
};

export const mockSpendTrends = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  datasets: [
    {
      label: 'Litigation',
      data: [120000, 145000, 132000, 158000, 142000, 165000, 157000, 169000, 178000, 184000, 192000, 205000]
    },
    {
      label: 'Corporate',
      data: [85000, 92000, 87000, 98000, 105000, 112000, 108000, 119000, 125000, 131000, 138000, 145000]
    },
    {
      label: 'IP',
      data: [62000, 68000, 72000, 75000, 81000, 85000, 91000, 95000, 98000, 105000, 112000, 120000]
    },
    {
      label: 'Compliance',
      data: [45000, 48000, 52000, 55000, 58000, 62000, 65000, 69000, 72000, 75000, 79000, 85000]
    }
  ]
};

export const mockAlerts = [
  {
    id: 1,
    type: 'budget',
    severity: 'high',
    title: 'Budget Threshold Exceeded',
    message: 'IP Litigation matter has exceeded 90% of allocated budget',
    time: '2 hours ago',
    icon: 'dollar'
  },
  {
    id: 2,
    type: 'anomaly',
    severity: 'medium',
    title: 'Unusual Billing Pattern',
    message: 'Baker McKenzie submitted 3x normal hours for Q4',
    time: '4 hours ago',
    icon: 'trend'
  },
  {
    id: 3,
    type: 'approval',
    severity: 'low',
    title: 'Pending Approvals',
    message: '12 invoices requiring manager approval',
    time: '6 hours ago',
    icon: 'clock'
  },
  {
    id: 4,
    type: 'compliance',
    severity: 'high',
    title: 'Missing Documentation',
    message: 'Invoice #INV-2024-003 lacks required supporting docs',
    time: '1 day ago',
    icon: 'file'
  }
];
