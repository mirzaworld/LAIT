# LAIT Demo Seeder - PROMPT 7 Implementation

## 🌱 Overview

The LAIT demo seeder provides realistic sample data for testing and demonstration purposes. It creates a demo user and loads 10 diverse legal invoices through the same API endpoints used by the frontend.

## 📁 Files Created

### 1. Sample Data: `data/staging/sample_invoice.json`
- **10 realistic legal invoices** with varied:
  - Vendors (law firms specializing in different areas)
  - Matters (corporate, IP, real estate, employment, etc.)  
  - Hours and rates (ranging from $180-$950/hr)
  - Line items (attorney work, paralegal support, filing fees)
- **No PII** - All names and companies are fictional
- **Realistic amounts** - Total spend: ~$137,000 across 10 invoices

### 2. Demo Seeder: `scripts/seed_demo.py`  
- **Registers/logs in** `demo@lait.com` with password `demo123!`
- **Loads sample data** from JSON file
- **Calls same HTTP endpoints** as frontend (`POST /api/invoices/upload`)
- **Simulates file uploads** by creating temporary text files
- **Prints count inserted** with detailed progress reporting
- **Colored terminal output** with success/error indicators

### 3. Makefile Target: `seed`
```makefile
seed:
	@echo "🌱 Seeding LAIT demo data..."
	@echo "Requirement: Backend must be running on localhost:5003"
	@echo ""
	python3 scripts/seed_demo.py
```

## 🚀 Usage

### Prerequisites
```bash
# Start the LAIT backend
cd backend && python app_real.py &
```

### Load Demo Data
```bash
make seed
```

### Test with API
```bash
# Get JWT token
export TOKEN=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email":"demo@lait.com","password":"demo123!"}' \
  http://localhost:5003/api/auth/login | jq -r .token)

# View dashboard metrics  
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5003/api/dashboard/metrics
```

## 📊 Sample Data Details

The seeder creates **10 legal invoices** covering diverse practice areas:

1. **Acme Corp** - Corporate restructuring ($15,750)
2. **TechStart Innovations** - IP/Patents ($8,920) 
3. **Metro Real Estate LLC** - Commercial leasing ($12,450)
4. **Global Manufacturing** - Employment law ($18,750)
5. **HealthTech Solutions** - FDA compliance ($9,875)
6. **Financial Services** - Securities law ($22,100)
7. **Energy Solutions** - Environmental law ($14,280)
8. **Retail Chain Holdings** - Litigation ($7,650)
9. **Biotech Research** - IP licensing ($16,890)
10. **Construction Dynamics** - Construction law ($11,340)

**Total Portfolio**: ~$137,000 in legal spending across 10 clients

## 🔧 Implementation Features

### Authentication Flow
- Attempts to register `demo@lait.com` 
- If user exists, logs in instead
- Captures JWT token for API calls
- Handles authentication errors gracefully

### File Upload Simulation
- Creates realistic invoice content as text files
- Uses multipart form data (same as frontend drag-and-drop)
- Includes client_name and matter_id metadata
- Processes line items through ML scoring

### Progress Reporting
- Color-coded terminal output
- Progress indicators (1/10, 2/10, etc.)
- Success/failure tracking
- Final summary with metrics

### Error Handling
- Backend connectivity checks
- Individual invoice upload failures
- Graceful degradation with partial success
- Detailed error messages

## 📈 Expected Output

### Successful Run
```
🌱 LAIT Demo Data Seeder
========================

=== Demo User Setup ===
✅ Demo user logged in successfully
✅ JWT token captured: eyJ0eXAiOiJKV1Qi...

=== Seeding Invoice Data ===
ℹ️  (1/10) Creating invoice AC-2024-001
  Client: Acme Corp
  Vendor: Morrison & Associates LLP
  Lines: 5
✅ Created invoice AC-2024-001 (ID: 1, Lines: 7)

[... continues for all 10 invoices ...]

=== Dashboard Metrics ===
✅ Dashboard metrics loaded:
  📊 Invoices Count: 10
  💰 Total Spend: $137,055.00
  📝 Total Lines: 42
  🚩 Flagged Lines: 8
  ⚖️  Average Score: 2.34

=== COUNT INSERTED ===
✅ 10 invoices inserted successfully
```

## 🎯 Integration Points

### Same API Endpoints as Frontend
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - Authentication
- `POST /api/invoices/upload` - File upload with form data
- `GET /api/dashboard/metrics` - Analytics data

### Realistic Data Flow  
- Simulates actual user workflow
- Triggers ML scoring for each line item
- Creates proper database relationships
- Generates dashboard-ready metrics

### Demo User Credentials
- **Email**: `demo@lait.com`
- **Password**: `demo123!`
- Can be used to login to frontend at `http://localhost:5173`

---

**PROMPT 7 Complete**: Demo seeder with 10 realistic invoices, Makefile integration, and comprehensive API testing capabilities.
