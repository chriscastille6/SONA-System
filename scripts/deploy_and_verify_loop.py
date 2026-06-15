import sys
import subprocess
import time
from pathlib import Path

def run_command(cmd, shell=True):
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, check=True)
        return result.stdout.strip(), None
    except subprocess.CalledProcessError as e:
        return None, e.stderr.strip() or e.stdout.strip()

def main():
    print("🔄 Starting Automated Deployment & Live Database Verification Loop...")
    repo_root = Path(__file__).resolve().parent.parent
    
    # Step 1: Run local deploy script to sync code to the server
    print("\n📦 Step 1: Synchronizing code and assets to server...")
    deploy_script = repo_root / "deploy-to-server-rsync.sh"
    stdout, error = run_command(str(deploy_script))
    if error:
        print(f"❌ Deployment failed: {error}")
        sys.exit(1)
    print("✅ Files synced and server commands executed successfully.")

    # Step 2: Loop & Verify until live database is perfectly populated and matching
    print("\n🧪 Step 2: Verifying live database fields on server...")
    
    server_user = "ccastille"
    server_host = "bayoupal.nicholls.edu"
    remote_path = "hsirb-system"
    
    # We run a verification check on the server itself via SSH to pull the current DB state
    verify_cmd = (
        f"ssh {server_user}@{server_host} \"cd ~/{remote_path} && source venv/bin/activate && "
        "python manage.py shell -c '"
        "from apps.studies.models import Study, ProtocolSubmission; "
        "s = Study.objects.get(slug=\\\"goal-setting\\\"); "
        "sub = ProtocolSubmission.objects.get(study=s); "
        "print(\\\"TITLE:\\\", s.title); "
        "print(\\\"PI_TITLE:\\\", sub.pi_title); "
        "print(\\\"END_DATE:\\\", sub.estimated_completion_date); "
        "print(\\\"MEMBER_COUNT:\\\", sub.co_investigators.count(\\\"Dr.\\\")); "
        "print(\\\"CLEANUP:\\\", not Study.objects.filter(title__icontains=\\\"asdf\\\").exists());"
        "'\""
    )

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        print(f"\n🔄 Verification Attempt {attempt}/{max_retries}...")
        stdout, error = run_command(verify_cmd)
        
        if error:
            print(f"⚠️ SSH Verification error: {error}")
            print("Retrying in 3 seconds...")
            time.sleep(3)
            continue
            
        # Parse verification details
        db_state = {}
        for line in stdout.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                db_state[k.strip()] = v.strip()
                
        # Define expectations
        title_ok = db_state.get("TITLE") == "A Study in Decision Making"
        pi_title_ok = db_state.get("PI_TITLE") == "Associate Professor"
        end_date_ok = db_state.get("END_DATE") == "Spring 2027"
        co_i_ok = db_state.get("MEMBER_COUNT") == "4"  # Castille (Associate), Falgout (Assistant), Ann-Marie (Associate), Gravois (Doctorate), Maught (Doctorate) -> 4 Co-Is with "Dr." title
        cleanup_ok = db_state.get("CLEANUP") == "True"
        
        all_passed = title_ok and pi_title_ok and end_date_ok and co_i_ok and cleanup_ok
        
        print("\n--- LIVE SERVER VERIFICATION RESULTS ---")
        print(f"  · Study Title:        {'✅' if title_ok else '❌'} ({db_state.get('TITLE')})")
        print(f"  · PI Academic Rank:   {'✅' if pi_title_ok else '❌'} ({db_state.get('PI_TITLE')})")
        print(f"  · Completion Date:    {'✅' if end_date_ok else '❌'} ({db_state.get('END_DATE')})")
        print(f"  · Co-Investigators:   {'✅' if co_i_ok else '❌'} ({db_state.get('MEMBER_COUNT')} Dr. members found)")
        print(f"  · 'asdf' Cleaned:     {'✅' if cleanup_ok else '❌'}")
        print("----------------------------------------")
        
        if all_passed:
            print("\n🎉 SUCCESS: All database alignment tests have fully satisfied expectations!")
            break
        else:
            print("❌ Failure: Some fields are still out of alignment. Triggering re-population on server...")
            populate_cmd = (
                f"ssh {server_user}@{server_host} \"cd ~/{remote_path} && source venv/bin/activate && "
                "python manage.py populate_goal_setting_protocol_details && "
                "python manage.py cleanup_test_studies && "
                "sudo systemctl restart hsirb-system\""
            )
            run_command(populate_cmd)
            print("Repopulation commands and server restarts triggered. Waiting 5 seconds before retrying...")
            time.sleep(5)
    else:
        print("\n❌ Error: Failed to satisfy database expectations after max retries. Please check server logs.")

if __name__ == "__main__":
    main()
