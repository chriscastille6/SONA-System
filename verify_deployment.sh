#!/bin/bash
# Quick verification script to check if amendment system is deployed

echo "🔍 Verifying Deployment Status..."
echo ""

# Check if on server
if [ ! -d ~/hsirb-system ]; then
    echo "❌ Not on server. Run this on bayoupal.nicholls.edu"
    exit 1
fi

cd ~/hsirb-system
source venv/bin/activate

echo "1. Checking git status..."
git_status=$(git status -sb)
if echo "$git_status" | grep -q "ahead"; then
    echo "   ⚠️  Local changes not pushed"
elif echo "$git_status" | grep -q "behind"; then
    echo "   ⚠️  Server is behind - need to pull"
else
    echo "   ✅ Code is up to date"
fi

echo ""
echo "2. Checking migrations..."
if python manage.py showmigrations studies | grep -q "0019.*\[X\]"; then
    echo "   ✅ Amendment migration applied"
else
    echo "   ❌ Amendment migration NOT applied - run: python manage.py migrate"
fi

echo ""
echo "3. Checking ProtocolAmendment model..."
if python manage.py shell -c "from apps.studies.models import ProtocolAmendment; print('✅ Model exists')" 2>/dev/null; then
    echo "   ✅ ProtocolAmendment model accessible"
else
    echo "   ❌ Model not accessible - check migrations"
fi

echo ""
echo "4. Checking for TRO amendment..."
amendment_count=$(python manage.py shell -c "from apps.studies.models import ProtocolAmendment; print(ProtocolAmendment.objects.count())" 2>/dev/null | tail -1)
if [ "$amendment_count" -gt 0 ]; then
    echo "   ✅ Found $amendment_count amendment(s)"
else
    echo "   ⚠️  No amendments found - run: python manage.py populate_tro_protocol_details"
fi

echo ""
echo "5. Checking Jon Murphy account..."
jon_email=$(python manage.py shell -c "from apps.accounts.models import User; j=User.objects.filter(email__icontains='murphy', role='irb_member', is_active=True).first(); print(j.email if j else 'NOT FOUND')" 2>/dev/null | tail -1)
if [ "$jon_email" = "jonathan.murphy@nicholls.edu" ]; then
    echo "   ✅ Jon Murphy account correct: $jon_email"
elif [ "$jon_email" != "NOT FOUND" ]; then
    echo "   ⚠️  Jon Murphy has different email: $jon_email"
    echo "      Run: python manage.py fix_jon_murphy_accounts"
else
    echo "   ❌ Jon Murphy account not found"
fi

echo ""
echo "6. Checking service status..."
if sudo systemctl is-active --quiet hsirb-system; then
    echo "   ✅ hsirb-system service is running"
else
    echo "   ❌ hsirb-system service is NOT running"
fi

echo ""
echo "✅ Verification complete!"
