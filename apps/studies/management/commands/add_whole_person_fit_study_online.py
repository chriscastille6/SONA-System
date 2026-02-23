"""
Add the Whole Person Fit study to the online database.
Reads study_config.json from apps/studies/assets/irb/whole-person-fit/.
If the config is missing, prints instructions and exits.
Safe to run on production; idempotent (get_or_create study).
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.studies.models import Study
from apps.studies.irb_utils import create_or_update_protocol_from_json

User = get_user_model()

# Default consent if not in config (minimal placeholder; replace via config or UI)
DEFAULT_CONSENT = (
    "You will be asked to complete surveys and assessments. "
    "You may receive course credit via the PRAMS system. "
    "You can withdraw at any time. Contact the PI with questions."
)


class Command(BaseCommand):
    help = "Add Whole Person Fit study to online database (reads study_config.json)"

    def handle(self, *args, **options):
        base = Path(__file__).resolve().parent.parent.parent.parent.parent
        config_dir = base / "apps" / "studies" / "assets" / "irb" / "whole-person-fit"
        config_path = config_dir / "study_config.json"

        if not config_path.exists():
            self.stdout.write(self.style.ERROR(
                "Whole Person Fit study config not found.\n"
            ))
            self.stdout.write(
                f"Create: {config_path}\n"
                "Copy from: apps/studies/assets/irb/whole-person-fit/study_config.json.example\n"
                "Fill in: slug, title, description, researcher_email, credit_value, mode, consent_text (optional), irb_status"
            )
            return

        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        slug = cfg.get("slug") or "whole-person-fit"
        title = cfg.get("title") or "Whole Person Fit"
        description = cfg.get("description") or "See study materials."
        researcher_email = cfg.get("researcher_email")
        if not researcher_email:
            self.stdout.write(self.style.ERROR("study_config.json must set researcher_email"))
            return

        credit_value = float(cfg.get("credit_value", 1))
        mode = cfg.get("mode") or "online"
        consent_text = cfg.get("consent_text") or DEFAULT_CONSENT
        irb_status = cfg.get("irb_status") or "pending"

        researcher = User.objects.filter(email__iexact=researcher_email).first()
        if not researcher:
            researcher = User.objects.create(
                email=researcher_email,
                first_name="Researcher",
                last_name="User",
                role="researcher",
                is_active=True,
            )

        study, created = Study.objects.get_or_create(
            slug=slug,
            defaults={
                "title": title,
                "description": description,
                "mode": mode,
                "credit_value": credit_value,
                "consent_text": consent_text,
                "irb_status": irb_status,
                "is_active": True,
                "is_approved": True,
                "researcher": researcher,
            },
        )
        if not created:
            study.title = title
            study.description = description
            study.credit_value = credit_value
            study.consent_text = consent_text
            study.irb_status = irb_status
            study.researcher = researcher
            study.save()
            self.stdout.write(self.style.SUCCESS(f"✓ Updated study: {study.title}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✓ Created study: {study.title}"))

        self.stdout.write(self.style.SUCCESS(f"  Slug: {study.slug}  PI: {researcher.get_full_name()}"))

        # Create/update draft protocol so reviewers can see details
        protocol_path = config_dir / "protocol.json"
        if protocol_path.exists():
            submission = create_or_update_protocol_from_json(study, protocol_path, researcher)
            if submission:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Protocol draft created/updated (ID: {submission.id})"))
        else:
            self.stdout.write(self.style.WARNING(
                f"  No protocol.json at {protocol_path} - protocol details not loaded. Add protocol.json for IRB review."
            ))
