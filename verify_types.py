import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'express_delivery.settings')
django.setup()

from core.models import CustomerProfile, User

def verify_customer_types():
    print("Verifying Customer Types in CustomerProfile model...")
    
    # Check choices
    expected_types = {
        'CONTRACT': 'Contract Customers (with monthly billing accounts)',
        'NON_CONTRACT': 'Non-Contract Customers (paying by cash or credit card)',
        'PREPAID': 'Prepaid Customers (shipping fees paid by the merchant or a third party)'
    }
    
    actual_types = dict(CustomerProfile.CustomerType.choices)
    
    all_match = True
    for code, label in expected_types.items():
        if code not in actual_types:
            print(f"[FAIL] Missing type: {code}")
            all_match = False
        elif actual_types[code] != label:
            print(f"[WARN] Label mismatch for {code}. Expected '{label}', got '{actual_types[code]}'")
            # This might be fine if translation or minor wording diff, but good to note
        else:
            print(f"[PASS] Found type: {code} - {label}")
            
    if all_match:
        print("\nAll requested customer types are present in the system.")
    else:
        print("\nSome customer types are missing.")

if __name__ == '__main__':
    verify_customer_types()
