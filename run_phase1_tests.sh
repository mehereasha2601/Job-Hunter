#!/bin/bash
# Run complete Phase 1 testing workflow

echo "=================================================="
echo "Phase 1 Testing Workflow"
echo "=================================================="
echo ""

# Step 1: Activate virtual environment
echo "Step 1: Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Step 2: Verify API keys
echo "Step 2: Verifying API keys..."
python test_api_keys.py
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  API keys not configured. Please:"
    echo "   1. Copy .env.example to .env"
    echo "   2. Add your GROQ_API_KEY and GEMINI_API_KEY"
    echo "   3. Run this script again"
    exit 1
fi
echo ""

# Step 3: Run test harness
echo "Step 3: Running test harness (this may take 2-3 minutes)..."
echo "   - Testing 5 jobs with both Groq and Gemini"
echo "   - Generating 10 resumes + 20 emails"
echo "   - Running 40 guardrail checks"
echo ""
python tests/test_harness.py
echo ""

# Step 4: Show results
echo "Step 4: Results summary"
echo "=================================================="
echo ""
echo "✓ Test complete! Review the output:"
echo ""
echo "  📊 test_output/SUMMARY.md - Side-by-side comparison"
echo "  📄 test_output/*_resume.txt - Generated resumes"
echo "  📧 test_output/*_emails.txt - Generated emails"
echo "  📁 test_output/*.json - Full result data"
echo ""
echo "Next: Review output quality and iterate on prompts if needed"
echo ""
