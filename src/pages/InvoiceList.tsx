import React, { useState } from 'react';
import { useInvoices } from '../hooks/useApi';

const InvoiceList: React.FC = () => {
  const { invoices, loading, error } = useInvoices();
  const [filters, setFilters] = useState({ firm: '', matter: '', flaggedOnly: false });

  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
    const { name, value, type } = e.target as HTMLInputElement;
    const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined;
    setFilters((prevFilters) => ({
      ...prevFilters,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const filteredInvoices = invoices.filter((invoice) => {
    const matchesFirm = filters.firm ? invoice.vendor.includes(filters.firm) : true;
    const matchesMatter = filters.matter ? invoice.matter.includes(filters.matter) : true;
    const matchesFlagged = filters.flaggedOnly ? invoice.riskScore >= 70 : true;
    return matchesFirm && matchesMatter && matchesFlagged;
  });

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold text-gray-900">Reviewed Line-Items</h1>

      <div className="flex space-x-4">
        <select
          name="firm"
          value={filters.firm}
          onChange={handleFilterChange}
          className="border border-gray-300 rounded-lg py-2 px-3 shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="">All Firms</option>
          <option value="Morrison & Foerster LLP">Morrison & Foerster LLP</option>
          <option value="Baker McKenzie">Baker McKenzie</option>
          <option value="Latham & Watkins">Latham & Watkins</option>
        </select>

        <select
          name="matter"
          value={filters.matter}
          onChange={handleFilterChange}
          className="border border-gray-300 rounded-lg py-2 px-3 shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="">All Matters</option>
          <option value="IP Litigation">IP Litigation</option>
          <option value="M&A Advisory">M&A Advisory</option>
          <option value="Regulatory Compliance">Regulatory Compliance</option>
        </select>

        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            name="flaggedOnly"
            checked={filters.flaggedOnly}
            onChange={handleFilterChange}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="text-sm text-gray-700">Flagged Only</span>
        </label>
      </div>

      {loading ? (
        <div className="flex items-center justify-center p-8">
          <span className="text-gray-500">Loading invoices...</span>
        </div>
      ) : error ? (
        <div className="p-4 text-center text-danger-600 bg-danger-50 rounded-lg">
          <p>Error loading invoices. Please try again.</p>
        </div>
      ) : (
        <table className="w-full border border-gray-200 rounded-lg">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Invoice ID</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Date</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Description</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Hours</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Rate</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Total</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Flagged</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Overspend Probability (%)</th>
            </tr>
          </thead>
          <tbody>
            {filteredInvoices.map((invoice) => (
              <tr
                key={invoice.id}
                className={`border-t ${invoice.riskScore >= 70 ? 'bg-danger-50' : ''}`}
              >
                <td className="px-4 py-2 text-sm text-gray-700">{invoice.id}</td>
                <td className="px-4 py-2 text-sm text-gray-700">{invoice.date}</td>
                <td className="px-4 py-2 text-sm text-gray-700">{invoice.description}</td>
                <td className="px-4 py-2 text-sm text-gray-700">{invoice.hours}</td>
                <td className="px-4 py-2 text-sm text-gray-700">{invoice.rate}</td>
                <td className="px-4 py-2 text-sm text-gray-700">{invoice.total}</td>
                <td className="px-4 py-2 text-sm text-gray-700">{invoice.riskScore >= 70 ? 'Yes' : 'No'}</td>
                <td className="px-4 py-2 text-sm text-gray-700">{invoice.riskScore}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default InvoiceList;
