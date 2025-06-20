import React from 'react';
import { Bar } from 'react-chartjs-2';
import '../utils/chartConfig';

const VendorPerformance: React.FC = () => {
  const metricsData = {
    labels: ['Firm A', 'Firm B', 'Firm C', 'Firm D', 'Firm E'],
    datasets: [
      {
        label: 'Avg. Rate ($)',
        data: [450, 350, 500, 400, 300],
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold text-gray-900">Law Firm Benchmarking</h1>

      <div className="mt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Metrics Table</h3>
        <table className="w-full border border-gray-200 rounded-lg">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Firm Name</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Avg. Rate</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">% Line-Items Flagged</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Diversity Score</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Success Rate</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-t">
              <td className="px-4 py-2 text-sm text-gray-700">Firm A</td>
              <td className="px-4 py-2 text-sm text-gray-700">$450</td>
              <td className="px-4 py-2 text-sm text-gray-700">10%</td>
              <td className="px-4 py-2 text-sm text-gray-700">85</td>
              <td className="px-4 py-2 text-sm text-gray-700">90%</td>
            </tr>
            <tr className="border-t">
              <td className="px-4 py-2 text-sm text-gray-700">Firm B</td>
              <td className="px-4 py-2 text-sm text-gray-700">$350</td>
              <td className="px-4 py-2 text-sm text-gray-700">5%</td>
              <td className="px-4 py-2 text-sm text-gray-700">80</td>
              <td className="px-4 py-2 text-sm text-gray-700">85%</td>
            </tr>
            <tr className="border-t">
              <td className="px-4 py-2 text-sm text-gray-700">Firm C</td>
              <td className="px-4 py-2 text-sm text-gray-700">$500</td>
              <td className="px-4 py-2 text-sm text-gray-700">15%</td>
              <td className="px-4 py-2 text-sm text-gray-700">75</td>
              <td className="px-4 py-2 text-sm text-gray-700">88%</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="mt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Bar Chart</h3>
        <Bar data={metricsData} options={{ responsive: true, plugins: { legend: { position: 'top' } } }} />
      </div>
    </div>
  );
};

export default VendorPerformance;
