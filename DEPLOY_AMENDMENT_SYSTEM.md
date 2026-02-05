# Deploy Protocol Amendment System & Coming Soon Indicator

## Steps to Deploy to Production Server

```bash
# 1. SSH to server
ssh ccastille@bayoupal

# 2. Navigate to project directory
cd ~/hsirb-system

# 3. Activate virtual environment
source venv/bin/activate

# 4. Pull latest code
git pull origin main

# 5. Run migrations (creates protocol_amendments table)
python manage.py migrate

# 6. Fix Jon Murphy accounts (merge test account into real account)
python manage.py fix_jon_murphy_accounts

# 7. Populate TRO protocol details and create Loss Aversion amendment
python manage.py populate_tro_protocol_details

# 8. Restart Gunicorn service
echo "nsutemppasswd123" | sudo -S systemctl restart hsirb-system

# 9. Verify service is running
sudo systemctl status hsirb-system
```

## What This Deploys

1. **Protocol Amendment System**
   - New `ProtocolAmendment` model and database table
   - Amendment create/detail/review/list pages
   - Amendment workflow (pending → approved/rejected/R&R)

2. **TRO Protocol Details**
   - All protocol fields populated from PDF
   - Complete protocol information visible

3. **Loss Aversion Amendment**
   - Amendment `IRBE20251031-005CBA-AMD-01` created
   - Assigned to Jon Murphy for review
   - Includes endowment effect and correlate measures

4. **Coming Soon Indicator**
   - Shows for studies with `irb_status='pending'` and no protocol
   - EI Fluid Intelligence study will show "Coming Soon"

5. **Jon Murphy Account Fix**
   - Merges test account into `jonathan.murphy@nicholls.edu`
   - Transfers all protocol assignments

## Verification After Deployment

1. **Check Amendment System:**
   - Log in as PI (Martin Meder or Christopher Castille)
   - Go to TRO study → Protocol Submission detail
   - Should see "Amendments" section with Loss Aversion amendment

2. **Check Jon Murphy Access:**
   - Log in as `jonathan.murphy@nicholls.edu`
   - Go to Protocol Submissions
   - Should see "Pending Amendments Requiring Review" section
   - Click amendment to review and approve

3. **Check Coming Soon:**
   - View EI Fluid Intelligence study
   - Should show yellow "Coming Soon" badge

## Troubleshooting

If migrations fail:
```bash
# Check migration status
python manage.py showmigrations studies

# If needed, fake the amendment migration (if table already exists)
python manage.py migrate studies 0019 --fake
```

If service won't restart:
```bash
# Check logs
sudo journalctl -u hsirb-system -n 50

# Check for syntax errors
python manage.py check
```
