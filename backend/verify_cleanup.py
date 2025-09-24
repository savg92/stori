"""Verify that all mock dependencies have been removed."""
import os

def verify_mock_cleanup():
    """Check that all mock dependencies are gone."""
    print("🔍 Verifying mock data cleanup...")
    
    service_files = [
        "src/modules/ai/service.py",
        "src/modules/expenses/service.py", 
        "src/modules/timeline/service.py",
        "src/modules/transactions/transactions_service.py"
    ]
    
    all_clean = True
    
    for file_path in service_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for mock references
            mock_references = [
                "mock_service",
                "MockDataService", 
                "_get_mock_",
                "is_mock_user",
                "get_mock_transactions"
            ]
            
            found_mocks = []
            for mock_ref in mock_references:
                if mock_ref in content:
                    found_mocks.append(mock_ref)
            
            if found_mocks:
                print(f"❌ {file_path}: Found mock references: {', '.join(found_mocks)}")
                all_clean = False
            else:
                print(f"✅ {file_path}: Clean of mock dependencies")
        else:
            print(f"⚠️  {file_path}: File not found")
    
    if all_clean:
        print(f"\n🎉 ALL SERVICES ARE CLEAN!")
        print(f"✅ No mock data dependencies found in any service")
        print(f"🔥 Backend is ready for real database data only!")
        
        # Check line counts to show the cleanup
        print(f"\n📊 Service file sizes after cleanup:")
        for file_path in service_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    lines = len(f.readlines())
                print(f"   {file_path}: {lines} lines")
    else:
        print(f"\n❌ Some files still have mock dependencies!")
    
    return all_clean

if __name__ == "__main__":
    verify_mock_cleanup()
