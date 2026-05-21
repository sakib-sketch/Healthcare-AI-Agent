import json
import re

def clean_and_parse_json(response_text: str, default_fallback=None):
    """
    Cleans raw response_text from an LLM and safely parses it as a JSON object or array.
    Supports markdown backticks, trailing commas, comments, and inline malformed characters.
    """
    if not response_text:
        return default_fallback if default_fallback is not None else {}

    cleaned = response_text.strip()
    
    # 1. Strip markdown JSON formatting (e.g. ```json ... ```)
    if "```json" in cleaned:
        match = re.search(r'```json\s*(.*?)\s*```', cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1).strip()
    elif "```" in cleaned:
        match = re.search(r'```\s*(.*?)\s*```', cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1).strip()

    # 2. Attempt standard parsing after locating delimiters
    try:
        start_arr = cleaned.find('[')
        start_obj = cleaned.find('{')
        
        # Determine the earliest matching boundary
        if start_arr != -1 and (start_obj == -1 or start_arr < start_obj):
            start = start_arr
            end = cleaned.rfind(']') + 1
        elif start_obj != -1:
            start = start_obj
            end = cleaned.rfind('}') + 1
        else:
            start = 0
            end = len(cleaned)
            
        json_str = cleaned[start:end]
        return json.loads(json_str)
    except Exception:
        pass

    # 3. Fallback: Syntax cleanup (trailing commas, quotes, comments)
    try:
        # Resolve comments
        cleaned_str = re.sub(r'//.*?\n|/\*.*?\*/', '', json_str, flags=re.S)
        # Resolve unneeded trailing commas in objects and arrays
        cleaned_str = re.sub(r',\s*([\]}])', r'\1', cleaned_str)
        # Clean extra unicode characters/escapes
        return json.loads(cleaned_str)
    except Exception as e:
        # Safe fallback rather than crash
        return default_fallback if default_fallback is not None else {
            "error": f"JSON parsing failed: {str(e)}",
            "raw_response": response_text
        }
