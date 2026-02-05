# Check CITI Certificates and OSF Link

## CITI Certificates

### Where They Should Be Stored:
- **On Server**: `~/hsirb-system/media/protocol_submissions/citi_certificates/YYYY/MM/`
- **Or**: `/var/www/html/hsirb/media/protocol_submissions/citi_certificates/YYYY/MM/`

### To Check on Server:
```bash
ssh bayoupal
ls -lh ~/hsirb-system/media/protocol_submissions/citi_certificates/*/* 2>/dev/null
# Or if symlinked:
ls -lh /var/www/html/hsirb/media/protocol_submissions/citi_certificates/*/* 2>/dev/null
```

### To Check in Database:
```bash
python manage.py shell -c "
from apps.studies.models import ProtocolSubmission
ps = ProtocolSubmission.objects.filter(protocol_number='IRBE20251031-005CBA').first()
if ps:
    print(f'CITI Certificate: {ps.citi_training_certificate.name if ps.citi_training_certificate else \"None\"}')
    if ps.citi_training_certificate:
        print(f'URL: {ps.citi_training_certificate.url}')
else:
    print('Protocol submission not found')
"
```

## OSF Link

### TRO Study OSF Link:
- **OSF Project ID**: `j9ghr`
- **OSF Link**: `https://osf.io/j9ghr/`

### To Verify OSF Link is Set:
```bash
python manage.py shell -c "
from apps.studies.models import Study
study = Study.objects.filter(slug='conjoint-analysis').first()
if study:
    print(f'OSF Enabled: {study.osf_enabled}')
    print(f'OSF Project ID: {study.osf_project_id}')
    print(f'OSF Link: {study.osf_link}')
else:
    print('Study not found')
"
```

### To Update OSF Link (if needed):
The command `add_tro_study_online` now sets the OSF link automatically. Run:
```bash
python manage.py add_tro_study_online
```
