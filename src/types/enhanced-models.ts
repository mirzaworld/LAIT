// Enhanced data models for LAIT system

export interface Matter {
  id: string;
  name: string;
  description: string;
  client: string;
  practice_area: string;
  matter_type: string;
  status: 'open' | 'closed' | 'on_hold' | 'pending';
  priority: 'low' | 'medium' | 'high' | 'critical';
  budget: number;
  spent: number;
  forecast: number;
  start_date: string;
  target_end_date: string;
  actual_end_date?: string;
  responsible_attorney: string;
  assigned_team: string[];
  phases: MatterPhase[];
  documents: Document[];
  risks: RiskAssessment[];
  created_at: string;
  updated_at: string;
}

export interface MatterPhase {
  id: string;
  matter_id: string;
  name: string;
  description: string;
  status: 'not_started' | 'in_progress' | 'completed' | 'on_hold';
  budget: number;
  spent: number;
  start_date: string;
  target_end_date: string;
  actual_end_date?: string;
  milestones: Milestone[];
  deliverables: string[];
}

export interface Milestone {
  id: string;
  phase_id: string;
  name: string;
  description: string;
  due_date: string;
  completed: boolean;
  completed_date?: string;
  assigned_to: string;
}

export interface EnhancedInvoice {
  id: string;
  vendor: string;
  vendor_id: string;
  matter_id: string;
  matter_name: string;
  amount: number;
  currency: string;
  exchange_rate: number;
  amount_usd: number;
  status: 'pending' | 'approved' | 'rejected' | 'flagged' | 'processing';
  date: string;
  due_date: string;
  payment_date?: string;
  invoice_number: string;
  po_number?: string;
  description: string;
  line_items: InvoiceLineItem[];
  hours: number;
  rate: number;
  risk_score: number;
  risk_level: 'low' | 'medium' | 'high';
  anomalies: Anomaly[];
  ai_analysis: AIAnalysis;
  approval_workflow: ApprovalStep[];
  documents: string[];
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface InvoiceLineItem {
  id: string;
  invoice_id: string;
  description: string;
  attorney_name: string;
  attorney_rate: number;
  hours: number;
  amount: number;
  date: string;
  task_code: string;
  activity_code: string;
  phase_id?: string;
  expense_type?: string;
  approved: boolean;
  flagged: boolean;
  flag_reason?: string;
}

export interface Anomaly {
  type: 'rate_spike' | 'time_anomaly' | 'duplicate' | 'budget_overrun' | 'pattern_deviation';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  confidence: number;
  details: any;
  auto_resolved: boolean;
  resolved_by?: string;
  resolved_at?: string;
}

export interface AIAnalysis {
  document_classification: string;
  confidence_score: number;
  extracted_entities: EntityExtraction[];
  sentiment_analysis: SentimentAnalysis;
  compliance_check: ComplianceCheck;
  recommendations: string[];
  processed_at: string;
  model_version: string;
}

export interface EntityExtraction {
  entity_type: string;
  entity_value: string;
  confidence: number;
  start_position: number;
  end_position: number;
}

export interface SentimentAnalysis {
  overall_sentiment: 'positive' | 'neutral' | 'negative';
  confidence: number;
  aspects: AspectSentiment[];
}

export interface AspectSentiment {
  aspect: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  confidence: number;
}

export interface ComplianceCheck {
  compliant: boolean;
  violations: ComplianceViolation[];
  checked_regulations: string[];
  last_checked: string;
}

export interface ComplianceViolation {
  regulation: string;
  violation_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  remedy_suggestion: string;
}

export interface ApprovalStep {
  id: string;
  step_number: number;
  approver_id: string;
  approver_name: string;
  status: 'pending' | 'approved' | 'rejected' | 'delegated';
  comments?: string;
  approved_at?: string;
  amount_limit: number;
}

export interface EnhancedVendor {
  id: string;
  name: string;
  legal_name: string;
  category: string;
  vendor_type: 'law_firm' | 'alternative_provider' | 'consultant' | 'expert_witness';
  tier: 'preferred' | 'approved' | 'restricted' | 'probation';
  status: 'active' | 'inactive' | 'under_review';
  
  // Contact Information
  primary_contact: Contact;
  billing_contact: Contact;
  
  // Financial Information
  spend: number;
  matter_count: number;
  avg_rate: number;
  payment_terms: string;
  currency_preference: string;
  
  // Performance Metrics
  performance_score: number;
  on_time_rate: number;
  budget_adherence: number;
  quality_score: number;
  client_satisfaction: number;
  
  // Diversity & Inclusion
  diversity_score: number;
  minority_owned: boolean;
  women_owned: boolean;
  small_business: boolean;
  diversity_certifications: string[];
  
  // Capabilities
  practice_areas: string[];
  jurisdictions: string[];
  languages: string[];
  specializations: string[];
  
  // Compliance & Risk
  insurance_coverage: InsuranceCoverage;
  compliance_status: ComplianceStatus;
  background_check: BackgroundCheck;
  conflicts_cleared: boolean;
  
  // Analytics
  success_rate: number;
  case_outcomes: CaseOutcome[];
  rate_trends: RateTrend[];
  utilization_patterns: UtilizationPattern[];
  
