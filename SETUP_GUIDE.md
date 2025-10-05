# Setup Guide - arXiv Daily Digest

Complete step-by-step guide to get your arXiv digest running.

## Step 1: Initial Setup

### Create Project Directory

```bash
# Create and navigate to project directory
mkdir arxiv-daily-digest
cd arxiv-daily-digest

# Initialize git repository
git init
```

### Download Project Files

Save all the files from the artifacts into this structure:

```
arxiv-daily-digest/
├── .gitignore
├── LICENSE
├── README.md
├── config.yml
├── environment.yml
├── requirements.txt
├── llm.txt
├── src/
│   ├── __init__.py
│   ├── arxiv_fetcher.py
│   ├── summarizer.py
│   ├── notifier.py
│   └── main.py
└── tests/
    └── test_arxiv_fetcher.py
```

## Step 2: Set Up Python Environment

### Option A: Using Conda (Recommended)

```bash
# Create environment from file
conda env create -f environment.yml

# Activate environment
conda activate arxiv-digest

# Verify installation
python --version  # Should be 3.9+
```

### Option B: Using venv + pip

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Copy the key (starts with `sk-...`)

### Set the API Key

**Linux/Mac:**
```bash
export OPENAI_API_KEY='sk-your-key-here'

# Make it persistent (add to ~/.bashrc or ~/.zshrc)
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=sk-your-key-here

# Make it persistent (PowerShell as Admin):
setx OPENAI_API_KEY "sk-your-key-here"
```

**Verify it's set:**
```bash
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY%  # Windows CMD
```

## Step 4: Configure Your Keywords

Edit `config.yml` to match your research interests:

```yaml
keywords:
  - ["dislocation", "molecular dynamics"]  # Papers with BOTH terms
  - ["atomistic simulation"]               # OR papers with this
  - ["crystal plasticity"]                 # OR papers with this
  - ["phase field", "microstructure"]     # OR papers with BOTH these
```

**Tips for keywords:**
- Each list `["word1", "word2"]` requires ALL words (AND logic)
- Separate lists are alternatives (OR logic)
- Be specific enough to avoid too many results
- Use key technical terms from your field

## Step 5: Test Locally

### Quick Test (No API Key Needed)

Test just the arXiv fetcher:

```bash
cd src
python -c "from arxiv_fetcher import test_fetcher; test_fetcher()"
```

### Full Test with Summaries

```bash
cd src
python main.py --dry-run
```

This will:
- Fetch papers from arXiv
- Generate AI summaries
- Show you a preview without saving

### Generate Your First Digest

```bash
cd src
python main.py
```

Check the output file: `daily_digest.txt`

## Step 6: Verify Everything Works

### Run the Tests

```bash
# From project root
pytest tests/ -v

# Or with coverage
pytest tests/ --cov=src --cov-report=html
```

### Check Your Output

Open `daily_digest.txt` and verify:
- Papers are relevant to your keywords
- Summaries are concise and informative
- URLs are correct

## Step 7: Customize Output

### Change Output Format

In `config.yml`:

```yaml
output:
  format: 'text'  # Options: 'text', 'email', 'both'
  output_file: 'my_digest.txt'
  include_abstract: false  # Set true to include full abstracts
```

### Adjust Time Window

```yaml
arxiv:
  time_window_hours: 48  # Check last 2 days instead of 1
```

### Change AI Model

```yaml
openai:
  model: "gpt-4o-mini"  # Fast and cheap
  # Or: "gpt-4o" for better quality (more expensive)
  max_tokens: 200  # Longer summaries
  temperature: 0.5  # More creative
```

## Step 8: Set Up GitHub Repository

### Initialize Repository

```bash
# Add all files
git add .
git commit -m "Initial commit: arXiv Daily Digest"

# Create repository on GitHub, then:
git remote add origin https://github.com/yourusername/arxiv-daily-digest.git
git branch -M main
git push -u origin main
```

### Add Secrets for GitHub Actions

1. Go to your repository on GitHub
2. Settings → Secrets and variables → Actions
3. Add these secrets:

- `OPENAI_API_KEY`: Your OpenAI API key
- `SMTP_SERVER`: (optional) e.g., `smtp.gmail.com`
- `SMTP_PORT`: (optional) e.g., `587`
- `SMTP_USER`: (optional) Your email
- `SMTP_PASSWORD`: (optional) Email app password

