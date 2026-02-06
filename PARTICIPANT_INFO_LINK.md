# "Read full participant information document" link

On the **assessment platform** “Your Rights and Options” page (People Analytics Lab of the Bayou), the link **“Read full participant information document →”** should point to the full consent/information page served by this SONA System.

## URL to use

The page is available at **two paths** (use whichever works on your deployment):

| Path | When to use |
|------|-------------------------------|
| **`/participant-information/`** | Short path; works at app root (recommended for links). |
| **`/studies/participant-information/`** | Under the studies app. |

- **Same server with path prefix (e.g. Bayoupal):**  
  If SONA runs under `/hsirb/`, use one of:
  - `https://bayoupal.nicholls.edu/hsirb/participant-information/`
  - `https://bayoupal.nicholls.edu/hsirb/studies/participant-information/`
- **Root deployment:**  
  If SONA is at the site root:
  - `https://your-domain.edu/participant-information/`
  - or `https://your-domain.edu/studies/participant-information/`

## In HTML (assessment platform)

With path prefix (e.g. Bayoupal):

```html
<a href="/hsirb/participant-information/" target="_blank" rel="noopener">Read full participant information document →</a>
```

Without prefix:

```html
<a href="/participant-information/" target="_blank" rel="noopener">Read full participant information document →</a>
```

Use a full URL if the assessment platform is on a different host than SONA.

## Contact info on the full document

The full page is rendered with contact details from this app’s settings (see `config/settings.py` and `env.example`). Defaults match the “Your Rights and Options” page:

- **Platform features:** Christopher Castille (christopher.castille@nicholls.edu)
- **IRB / rights as participant:** Dr. Alaina Daigle, 168 Ayo Hall, 985-448-4697, alania.daigle@nicholls.edu

Override via environment variables if needed.
