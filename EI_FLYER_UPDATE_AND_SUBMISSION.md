# EI Study Flyer: QR Code Update & Posting for Dr. Jon Murphy Review

## (i) Replace the QR Code with the Study Link

The flyer’s QR code has been replaced with one that points to the EI study.

### What was done

- **Study URL (QR destination):**  
  `https://bayoupal.nicholls.edu/platform/studies/study.html?id=local-study-001`
- **Updated flyer:** `Flyer_EI_Study.pdf` (in the project root).

### Regenerating the updated flyer yourself

1. Install dependencies (if needed):
   ```bash
   pip install PyMuPDF "qrcode[pil]"
   ```
2. Run the script. Uses `Flyer_EI_Study.pdf` as default input (exact EI layout).

   **With your custom QR image:**
   ```bash
   cd "/Users/ccastille/Documents/GitHub/SONA System"
   python3 scripts/update_flyer_qr.py Flyer_EI_Study.pdf Flyer_EI_Study_Updated.pdf --qr-image path/to/your_qr.png
   ```

   **Or generate QR from URL:**
   ```bash
   python3 scripts/update_flyer_qr.py --url "https://your-study-url/run/"
   ```

---

## (ii) Post the Updated Flyer for Review by Dr. Jon Murphy

Post the updated flyer so it’s visible to Dr. Murphy in the system. Two options:

### Option A: Study Update (recommended)

This makes the flyer visible on the study and on the IRB member dashboard.

1. Log in: **https://bayoupal.nicholls.edu/hsirb/accounts/login/**
2. Open the **Researcher Dashboard**:  
   **https://bayoupal.nicholls.edu/hsirb/studies/researcher/**
3. Open your **EI study** (e.g. EI × Dunning–Kruger or the study tied to your protocol).
4. Go to the study **Status** page (or the page where you can post updates).
5. Use **“Post an update”** (or equivalent):
   - **Message:** e.g. “Updated recruitment flyer with QR code linking to the study. Please use this version for IRB review.”
   - **Attachment:** upload `Flyer_EI_Study.pdf`.
6. Save/post the update.

Dr. Murphy will see this update (and the flyer) when he views the study or his IRB member dashboard.

### Option B: Submit Materials for Review (Recruitment Materials)

This adds the flyer to the study’s IRB review materials.

1. Log in and go to the **Researcher Dashboard** (link above).
2. Open your **EI study**.
3. Use **“Submit Materials for Review”** (or **“IRB Review”** → create/new review).
4. In the upload form, use the **“Recruitment Materials”** field and upload **`Flyer_EI_Study.pdf`**.
5. Submit the form.

The flyer will appear under the study’s IRB review documents. Dr. Murphy can open the protocol submission and the related IRB review to view it.

---

## Quick reference

| Item | Value |
|------|--------|
| Study participant link | https://bayoupal.nicholls.edu/platform/studies/study.html?id=local-study-001 |
| Updated flyer file | `Flyer_EI_Study.pdf` |
| Protocol submissions (Jon Murphy) | https://bayoupal.nicholls.edu/hsirb/studies/protocol/submissions/ |
| Script | `scripts/update_flyer_qr.py` |
