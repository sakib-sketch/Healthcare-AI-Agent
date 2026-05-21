"""Fast, isolated unit test for json_parser.py. No API calls."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from agents.json_parser import clean_and_parse_json

passed = 0

# Test 1: Clean JSON object
r = clean_and_parse_json('{"diagnosis": ["Diabetes"], "symptoms": []}')
assert isinstance(r, dict) and r['diagnosis'] == ['Diabetes'], 'Test 1 FAILED'
print('✅ Test 1 PASSED: Clean JSON object')
passed += 1

# Test 2: JSON array
r = clean_and_parse_json('[{"code": "E11.9", "status": "Approved"}]')
assert isinstance(r, list) and r[0]['code'] == 'E11.9', 'Test 2 FAILED'
print('✅ Test 2 PASSED: Clean JSON array')
passed += 1

# Test 3: Markdown code block wrapping (```json ... ```)
r = clean_and_parse_json('```json\n[{"entity": "Type 2 DM", "code": "E11.9"}]\n```')
assert isinstance(r, list) and r[0]['entity'] == 'Type 2 DM', 'Test 3 FAILED'
print('✅ Test 3 PASSED: Markdown-wrapped JSON')
passed += 1

# Test 4: Trailing comma (common LLM mistake)
r = clean_and_parse_json('[{"entity": "Hypertension", "code": "I10",}]')
assert isinstance(r, list) and r[0]['code'] == 'I10', 'Test 4 FAILED'
print('✅ Test 4 PASSED: Trailing comma cleaned')
passed += 1

# Test 5: Completely broken input returns fallback
r = clean_and_parse_json('Sorry, I cannot produce JSON.', default_fallback={'error': True})
assert r == {'error': True}, 'Test 5 FAILED'
print('✅ Test 5 PASSED: Broken input safely returns fallback')
passed += 1

# Test 6: Empty string returns fallback
r = clean_and_parse_json('', default_fallback=[])
assert r == [], 'Test 6 FAILED'
print('✅ Test 6 PASSED: Empty string returns fallback')
passed += 1

print(f'\n🎉 ALL {passed}/6 TESTS PASSED — json_parser.py is working correctly!')
