# LAIT Frontend Codebase Guide

This guide provides an overview of the frontend codebase structure, key concepts, and how the major components work together.

## Project Overview

The LAIT (Legal AI Intelligence Toolkit) is a web application for legal spend analysis and optimization. The frontend is built with:

- React 18.x
- TypeScript
- TailwindCSS for styling
- React Router for navigation
- Recharts and Chart.js for data visualization
- Various custom hooks for data fetching and state management

## Directory Structure

```text
/src
├── components/        # Reusable UI components
├── context/           # React context providers
├── data/              # Static data and mock data
├── hooks/             # Custom React hooks
├── pages/             # Page components
├── services/          # API services and utilities
├── types/             # TypeScript type definitions
├── App.tsx            # Main application component
└── main.tsx           # Application entry point
```

## Key Concepts

### Authentication Flow

Authentication is managed through the `AuthContext` (`/src/context/AuthContext.tsx`). The frontend supports:

1. Username/password authentication
2. JWT token storage in localStorage
3. Protected routes via the `ProtectedRoute` component in App.tsx
4. Auto-login for development via `setDevelopmentToken()`

### API Communication

API calls are primarily managed through:

1. **services/api.ts** - Contains core API functions for data fetching
2. **hooks/useApi.ts** - React hooks that wrap the API functions
3. **hooks/useAnalytics.ts** - Custom hooks for analytics-specific data

The application is configured to connect to the backend at `http://localhost:5003` by default.

### Component Hierarchy

- **App.tsx** - Sets up routing and wraps the application in context providers
- **Layout.tsx** - Provides the common layout (sidebar, header, etc.)
- **Page Components** - Specific page content (Dashboard, Analytics, etc.)
- **UI Components** - Reusable UI elements used across pages

## Data Flow

1. **API Request** - Custom hooks like `useDashboardMetrics()` fetch data from the backend
2. **State Management** - Data is stored in component state or context
3. **Rendering** - Components render based on the current state
4. **User Interaction** - Actions might trigger new API calls or state updates

## Key Files

- **/src/services/api.ts** - Core API interaction functions
- **/src/hooks/useApi.ts** - React hooks for data fetching
- **/src/hooks/useAnalytics.ts** - Advanced analytics hooks
- **/src/context/AuthContext.tsx** - Authentication management
- **/src/pages/Dashboard.tsx** - Main dashboard with metrics and charts
- **/src/pages/EnhancedDashboard.tsx** - Advanced dashboard with ML features
- **/src/components/VendorAnalysis.tsx** - Detailed vendor analytics

## API Endpoints

The frontend expects these main API endpoints:

- `/api/health` - Backend health check
- `/api/dashboard/metrics` - Main dashboard metrics
- `/api/invoices` - Invoice data
- `/api/vendors` - Vendor data
- `/api/matters` - Legal matters
- `/api/ml/*` - Machine learning services
- `/api/workflow/*` - Workflow status endpoints
- `/api/analytics/*` - Advanced analytics

## Development Tools

- **API Tester** - `/src/components/ApiTester.tsx` for testing API connections
- **API Diagnostics** - `/api_diagnostics.html` and `/api_diagnostics.js` for troubleshooting
- **ApiStatus Component** - Quick status indicators for service health

## Troubleshooting

1. **Connection Issues**
   - Check backend is running at `http://localhost:5003`
   - Verify proxy settings in `vite.config.ts`
   - Use the API diagnostics tools

2. **Authentication Problems**
   - Check localStorage for 'lait_token'
   - Ensure protected routes are working properly

3. **Data Loading Issues**
   - Check network requests in browser developer tools
   - Verify correct error handling in hooks

## Adding New Features

1. **New Components**
   - Add to `/src/components/`
   - Ensure proper TypeScript typing

2. **New Pages**
   - Create in `/src/pages/`
   - Add route in `App.tsx`

3. **New API Integration**
   - Add API functions to `services/api.ts`
   - Create custom hooks in `hooks/` if needed

4. **New Analytics**
   - Extend `hooks/useAnalytics.ts` with new hooks
   - Add visualization components as needed
