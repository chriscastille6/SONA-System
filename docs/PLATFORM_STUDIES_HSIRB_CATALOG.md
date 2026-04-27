# Platform studies catalog (Django / HSIRB)

The People Analytics Lab **Studies** tab can load IRB-visible studies directly from this app—**no Supabase** for that list.

## Endpoints (public GET)

- **List:** `/api/platform/studies/`  
  Returns `{ "studies": [ ... ] }` for slugs whitelisted in `platform_studies_catalog` (`goals-refs`, `hr-sjt`), only rows matching `Study.active_approved`.

- **Detail:** `/api/platform/studies/<uuid>/`  
  Same payload shape as one list item; `404` if not active/approved or not whitelisted.

If the site uses `FORCE_SCRIPT_NAME` (e.g. `/hsirb`), prefix those paths: `/hsirb/api/platform/studies/`.

## Participant URLs

- **HR SJT:** If `external_link` has no `study=` query param, the serializer appends `?study=<Study.id>` (or `&study=` if the URL already has a query string).

## HR-SJT UUID

The UUID is **not in git**; it is created when the study row is created (e.g. `add_hr_sjt_study_online`). On the server:

```bash
python manage.py print_study_uuid --slug hr-sjt
```

## Platform frontend

`Psychological Assessments/platform/js/config.js` can set:

```js
window.HSIRB_PLATFORM_STUDIES_URL = '/hsirb/api/platform/studies/';
```

`api.js` merges this catalog with the Node `/studies` API and local JSON (deduped by `id`).

## Survey software

Listing and “open when IRB approves” need **no** changes inside Qualtrics or the HR SJT app for approval gating—the **Django** queryset is the source of truth. Optional later: credit callback or `?participant=` on the survey URL.
