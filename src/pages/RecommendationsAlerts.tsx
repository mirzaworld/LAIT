import React from 'react';

const RecommendationsAlerts: React.FC = () => {
  const recommendations = [
    {
      id: 1,
      text: 'Consider shifting work from Firm A (avg rate $450/hr) to Firm B ($350/hr) — potential savings $10K.',
    },
    {
      id: 2,
      text: 'Reduce reliance on Firm C for routine matters to save $5K annually.',
    },
  ];

  const alerts = [
    {
      id: 1,
      type: 'Budget',
      severity: 'High',
      message: 'IP Litigation matter has exceeded 90% of allocated budget.',
    },
    {
      id: 2,
      type: 'Anomaly',
      severity: 'Medium',
      message: 'Baker McKenzie submitted 3x normal hours for Q4.',
    },
  ];

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold text-gray-900">Recommendations & Alerts</h1>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Savings Suggestions</h3>
        <ul className="space-y-4">
          {recommendations.map((rec) => (
            <li key={rec.id} className="p-4 border border-gray-200 rounded-lg bg-gray-50">
              <p className="text-sm text-gray-700">{rec.text}</p>
            </li>
          ))}
        </ul>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Alerts</h3>
        <ul className="space-y-4">
          {alerts.map((alert) => (
            <li
              key={alert.id}
              className={`p-4 border border-gray-200 rounded-lg ${
                alert.severity === 'High' ? 'bg-danger-50' : 'bg-warning-50'
              }`}
            >
              <p className="text-sm text-gray-700">
                <strong>{alert.type}:</strong> {alert.message}
              </p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default RecommendationsAlerts;
