#!/usr/bin/env python3
"""
Test script for Axial parser integration
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from parsers.axial import parse_axial
from parsers import parse_emails_to_records
from filters import policy_filter
import yaml

def test_axial_parser():
    """Test the Axial parser with sample email data"""
    
    # Sample Axial email (simulated structure)
    sample_axial_email = {
        "subject": "New Deal Alert: Manufacturing Business for Sale",
        "from": [("Axial", "deals@axial.net")],
        "text_html": """
        <html>
        <body>
        <h2>Investment Opportunity</h2>
        <p><strong>Company:</strong> Premium Manufacturing Co.</p>
        <p><strong>Industry:</strong> Manufacturing</p>
        <p><strong>Location:</strong> Albany, NY</p>
        <p><strong>Asking Price:</strong> $3.2M</p>
        <p><strong>TTM EBITDA:</strong> $850K</p>
        <p><strong>Revenue:</strong> $5.8M</p>
        <p><strong>Reason for Sale:</strong> Owner retirement after 25 years</p>
        <p><a href="https://axial.net/deal/12345">View Deal Details</a></p>
        </body>
        </html>
        """,
        "text_plain": """
        Investment Opportunity
        Company: Premium Manufacturing Co.
        Industry: Manufacturing
        Location: Albany, NY
        Asking Price: $3.2M
        TTM EBITDA: $850K
        Revenue: $5.8M
        Reason for Sale: Owner retirement after 25 years
        View Deal Details: https://axial.net/deal/12345
        """
    }
    
    # Test individual parser
    print("Testing Axial parser directly...")
    results = parse_axial(sample_axial_email)
    
    if results:
        print(f"✓ Parser successfully extracted {len(results)} record(s)")
        for record in results:
            print(f"  - Business: {record['name']}")
            print(f"  - Price: ${record['price']:,}")
            print(f"  - Multiple: {record['earnings_multiple']}")
            print(f"  - Reason: {record['reason_for_sale']}")
            print(f"  - Location: {record['address']}")
            print(f"  - Partial match explanation: {record.get('partial_match_explanation', 'N/A')}")
    else:
        print("✗ Parser failed to extract records")
        return False
    
    # Test integration with parser system
    print("\nTesting integration with parser system...")
    records, rejects = parse_emails_to_records([sample_axial_email])
    
    if records:
        print(f"✓ Parser system extracted {len(records)} record(s)")
    else:
        print("✗ Parser system failed")
        return False
    
    # Test filtering
    print("\nTesting filtering...")
    try:
        # Load config
        with open('agent_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        for record in records:
            passed, reason = policy_filter(record, config)
            print(f"  - Filter result: {'✓ PASSED' if passed else '✗ REJECTED'}")
            if not passed:
                print(f"    Reason: {reason}")
    except Exception as e:
        print(f"✗ Filter test failed: {e}")
        return False
    
    print("\n✓ All tests completed successfully!")
    return True

def test_negative_case():
    """Test that non-Axial emails are ignored"""
    
    non_axial_email = {
        "subject": "Random newsletter",
        "from": [("Some Company", "newsletter@example.com")],
        "text_html": "<p>This is not a deal email</p>",
        "text_plain": "This is not a deal email"
    }
    
    print("\nTesting negative case (non-Axial email)...")
    results = parse_axial(non_axial_email)
    
    if not results:
        print("✓ Non-Axial email correctly ignored")
        return True
    else:
        print("✗ Non-Axial email incorrectly parsed")
        return False

if __name__ == "__main__":
    print("=== Axial Parser Test ===")
    
    success = test_axial_parser()
    success = test_negative_case() and success
    
    if success:
        print("\n🎉 All tests passed! Axial parser is ready to use.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
    
    sys.exit(0 if success else 1)
