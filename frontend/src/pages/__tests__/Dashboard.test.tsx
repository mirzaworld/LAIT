import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../Dashboard';

// Mock the API service
vi.mock('../../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

// Mock the analytics hook
vi.mock('../../hooks/useAnalytics', () => ({
  default: () => ({
    dashboardMetrics: {
      totalSpend: 2500000,
      invoiceCount: 150,
      vendorCount: 25,
      averageRiskScore: 35,
      spendChange: 12.5,
      recentInvoices: [
        {
          id: 1,
          vendor: 'Test Law Firm',
          amount: 50000,
          date: '2024-01-15',
          status: 'approved',
          riskScore: 25
        }
      ],
      topVendors: [
        {
          name: 'Top Law Firm',
          totalSpend: 500000
        }
      ]
    },
    loading: false,
    error: null,
    refetch: vi.fn()
  })
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard with metrics', async () => {
    renderWithRouter(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('$2,500,000')).toBeInTheDocument(); // totalSpend
      expect(screen.getByText('150')).toBeInTheDocument(); // invoiceCount
      expect(screen.getByText('25')).toBeInTheDocument(); // vendorCount
    });
  });

  it('displays recent invoices', async () => {
    renderWithRouter(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Law Firm')).toBeInTheDocument();
      expect(screen.getByText('$50,000')).toBeInTheDocument();
    });
  });

  it('displays top vendors', async () => {
    renderWithRouter(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Top Law Firm')).toBeInTheDocument();
      expect(screen.getByText('$500,000')).toBeInTheDocument();
    });
  });

  it('shows spend change indicator', async () => {
    renderWithRouter(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('+12.5%')).toBeInTheDocument();
    });
  });

  it('displays risk score', async () => {
    renderWithRouter(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('35')).toBeInTheDocument(); // averageRiskScore
    });
  });
}); 