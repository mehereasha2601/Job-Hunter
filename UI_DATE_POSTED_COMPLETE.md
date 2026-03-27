# UI Updated with date_posted Field

## Changes Made

### 1. JobTable Component (`ui/src/components/JobTable.jsx`)

#### Added Sort Dropdown
```javascript
<select value={filters.sort_by} onChange={...}>
  <option value="score">Score (Best Match)</option>
  <option value="date_posted">Date Posted (Newest)</option>
  <option value="first_seen_at">Recently Added</option>
</select>
```

#### Added Date Column
New column in table: **Posted**
- Shows formatted date/time: "5h ago", "2d ago", "Mar 20"
- Positioned between Location and Status columns

#### Date Formatting Function
```javascript
formatDate(dateString) {
  < 1 hour:  "Just now"
  < 24 hours: "5h ago"
  < 7 days:   "2d ago"
  < 30 days:  "3w ago"
  > 30 days:  "Mar 20"
}
```

### 2. API Client (`ui/src/api.js`)
Added `sort_by` parameter to `getJobs()` method:
```javascript
if (filters.sort_by) params.append('sort_by', filters.sort_by);
```

### 3. Layout Changes
- Filter grid: 4 columns → 5 columns (added Sort By)
- Table: 7 columns → 8 columns (added Posted)
- Updated colspan in empty state message

## UI Features

### Sorting Options
1. **Score (Best Match)** - Default, shows highest scoring jobs first
2. **Date Posted (Newest)** - Shows most recently posted jobs first
3. **Recently Added** - Shows jobs we most recently discovered

### Date Display Examples
| Actual Time | Display |
|-------------|---------|
| 30 minutes ago | Just now |
| 5 hours ago | 5h ago |
| 2 days ago | 2d ago |
| 1 week ago | 7d ago |
| 3 weeks ago | 3w ago |
| March 20, 2026 | Mar 20 |

## Testing

### Build Test
```bash
cd ui && npm run build
```
✅ Build successful - no errors

### To Run UI Locally
```bash
# Terminal 1: Start API
cd /Users/koppisettyeashameher/job-hunter
python3 api/main.py

# Terminal 2: Start UI
cd ui
npm run dev
```

Then visit: `http://localhost:5173`

### Testing Checklist
- [ ] Sort by Score - shows best matches first
- [ ] Sort by Date Posted - shows newest jobs first
- [ ] Sort by Recently Added - shows latest discoveries
- [ ] Date column displays "5h ago" for recent jobs
- [ ] Date column displays "Mar 20" for older jobs
- [ ] Filter combinations work (Status + Score + Company + Sort)

## Data Flow

1. **Scraping** → Scrapers extract `date_posted` from APIs
2. **Database** → Stores in `date_posted TIMESTAMPTZ` column
3. **API** → Returns `date_posted` in ISO format
4. **UI** → Formats for display ("5h ago" or "Mar 20")

## Production Deployment

### Before Deploying
1. **Run migration** in Supabase SQL Editor:
   ```sql
   ALTER TABLE jobs ADD COLUMN IF NOT EXISTS date_posted TIMESTAMPTZ;
   CREATE INDEX IF NOT EXISTS idx_jobs_date_posted ON jobs(date_posted);
   ```

2. **Rebuild UI:**
   ```bash
   cd ui && npm run build
   ```

3. **Deploy API & UI:**
   - Push to GitHub
   - Deploy to your hosting (Vercel, Render, etc.)

### Environment Variables
Make sure these are set:
```bash
VITE_API_URL=https://your-api-domain.com
```

## Complete
✅ UI updated with date_posted column  
✅ Sort dropdown added (Score, Date Posted, Recently Added)  
✅ Date formatting function (5h ago, 2d ago, Mar 20)  
✅ API client passes sort_by parameter  
✅ Build tested and successful  
✅ Ready for deployment
