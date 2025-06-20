import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import Dashboard from '../pages/Dashboard';
import InvoiceUpload from '../pages/UploadInvoice';
import * as apiServices from '../services/api';

// Mock API calls
jest.mock('../services/api');
const mockedApi = apiServices as jest.Mocked<typeof apiServices>;

describe('Dashboard Component', () => {
  beforeEach(() => {
    mockedApi.get.mockResolvedValue({
      data: {
        total_spend: 1000000,
        flagged_items_count: 5,
        vendor_count: 10,
        recent_invoices: []
      }
    });
  });

  it('renders dashboard with metrics', async () => {
    render(
      <AuthProvider>
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Total Spend/i)).toBeInTheDocument();
      expect(screen.getByText(/\$1,000,000/i)).toBeInTheDocument();
      expect(screen.getByText(/5/i)).toBeInTheDocument(); // flagged items
    });
  });

  it('handles API errors gracefully', async () => {
    mockedApi.get.mockRejectedValue(new Error('API Error'));

    render(
      <AuthProvider>
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Error loading dashboard data/i)).toBeInTheDocument();
    });
  });
});

describe('Invoice Upload Component', () => {
  const mockFile = new File(['test pdf content'], 'test.pdf', { type: 'application/pdf' });

  beforeEach(() => {
    mockedApi.post.mockResolvedValue({
      data: {
        id: 1,
        status: 'processing'
      }
    });
  });

  it('allows PDF file upload', async () => {
    render(
      <AuthProvider>
        <BrowserRouter>
          <InvoiceUpload />
        </BrowserRouter>
      </AuthProvider>
    );

    const input = screen.getByLabelText(/choose file/i);
    fireEvent.change(input, { target: { files: [mockFile] } });

    const submitButton = screen.getByRole('button', { name: /upload/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockedApi.post).toHaveBeenCalledWith('/api/invoices', expect.any(FormData));
    });
  });

  it('shows error for non-PDF files', async () => {
    const invalidFile = new File(['test'], 'test.txt', { type: 'text/plain' });

    render(
      <AuthProvider>
        <BrowserRouter>
          <InvoiceUpload />
        </BrowserRouter>
      </AuthProvider>
    );

    const input = screen.getByLabelText(/choose file/i);
    fireEvent.change(input, { target: { files: [invalidFile] } });

    expect(screen.getByText(/only pdf files are allowed/i)).toBeInTheDocument();
  });

  it('handles upload errors', async () => {
    mockedApi.post.mockRejectedValue(new Error('Upload failed'));

    render(
      <AuthProvider>
        <BrowserRouter>
          <InvoiceUpload />
        </BrowserRouter>
      </AuthProvider>
    );

    const input = screen.getByLabelText(/choose file/i);
    fireEvent.change(input, { target: { files: [mockFile] } });

    const submitButton = screen.getByRole('button', { name: /upload/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/failed to upload invoice/i)).toBeInTheDocument();
    });
  });
});
