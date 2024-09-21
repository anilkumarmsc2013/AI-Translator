import requests
import json

api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
api_key = "AIzaSyB1Z8o2ipBbuuSJOI3a8okqkrSBs5_Tx28"  # API Key

def google_gemini_translate(input_text, input_language=None, target_language_code=None):
    headers = {
        "Content-Type": "application/json"
    }   
    
    if target_language_code:
        text_request = f"Please translate this {input_text} into {target_language_code}. If the content is already in {target_language_code}, keep it as it is without any changes or suggestions. Keep the same semantic meaning as original input text. Return the output in paragraph form."
    elif input_language:
        text_request = f"Please translate this {input_text} from {input_language} into {target_language_code}. If the content is already in {target_language_code}, keep it as it is without any changes or suggestions. Keep the same semantic meaning as original input text. Return the output in paragraph form."
    else:
        text_request = input_text

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": text_request
                    }
                ]
            }   
        ]
    }
    
    params = {
        "key": api_key
    }
    
    try:
        response = requests.post(api_url, headers=headers, params=params, json=data)
        response.raise_for_status()
        result = response.json()

        print("API Response:", json.dumps(result, indent=2))

        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                translated_text = ''.join(part['text'] for part in candidate['content']['parts'])
                return translated_text
        
        return input_text
    
    except requests.exceptions.RequestException as e:
        print(f"Error querying Gemini API: {e}")
        return None
    