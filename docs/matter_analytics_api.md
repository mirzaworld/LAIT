# Matter Analytics API Documentation

This document describes the API endpoints for the Matter Analytics functionality in the Legal AI Spend Optimizer system.

## Matter Analytics Endpoints

### Get Matter Analytics Overview

`GET /api/analytics/matters`

Returns comparative analytics for all matters in the system, including spend, risk scores, and efficiency metrics.

**Parameters:**

- `date_from` (optional): Start date for analytics in YYYY-MM-DD format. Defaults to 1 year ago.
- `date_to` (optional): End date for analytics in YYYY-MM-DD format. Defaults to current date.

**Response Example:**

```json
{
  "matters": [
    {
      "id": "1",
      "name": "IP Litigation - TechCorp vs CompetitorX",
      "total_spend": 360000,
      "invoice_count": 3,
      "avg_risk_score": 5.2,
      "avg_hourly_rate": 450,
      "efficiency_score": 48
    }
  ],
  "benchmarks": {
    "avg_hourly_rate": 425,
    "avg_risk_score": 4.8
  },
  "date_range": {
    "from": "2024-06-18",
    "to": "2025-06-18"
  }
}
```

### Get Matter Risk Profile

`GET /api/analytics/matter/{matter_id}/risk_profile`

Returns a detailed risk analysis for a specific matter, including risk factors and an overall risk score.

**Parameters:**

- `matter_id`: The ID of the matter to analyze.

**Response Example:**

```json
{
  "matter_id": "1",
  "matter_name": "IP Litigation - TechCorp vs CompetitorX",
  "risk_score": 65,
  "risk_level": "medium",
  "risk_factors": [
    {
      "type": "budget_overrun",
      "severity": "medium",
      "description": "Budget utilization at 72.0%"
    },
    {
      "type": "partner_heavy",
      "severity": "medium",
      "description": "Partner-heavy staffing (48.0% of hours)"
    }
  ],
  "budget_utilization": 0.72
}
```

### Get Matter Expense Forecast

`GET /api/analytics/matter/{matter_id}/forecast`

Returns an ML-based forecast of the expected final cost and budget status for a specific matter.

**Parameters:**

- `matter_id`: The ID of the matter to analyze.

**Response Example:**

```json
{
  "matter_id": "1",
  "matter_name": "IP Litigation - TechCorp vs CompetitorX",
  "current_spend": 360000,
  "budget": 500000,
  "budget_utilization": 0.72,
  "invoice_count": 3,
  "projected_final_cost": 475000,
  "budget_variance_amount": -25000,
  "budget_variance_pct": -5.0,
  "remaining_budget": 140000,
  "projected_remaining_cost": 115000,
  "budget_status": "under_budget",
  "confidence_score": 0.85
}
```

## Technical Implementation Details

The Matter Analytics functionality is implemented using several machine learning approaches:

1. **Expense Forecasting**: Uses a Gradient Boosting regression model trained on historical matter data to predict the final cost as a percentage of budget based on current spending patterns, timekeeper composition, and matter characteristics.

2. **Risk Analysis**: Identifies risk factors based on budget utilization, rate consistency, staffing patterns, and timeline factors. Assigns a risk score and generates specific risk factors for each matter.

3. **Feature Extraction**: Transforms matter data including category, budget, status, and invoicing patterns into numerical features used for ML models.

The implementation can fall back to simpler extrapolation methods when insufficient data is available for ML-based predictions.