  created_at: string;
  updated_at: string;
}

export interface Contact {
  name: string;
  title: string;
  email: string;
  phone: string;
  address: Address;
}

export interface Address {
  street: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
}

export interface InsuranceCoverage {
  professional_liability: number;
  general_liability: number;
  cyber_liability: number;
  expires_at: string;
  carrier: string;
  verified: boolean;
}

export interface ComplianceStatus {
  malpractice_insurance: boolean;
  bar_standing: boolean;
  background_verified: boolean;
  conflicts_cleared: boolean;
  data_security_certified: boolean;
  last_updated: string;
}

export interface BackgroundCheck {
  completed: boolean;
  completed_at: string;
  provider: string;
  results: 'clear' | 'minor_issues' | 'major_issues' | 'failed';
  next_check_due: string;
}

export interface CaseOutcome {
  matter_type: string;
  outcome: 'won' | 'lost' | 'settled' | 'dismissed';
  settlement_amount?: number;
  duration_days: number;
  client_satisfaction: number;
}

export interface RateTrend {
  year: number;
  month: number;
  avg_rate: number;
  change_percentage: number;
}

export interface UtilizationPattern {
  timekeeper: string;
  role: string;
  avg_hours_per_matter: number;
  efficiency_score: number;
  rate: number;
}

export interface RiskAssessment {
  id: string;
  matter_id?: string;
  vendor_id?: string;
  invoice_id?: string;
  risk_type: 'financial' | 'legal' | 'compliance' | 'operational' | 'reputational';
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  probability: number;
  impact: number;
  risk_score: number;
  description: string;
  mitigation_strategies: string[];
  owner: string;
  status: 'identified' | 'assessed' | 'mitigated' | 'accepted' | 'transferred';
  created_at: string;
  updated_at: string;
  review_date: string;
}

export interface EnhancedDashboardMetrics {
  // Financial Metrics
  total_spend: number;
  spend_change_percentage: number;
  budget_utilization: number;
  cost_per_matter: number;
  
  // Volume Metrics
  invoice_count: number;
  matter_count: number;
  active_matters: number;
  vendor_count: number;
  
  // Performance Metrics
  avg_processing_time: number;
  approval_rate: number;
  budget_adherence: number;
  vendor_performance_avg: number;
  
  // Risk Metrics
  high_risk_invoices_count: number;
  risk_factors_count: number;
  anomalies_detected: number;
  compliance_violations: number;
  
  // AI Metrics
  ai_processing_accuracy: number;
  auto_approval_rate: number;
  time_saved_hours: number;
  cost_savings: number;
  
  // Diversity Metrics
  diverse_vendor_spend: number;
  diverse_vendor_percentage: number;
  diversity_score: number;
  
  // Time Range
  date_range: {
    from: string;
    to: string;
  };
  
  // Trend Data
  trend_data: {
    monthly_spend: MonthlySpend[];
    matter_pipeline: MatterPipelineData[];
    risk_trends: RiskTrendData[];
    performance_trends: PerformanceTrendData[];
  };
}

export interface MonthlySpend {
  period: string;
  amount: number;
  budget: number;
  forecast: number;
  matter_count: number;
  vendor_count: number;
}

export interface MatterPipelineData {
  period: string;
  opened: number;
  closed: number;
  active: number;
  on_hold: number;
}

export interface RiskTrendData {
  period: string;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  avg_risk_score: number;
}

export interface PerformanceTrendData {
  period: string;
  avg_processing_time: number;
  approval_rate: number;
  vendor_performance: number;
  client_satisfaction: number;
}

export interface BenchmarkData {
  category: string;
  metric: string;
  our_value: number;
  peer_median: number;
  peer_75th_percentile: number;
  peer_90th_percentile: number;
  industry_best: number;
  percentile_rank: number;
}

export interface PredictiveAnalytics {
  spend_forecast: SpendForecast[];
  budget_alerts: BudgetAlert[];
  risk_predictions: RiskPrediction[];
  vendor_recommendations: VendorRecommendation[];
}

export interface SpendForecast {
  period: string;
  predicted_spend: number;
  confidence_interval: [number, number];
  factors: string[];
}

export interface BudgetAlert {
  matter_id: string;
  matter_name: string;
  alert_type: 'approaching_limit' | 'exceeded' | 'unusual_spending';
  severity: 'low' | 'medium' | 'high';
  current_spend: number;
  budget: number;
  projected_overrun: number;
  recommendations: string[];
}

export interface RiskPrediction {
  entity_id: string;
  entity_type: 'matter' | 'vendor' | 'invoice';
  risk_type: string;
  probability: number;
  potential_impact: number;
  predicted_date: string;
  mitigation_suggestions: string[];
}

export interface VendorRecommendation {
  matter_id: string;
  recommended_vendors: RecommendedVendor[];
  reasoning: string;
  confidence: number;
}

export interface RecommendedVendor {
  vendor_id: string;
  vendor_name: string;
  match_score: number;
  estimated_cost: number;
  estimated_duration: number;
  success_probability: number;
  reasons: string[];
}

// External API Integration Models

export interface MarketData {
  symbol: string;
  price: number;
  change: number;
  change_percentage: number;
  volume: number;
  market_cap: number;
  updated_at: string;
}

export interface EconomicIndicator {
  indicator: string;
  value: number;
  previous_value: number;
  change: number;
  date: string;
  source: string;
}

export interface RegulatoryUpdate {
  id: string;
  title: string;
  summary: string;
  source: string;
  regulation_type: string;
  effective_date: string;
  impact_level: 'low' | 'medium' | 'high';
  affected_industries: string[];
  url: string;
  published_at: string;
}

export interface PatentData {
  patent_number: string;
  title: string;
  abstract: string;
  inventors: string[];
  assignee: string;
  filing_date: string;
  grant_date: string;
  status: string;
  classifications: string[];
  related_matters?: string[];
}

export interface CompanyData {
  name: string;
  legal_name: string;
  domain: string;
  industry: string;
  size: string;
  founded: number;
  revenue: number;
  employees: number;
  address: Address;
  social_profiles: any;
  risk_score: number;
  compliance_status: string;
}
