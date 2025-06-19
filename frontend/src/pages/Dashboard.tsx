import React, { useEffect, useState } from 'react';
import api from '../api';

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<any>(null);
  useEffect(() => {
    api.get('/analytics/summary').then(res => setSummary(res.data));
  }, []);
  return (
    <div>
      <h1>Dashboard</h1>
      {summary ? (
        <div>
          <div>Total Spend: ${summary.total_spend}</div>
          <div>Flagged Line Items: {summary.flagged_line_items}</div>
        </div>
      ) : (
        <div>Loading...</div>
      )}
    </div>
  );
};
export default Dashboard;
