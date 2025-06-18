import React from 'react';

const SettingsIntegrations: React.FC = () => {
  const environmentVariables = [
    { name: 'DB_URL', value: 'postgres://user:password@localhost:5432/legalspend' },
    { name: 'S3_BUCKET', value: 'legal-invoices' },
    { name: 'SMTP_HOST', value: 'smtp.mailtrap.io' },
    { name: 'SMTP_USER', value: 'user@mailtrap.io' },
    { name: 'SMTP_PASS', value: 'password' },
    { name: 'SLACK_WEBHOOK_URL', value: 'https://hooks.slack.com/services/...' },
  ];

  const handleRetrainModels = () => {
    alert('Retraining models...');
    // Simulate API call
    setTimeout(() => {
      alert('Models retrained successfully!');
    }, 2000);
  };

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold text-gray-900">Settings & Integrations</h1>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Environment Variables</h3>
        <table className="w-full border border-gray-200 rounded-lg">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Variable</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Value</th>
            </tr>
          </thead>
          <tbody>
            {environmentVariables.map((env) => (
              <tr key={env.name} className="border-t">
                <td className="px-4 py-2 text-sm text-gray-700">{env.name}</td>
                <td className="px-4 py-2 text-sm text-gray-700">{env.value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Management</h3>
        <button
          onClick={handleRetrainModels}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
        >
          Retrain Models
        </button>
      </div>
    </div>
  );
};

export default SettingsIntegrations;
