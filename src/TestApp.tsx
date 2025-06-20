import React from 'react';

const TestApp: React.FC = () => {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>LAIT Test App</h1>
      <p>If you can see this, React is working!</p>
      <p>Current time: {new Date().toLocaleString()}</p>
      <div style={{ background: '#f0f0f0', padding: '10px', marginTop: '20px' }}>
        <h3>System Status</h3>
        <ul>
          <li>React: ✅ Working</li>
          <li>TypeScript: ✅ Working</li>
          <li>Vite: ✅ Working</li>
        </ul>
      </div>
    </div>
  );
};

export default TestApp;
