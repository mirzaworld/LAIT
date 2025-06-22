import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import ApiHealthIndicator from '../ApiHealthIndicator';

// Mock fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('ApiHealthIndicator', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  it('renders with checking status initially', () => {
    render(<ApiHealthIndicator />);
    expect(screen.getByText('Checking API...')).toBeInTheDocument();
  });

  it('shows online status when API is healthy', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: 'OK'
    });

    render(<ApiHealthIndicator />);
    
    await waitFor(() => {
      expect(screen.getByText('API Online')).toBeInTheDocument();
    });
  });

  it('shows offline status when API is unreachable', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    render(<ApiHealthIndicator />);
    
    await waitFor(() => {
      expect(screen.getByText('API Offline')).toBeInTheDocument();
    });
  });

  it('shows degraded status when API returns error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error'
    });

    render(<ApiHealthIndicator />);
    
    await waitFor(() => {
      expect(screen.getByText('API Degraded')).toBeInTheDocument();
    });
  });

  it('toggles details panel when clicked', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: 'OK'
    });

    render(<ApiHealthIndicator />);
    
    await waitFor(() => {
      expect(screen.getByText('API Online')).toBeInTheDocument();
    });

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(screen.getByText('API Status')).toBeInTheDocument();
    expect(screen.getByText('Refresh')).toBeInTheDocument();
  });

  it('displays response time when available', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: 'OK'
    });

    render(<ApiHealthIndicator />);
    
    await waitFor(() => {
      expect(screen.getByText('API Online')).toBeInTheDocument();
    });

    const button = screen.getByRole('button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Response Time:/)).toBeInTheDocument();
    });
  });

  it('displays error message when API fails', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Connection timeout'));

    render(<ApiHealthIndicator />);
    
    await waitFor(() => {
      expect(screen.getByText('API Offline')).toBeInTheDocument();
    });

    const button = screen.getByRole('button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Connection timeout')).toBeInTheDocument();
    });
  });
}); 