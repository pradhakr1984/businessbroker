#!/bin/bash
# Daily Acquisition Agent Workflow Script
# Run this script every morning to check for new business opportunities

echo "🎯 Daily Business Acquisition Agent"
echo "=================================="
echo "Date: $(date)"
echo ""

# Navigate to project directory
cd "/Users/prashantradhakrishnan/Downloads/Coding on Cursor/acquisition-agent-starter"

# Activate virtual environment
source .venv/bin/activate

echo "🔧 Loading environment and running agent..."
# Run the acquisition agent
export $(cat .env | grep -v '^#' | xargs) && python -m src.main --config agent_config.yaml

echo ""
echo "📊 Results Summary:"
echo "=================="

# Check if results exist
if [ -f "data/results.json" ]; then
    # Count opportunities found
    OPPORTUNITIES=$(python -c "import json; print(len(json.load(open('data/results.json'))))" 2>/dev/null || echo "0")
    echo "✅ Found $OPPORTUNITIES new opportunities"
    
    # Show file locations
    echo "📁 Generated files:"
    echo "   📄 Main report: data/results.md"
    echo "   🔧 JSON data: data/results.json" 
    echo "   ❌ Rejected: data/rejects.csv"
    echo ""
    
    if [ "$OPPORTUNITIES" -gt 0 ]; then
        echo "🎉 New opportunities found! Review data/results.md"
        echo "📱 Opening results..."
        open data/results.md 2>/dev/null || echo "   (Open data/results.md manually to review)"
    else
        echo "😔 No new opportunities matching your criteria today"
        echo "💡 This is normal - quality opportunities are rare!"
    fi
else
    echo "❌ No results file generated - check for errors above"
fi

echo ""
echo "⏰ Workflow completed at $(date)"
echo "🔄 Run this script again tomorrow morning!"
