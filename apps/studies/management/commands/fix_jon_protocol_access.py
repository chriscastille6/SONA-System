"""
Fix Jon Murphy's protocol access on the server.
Run this when Jon cannot see any protocols. It:
1. Consolidates Jon Murphy accounts (jonathan.murphy@nicholls.edu)
2. Assigns college reps to protocols that have none
3. Ensures Jon is College of Business rep
4. Verifies Jon can see protocols
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Fix Jon Murphy's protocol access (consolidate accounts, assign college reps, verify)"

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("FIXING JON MURPHY PROTOCOL ACCESS")
        self.stdout.write("=" * 60)

        # Step 1: Fix Jon Murphy accounts (merge test into real, set as CBA rep)
        self.stdout.write("\n[1/3] Consolidating Jon Murphy accounts...")
        call_command("fix_jon_murphy_accounts", verbosity=1)

        # Step 2: Assign college reps to protocols that have none (fallback to Business rep when needed)
        self.stdout.write("\n[2/3] Assigning college reps to unassigned protocols...")
        call_command("assign_college_reps_to_protocols", "--fallback-business", verbosity=1)

        # Step 3: Verify
        self.stdout.write("\n[3/3] Verifying Jon Murphy account...")
        call_command("verify_jon_murphy_account", verbosity=1)

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("DONE. Have Jon log in at:")
        self.stdout.write("  https://bayoupal.nicholls.edu/hsirb/accounts/login/")
        self.stdout.write("  Email: jonathan.murphy@nicholls.edu")
        self.stdout.write("\nProtocol list: /hsirb/studies/protocol/submissions/")
        self.stdout.write("=" * 60)
