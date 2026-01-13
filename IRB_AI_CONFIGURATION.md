# AI IRB Review - Configuration Guide

**Last Updated**: October 22, 2025

---

## AI Provider Options

The system supports **two AI providers**:
- **OpenAI** (GPT-4, GPT-4 Turbo, GPT-4o) - DEFAULT
- **Anthropic** (Claude 3.5 Sonnet, Claude 3 Opus)

Choose the one where you have an API key!

---

## Option A: OpenAI (Recommended if you have OpenAI account)

### Step 1: Get API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-...`)

### Step 2: Configure in SONA

Add to your `.env` file or export:

```bash
export IRB_AI_PROVIDER="openai"
export OPENAI_API_KEY="sk-proj-your-key-here"
export IRB_AI_MODEL="gpt-4o"  # or gpt-4-turbo, gpt-4
```

### Step 3: Restart Server

```bash
# Kill and restart Django
pkill -f "python.*manage.py runserver"
cd "/Users/ccastille/Documents/GitHub/SONA System"
source venv/bin/activate
python manage.py runserver 8002
```

### OpenAI Model Options

- **`gpt-4o`** (recommended): Fast, excellent, cost-effective (~$0.15/review)
- **`gpt-4-turbo`**: Very good, slightly cheaper (~$0.10/review)
- **`gpt-4`**: Original GPT-4, more expensive (~$0.30/review)

---

## Option B: Anthropic Claude

### Step 1: Get API Key

1. Go to https://console.anthropic.com/
2. Sign in or create account
3. Go to API Keys section
4. Create new key
5. Copy the key (starts with `sk-ant-api03-...`)

### Step 2: Configure in SONA

```bash
export IRB_AI_PROVIDER="anthropic"
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
export IRB_AI_MODEL="claude-3-5-sonnet-20241022"
```

### Step 3: Restart Server

```bash
pkill -f "python.*manage.py runserver"
cd "/Users/ccastille/Documents/GitHub/SONA System"
source venv/bin/activate
python manage.py runserver 8002
```

### Anthropic Model Options

- **`claude-3-5-sonnet-20241022`** (recommended): Excellent, fast (~$0.15/review)
- **`claude-3-opus-20240229`**: Most capable, expensive (~$0.75/review)
- **`claude-3-sonnet-20240229`**: Good balance (~$0.15/review)

---

## Option C: No API Key (Testing Mode)

The system works **without any API key** for testing:

- Returns placeholder results
- Shows UI and workflow
- Each agent reports "API not configured" as a minor issue
- Good for testing interface before getting API access

**No configuration needed** - just use the system!

---

## Finding Your OpenAI API Key

If you've used OpenAI before, your key might be:

### Check Environment Variables

```bash
# Check if already set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Check common config files
grep -r "OPENAI_API_KEY" ~/.zshrc ~/.bashrc ~/.env
```

### Check Previous Projects

```bash
# Search your GitHub projects
find ~/Documents/GitHub -name ".env" -type f -exec grep -l "OPENAI_API_KEY" {} \;
```

### Check Password Manager

If you use a password manager, search for:
- "OpenAI API"
- "OpenAI Key"
- "platform.openai.com"

---

## Setting Up for the First Time

### 1. Create .env File

```bash
cd "/Users/ccastille/Documents/GitHub/SONA System"
touch .env
```

### 2. Add Configuration

Edit `.env` and add:

```bash
# AI IRB Review
IRB_AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-actual-key-here
IRB_AI_MODEL=gpt-4o

# Or for Anthropic:
# IRB_AI_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
# IRB_AI_MODEL=claude-3-5-sonnet-20241022
```

### 3. Verify Configuration

```bash
python manage.py shell -c "
from django.conf import settings
print('Provider:', settings.IRB_AI_PROVIDER)
print('Model:', settings.IRB_AI_MODEL)
print('OpenAI Key:', 'Configured' if settings.OPENAI_API_KEY else 'Not configured')
print('Anthropic Key:', 'Configured' if settings.ANTHROPIC_API_KEY else 'Not configured')
"
```

---

## Cost Estimates

### OpenAI Pricing (as of Oct 2025)

**GPT-4o** (recommended):
- Input: $2.50 / 1M tokens
- Output: $10.00 / 1M tokens
- **Per Review**: ~$0.10-$0.25 (depending on material size)

**GPT-4 Turbo**:
- Input: $10.00 / 1M tokens
- Output: $30.00 / 1M tokens
- **Per Review**: ~$0.15-$0.40

### Anthropic Pricing

**Claude 3.5 Sonnet**:
- Input: $3.00 / 1M tokens
- Output: $15.00 / 1M tokens
- **Per Review**: ~$0.15-$0.30

### Monthly Estimates

**Light Use** (10 reviews/month):
- OpenAI: ~$2-3/month
- Anthropic: ~$2-3/month

**Heavy Use** (50 reviews/month):
- OpenAI: ~$10-15/month
- Anthropic: ~$10-15/month

---

## Recommended Setup for You

Since you don't currently have an API key:

### Option 1: Use Testing Mode (No Key Needed)

**Pros**:
- Works immediately
- No cost
- Can test UI and workflow
- Good for demos

**Cons**:
- Placeholder results only
- Doesn't actually analyze your materials

**Setup**: Nothing! Just use it as-is.

### Option 2: Get OpenAI Key (Recommended)

**Pros**:
- Real AI analysis
- Familiar (GPT-4)
- Good quality results
- ~$0.15 per review

**Cons**:
- Costs money
- Requires credit card

**Setup**:
1. Go to https://platform.openai.com/api-keys
2. Create account
3. Add $5-10 credit
4. Generate API key
5. Add to `.env` file
6. Restart server

---

## Which Provider Should You Choose?

### Choose OpenAI if:
- ✅ You already have an OpenAI account
- ✅ You're familiar with GPT-4
- ✅ You want gpt-4o (fast and cost-effective)
- ✅ You prefer slightly lower costs

### Choose Anthropic if:
- ✅ You already have an Anthropic account
- ✅ You prefer Claude's analysis style
- ✅ You want longer context windows
- ✅ You need specific Claude capabilities

### Use Testing Mode if:
- ✅ You want to test the interface first
- ✅ You don't need real analysis yet
- ✅ You're still developing protocols
- ✅ You want to demo the system

---

## Testing the Configuration

After configuring, test with:

```bash
python manage.py test_irb_review
```

This will:
- Create a test review
- Run it immediately
- Show you if API is working
- Display results

Look for:
- ✅ "Review Complete!" = API working
- ❌ "API not configured" = Key missing or wrong

---

## Switching Providers

You can switch anytime by changing `.env`:

```bash
# Switch to OpenAI
IRB_AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...
IRB_AI_MODEL=gpt-4o

# Switch to Anthropic
IRB_AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-...
IRB_AI_MODEL=claude-3-5-sonnet-20241022
```

Then restart the server. Previous reviews will still show their original provider in the audit trail.

---

## Summary

**Current Default**: OpenAI with gpt-4o  
**Fallback**: Testing mode (placeholder results)  
**Flexibility**: Switch providers anytime  

**Next Step**: Either get an OpenAI API key or use testing mode to explore the interface!







