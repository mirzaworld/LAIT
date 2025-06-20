import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Area, AreaChart
} from 'recharts';
import { 
  Brain, TrendingUp, FileText, Users, DollarSign, AlertTriangle,
  CheckCircle, Clock, Target, Briefcase, Shield, Zap
} from 'lucide-react';

const EnhancedDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [matters, setMatters] = useState([]);
  const [mlStatus, setMlStatus] = useState(null);
  const [workflowStatus, setWorkflowStatus] = useState(null);
  const [budgetForecast, setBudgetForecast] = useState(null);
  const [anomalies, setAnomalies] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);

        // Fetch core metrics
        const metricsResponse = await fetch('http://localhost:5003/api/dashboard/metrics');
        const metricsData = await metricsResponse.json();
        setMetrics(metricsData);

        // Fetch matters
        const mattersResponse = await fetch('http://localhost:5003/api/matters');
        const mattersData = await mattersResponse.json();
        setMatters(mattersData);

        // Fetch ML status
        const mlResponse = await fetch('http://localhost:5003/api/ml/test');
        const mlData = await mlResponse.json();
        setMlStatus(mlData);

        // Fetch workflow status
        const workflowResponse = await fetch('http://localhost:5003/api/workflow/electronic-billing');
        const workflowData = await workflowResponse.json();
        setWorkflowStatus(workflowData);

        // Fetch budget forecast
        const forecastResponse = await fetch('http://localhost:5003/api/ml/budget-forecast', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ matter_id: 'MAT-001', time_horizon: 6 })
        });
        const forecastData = await forecastResponse.json();
        setBudgetForecast(forecastData);

        // Fetch anomalies
        const anomalyResponse = await fetch('http://localhost:5003/api/ml/anomaly-detection', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({})
        });
        const anomalyData = await anomalyResponse.json();
        setAnomalies(anomalyData);

      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading Enhanced Dashboard...</span>
      </div>
    );
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Enhanced Legal Intelligence Dashboard</h1>
          <p className="text-gray-600 mt-1">AI-powered legal spend optimization and analytics</p>
        </div>
        <div className="flex space-x-2">
          <Badge variant="outline" className="bg-green-50 text-green-700">
            <CheckCircle className="w-4 h-4 mr-1" />
            All Systems Active
          </Badge>
          <Badge variant="outline" className="bg-blue-50 text-blue-700">
            <Brain className="w-4 h-4 mr-1" />
            AI Enhanced
          </Badge>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-l-4 border-l-blue-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Legal Spend</p>
                <p className="text-2xl font-bold text-gray-900">
                  {metrics ? formatCurrency(metrics.total_spend) : '...'}
                </p>
                <p className="text-xs text-green-600 flex items-center mt-1">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  +{metrics?.spend_change_percentage || 0}% from last period
                </p>
              </div>
              <DollarSign className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Matters</p>
                <p className="text-2xl font-bold text-gray-900">
                  {matters?.length || 0}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {matters?.filter(m => m.status === 'active').length || 0} in progress
                </p>
              </div>
              <Briefcase className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-yellow-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Risk Alerts</p>
                <p className="text-2xl font-bold text-gray-900">
                  {anomalies?.anomalies_detected || 0}
                </p>
                <p className="text-xs text-yellow-600 flex items-center mt-1">
                  <AlertTriangle className="w-3 h-3 mr-1" />
                  {anomalies?.anomaly_rate?.toFixed(1) || 0}% anomaly rate
                </p>
              </div>
              <Shield className="w-8 h-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Automation Rate</p>
                <p className="text-2xl font-bold text-gray-900">
                  {workflowStatus?.processing_stats?.automation_rate?.toFixed(1) || 0}%
                </p>
                <p className="text-xs text-purple-600 flex items-center mt-1">
                  <Zap className="w-3 h-3 mr-1" />
                  {workflowStatus?.processing_stats?.invoices_processed_today || 0} today
                </p>
              </div>
              <Brain className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="analytics" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="matters">Matter Management</TabsTrigger>
          <TabsTrigger value="ml">AI Insights</TabsTrigger>
          <TabsTrigger value="workflow">Automation</TabsTrigger>
          <TabsTrigger value="forecasting">Forecasting</TabsTrigger>
        </TabsList>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Monthly Spend Trend</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={metrics?.trend_data?.monthly_spend || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis />
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                    <Area type="monotone" dataKey="amount" stroke="#0088FE" fill="#0088FE" fillOpacity={0.6} />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Invoice Processing Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Processed Today</span>
                    <Badge className="bg-green-100 text-green-800">
                      {workflowStatus?.processing_stats?.invoices_processed_today || 0}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Automation Rate</span>
                    <Badge className="bg-blue-100 text-blue-800">
                      {workflowStatus?.processing_stats?.automation_rate?.toFixed(1) || 0}%
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Error Rate</span>
                    <Badge className="bg-red-100 text-red-800">
                      {workflowStatus?.processing_stats?.error_rate?.toFixed(1) || 0}%
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Matter Management Tab */}
        <TabsContent value="matters" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Active Matters Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {matters.map((matter) => (
                  <div key={matter.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900">{matter.title}</h3>
                        <p className="text-sm text-gray-600">{matter.client}</p>
                        <div className="flex items-center space-x-4 mt-2">
                          <Badge className={getStatusColor(matter.status)}>
                            {matter.status}
                          </Badge>
                          <span className="text-sm text-gray-500">Phase: {matter.phase}</span>
                          <span className="text-sm text-gray-500">Priority: {matter.priority}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">Budget: {formatCurrency(matter.budget)}</p>
                        <p className="text-sm text-gray-600">Spent: {formatCurrency(matter.spent)}</p>
                        <div className="w-24 bg-gray-200 rounded-full h-2 mt-1">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${(matter.spent / matter.budget) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Insights Tab */}
        <TabsContent value="ml" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Brain className="w-5 h-5 mr-2" />
                  ML Model Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {mlStatus && Object.entries(mlStatus.models).map(([model, status]) => (
                    <div key={model} className="flex justify-between items-center">
                      <span className="text-sm font-medium capitalize">
                        {model.replace('_', ' ')}
                      </span>
                      <Badge className={status ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                        {status ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <AlertTriangle className="w-5 h-5 mr-2" />
                  Detected Anomalies
                </CardTitle>
              </CardHeader>
              <CardContent>
                {anomalies?.anomalies?.length > 0 ? (
                  <div className="space-y-3">
                    {anomalies.anomalies.slice(0, 3).map((anomaly, index) => (
                      <Alert key={index} className="border-yellow-200">
                        <AlertTriangle className="h-4 w-4" />
                        <AlertDescription>
                          <div className="font-medium">{anomaly.vendor_name}</div>
                          <div className="text-sm text-gray-600">
                            Score: {anomaly.anomaly_score} - {anomaly.recommendation}
                          </div>
                        </AlertDescription>
                      </Alert>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">No anomalies detected</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Workflow Tab */}
        <TabsContent value="workflow" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Workflow Features</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {workflowStatus && Object.entries(workflowStatus.features).map(([feature, enabled]) => (
                    <div key={feature} className="flex justify-between items-center">
                      <span className="text-sm font-medium capitalize">
                        {feature.replace('_', ' ')}
                      </span>
                      <Badge className={enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                        {enabled ? 'Enabled' : 'Disabled'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Processing Statistics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600">
                      {workflowStatus?.processing_stats?.automation_rate?.toFixed(1) || 0}%
                    </div>
                    <div className="text-sm text-gray-600">Automation Rate</div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-center">
                    <div>
                      <div className="text-xl font-semibold">
                        {workflowStatus?.processing_stats?.invoices_processed_today || 0}
                      </div>
                      <div className="text-xs text-gray-600">Processed Today</div>
                    </div>
                    <div>
                      <div className="text-xl font-semibold text-red-600">
                        {workflowStatus?.processing_stats?.error_rate?.toFixed(1) || 0}%
                      </div>
                      <div className="text-xs text-gray-600">Error Rate</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Forecasting Tab */}
        <TabsContent value="forecasting" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="w-5 h-5 mr-2" />
                Budget Forecast - 6 Month Projection
              </CardTitle>
            </CardHeader>
            <CardContent>
              {budgetForecast ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {formatCurrency(budgetForecast.total_predicted_spend)}
                      </div>
                      <div className="text-sm text-gray-600">Total Predicted Spend</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {budgetForecast.accuracy_estimate?.toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600">Accuracy Estimate</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {budgetForecast.forecast_horizon}
                      </div>
                      <div className="text-sm text-gray-600">Months Projected</div>
                    </div>
                  </div>
                  
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={budgetForecast.monthly_forecast}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip formatter={(value) => formatCurrency(value)} />
                      <Line type="monotone" dataKey="predicted_spend" stroke="#0088FE" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <p className="text-center text-gray-500">Loading forecast data...</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default EnhancedDashboard;
