# Deploy TRO Study to Online PRAMS

## Quick Deploy Steps

### Option 1: SSH and Run Command (Safest)

1. **SSH to the server:**
   ```bash
   ssh bayoupal
   ```

2. **Navigate to the project:**
   ```bash
   cd ~/hsirb-system
   source venv/bin/activate
   ```

3. **Pull latest code (if command exists):**
   ```bash
   git pull origin main
   ```

4. **Run the command:**
   ```bash
   python manage.py add_tro_study_online
   ```

5. **Verify it worked:**
   ```bash
   python manage.py shell -c "from apps.studies.models import Study, ProtocolSubmission; s = Study.objects.get(slug='conjoint-analysis'); print(f'IRB Status: {s.irb_status}'); print(f'IRB Number: {s.irb_number}'); ps = ProtocolSubmission.objects.raw('SELECT * FROM protocol_submissions WHERE protocol_number = %s', ['IRBE20251031-005CBA']); print(f'Protocol: {list(ps)[0].protocol_number if ps else \"Not found\"}')"
   ```

### Option 2: Push Code and Run Command

1. **Commit the new command:**
   ```bash
   cd "/Users/ccastille/Documents/GitHub/SONA System"
   git add apps/studies/management/commands/add_tro_study_online.py
   git commit -m "Add command to deploy TRO study to online database"
   git push
   ```

2. **SSH to server and run:**
   ```bash
   ssh bayoupal
   cd ~/hsirb-system
   git pull origin main
   source venv/bin/activate
   python manage.py add_tro_study_online
   ```

## What This Does

- ✅ Finds or creates the TRO/Conjoint Analysis study
- ✅ Creates the approved protocol submission with protocol number `IRBE20251031-005CBA`
- ✅ Copies approval PDF to media directory
- ✅ Copies protocol PDF to media directory
- ✅ Updates study IRB status to `approved`
- ✅ Sets all approval details (Jon Murphy as approver, dates, etc.)

## Verification

After running, check:
- https://bayoupal.nicholls.edu/hsirb/studies/researcher/ - Should show TRO study as approved
- https://bayoupal.nicholls.edu/hsirb/studies/protocol/submissions/ - Should show the approved protocol
