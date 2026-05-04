import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from agent import run_analysis_pipeline

def parse_scenarios(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by the '=' separator
    parts = content.split("============================================================")
    
    scenarios = []
    title = ""
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        if part.startswith("ÖRNEK"):
            title = part
        else:
            if title:
                scenarios.append((title, part))
                title = ""
                
    return scenarios

def test_all_scenarios():
    files_to_test = []

    # Only test scenario files under analysis-input-scenarios folder
    scenarios_dir = os.path.join(os.path.dirname(__file__), 'analysis-input-scenarios')
    if os.path.exists(scenarios_dir) and os.path.isdir(scenarios_dir):
        for f in sorted(os.listdir(scenarios_dir)):
            if f.endswith('.txt'):
                files_to_test.append(os.path.join('analysis-input-scenarios', f))

    if not files_to_test:
        raise AssertionError("No scenario files found in analysis-input-scenarios/")
    
    all_passed = True
    
    for file_name in files_to_test:
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        if not os.path.exists(file_path):
            continue
            
        print(f"\n{'='*60}\nTesting scenarios from: {file_name}\n{'='*60}")
        scenarios = parse_scenarios(file_path)
        
        for title, transcript in scenarios:
            print(f"\nRunning scenario: {title}")
            
            # Expected outcome based on title (MEZUN OLABİLİR vs MEZUN OLAMAZ)
            expected_graduated = "MEZUN OLABİLİR" in title
            
            try:
                # Run the pipeline
                result = run_analysis_pipeline(transcript)
                
                print(f"Expected Graduated: {expected_graduated}")
                print(f"Actual Graduated: {result.get('is_graduated')}")
                print(f"Total ECTS: {result.get('transcript_total_ects')}")
                
                if result.get('missing_conditions'):
                    print(f"Missing Conditions: {result.get('missing_conditions')}")
                
                if result.get('is_graduated') == expected_graduated:
                    print("Status: ✅ PASS")
                else:
                    print("Status: ❌ FAIL")
                    all_passed = False
                    
            except Exception as e:
                print(f"Status: ❌ ERROR during execution: {str(e)}")
                all_passed = False
                
    assert all_passed, "Some scenarios failed!"

if __name__ == "__main__":
    print("Running scenarios as a normal script...")
    try:
        test_all_scenarios()
        print("\n🎉 All scenarios passed successfully!")
    except AssertionError as e:
        print(f"\n❌ {str(e)}")
        sys.exit(1)