## Step 9: Set Up Email (Optional)

### For Gmail:

1. Enable 2-factor authentication
2. Generate an "App Password":
   - Google Account → Security → 2-Step Verification → App passwords
3. Use that password (not your regular password)

### Configure in config.yml:

```yaml
email:
  enabled: true
  recipient: "your.email@example.com"
  subject: "arXiv Daily Digest - {date}"

output:
  format: 'email'  # or 'both' for email + file
```

### Set Environment Variables:

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your.email@gmail.com"
export SMTP_PASSWORD="your-app-password"
```

### Test Email:

```bash
cd src
python main.py
```

Check your email!

## Step 10: Automate with GitHub Actions

Create `.github/workflows/daily_digest.yml`:

```yaml
name: Daily arXiv Digest

on:
  schedule:
    # Run at 9 AM UTC every day
    - cron: '0 9 * * *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  digest:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run digest
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        SMTP_SERVER: ${{ secrets.SMTP_SERVER }}
        SMTP_PORT: ${{ secrets.SMTP_PORT }}
        SMTP_USER: ${{ secrets.SMTP_USER }}
        SMTP_PASSWORD: ${{ secrets.SMTP_PASSWORD }}
      run: |
        cd src
        python main.py
    
    - name: Upload digest
      uses: actions/upload-artifact@v3
      with:
        name: daily-digest
        path: daily_digest.txt
        retention-days: 30
```

### Commit and Push:

```bash
git add .github/workflows/daily_digest.yml
git commit -m "Add GitHub Actions workflow"
git push
```

### Test the Workflow:

1. Go to Actions tab in GitHub
2. Click "Daily arXiv Digest"
3. Click "Run workflow"
4. Wait for it to complete
5. Check the artifacts

## Troubleshooting

### "No papers found"
- **Solution**: Broaden keywords or increase `time_window_hours`
- **Check**: Use test_fetcher() to see what arXiv returns

### "OPENAI_API_KEY not set"
- **Solution**: Export the environment variable
- **Check**: `echo $OPENAI_API_KEY`

### "Error generating summary"
- **Solution**: Check OpenAI account has credits
- **Check**: Visit [OpenAI Usage](https://platform.openai.com/usage)

### Rate Limit Errors
- **Solution**: Add delay between requests
- **Check**: Reduce `max_results` in config.yml

### Email Not Sending
- **Solution**: Verify SMTP credentials
- **Check**: Try sending test email with Python smtplib
- **Gmail**: Ensure "Less secure app access" or use App Password

### GitHub Actions Failing
- **Solution**: Check secrets are set correctly
- **Check**: View workflow logs in Actions tab
- **Common issue**: Secrets not accessible in forked repos

## Cost Estimation

### OpenAI API Costs (gpt-4o-mini)

- Input: ~500 tokens/paper (title + abstract)
- Output: ~150 tokens/summary
- Cost: ~$0.00015 per paper

**Daily scenarios:**
- 5 papers/day: ~$0.02/month
- 20 papers/day: ~$0.10/month
- 50 papers/day: ~$0.25/month

Very affordable! 🎉

## Next Steps

Now that everything is working:

1. **Refine keywords**: Adjust based on first results
2. **Set schedule**: Pick best time for daily runs
3. **Share with colleagues**: They can fork and customize
4. **Add features**: 
   - Slack notifications
   - HTML email formatting
   - Category-specific digests
   - Weekly summaries

## Getting Help

- **Check logs**: Look at GitHub Actions logs for errors
- **Test locally**: Always test changes locally first
- **Read docs**: 
  - [arXiv API](https://arxiv.org/help/api)
  - [OpenAI API](https://platform.openai.com/docs)
  - [GitHub Actions](https://docs.github.com/actions)

## Learning Objectives Achieved ✅

You now know how to:
- ✅ Use arXiv API for paper searches
- ✅ Integrate OpenAI API for text generation
- ✅ Set up GitHub Actions for automation
- ✅ Handle secrets securely
- ✅ Schedule daily tasks
- ✅ Parse XML responses
- ✅ Format and send emails programmatically

Happy researching! 🚀