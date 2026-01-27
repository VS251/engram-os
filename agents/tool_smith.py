import os
import re
import sys
from ollama import Client  

TOOLS_DIR = "tools"

client = Client(host='http://host.docker.internal:11434')

SYSTEM_PROMPT = """
You are a Senior Python Engineer. 
Your goal is to write a standalone Python script (a 'Tool') to fulfill a user's request.

RULES:
1. The code must be clean, heavily commented, and use standard libraries where possible.
2. If external libraries (like 'requests') are needed, import them.
3. The script MUST have a `main()` function or a `run()` function so it can be tested immediately.
4. RETURN ONLY THE CODE. No markdown backticks (```), no conversational filler.
"""

def create_new_skill(user_request):
    print(f"🔨 The Tool Smith is forging a new skill: '{user_request}'...")
    
    os.makedirs(TOOLS_DIR, exist_ok=True)
    
    try:
        response = client.chat(
            model='llama3.1:latest', 
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': f"Write a Python script to: {user_request}. Save it as a tool."}
            ],
            stream=False 
        )
        
        code = response['message']['content']
        
        code = re.sub(r'^```python\n', '', code)
        code = re.sub(r'^```\n', '', code)
        code = re.sub(r'\n```$', '', code)
        
        safe_name = "_".join(user_request.split()[:3]).lower().replace(" ", "_")
        safe_name = re.sub(r'[^a-z0-9_]', '', safe_name)
        filename = f"generated_{safe_name}.py"
        filepath = os.path.join(TOOLS_DIR, filename)
        
        with open(filepath, "w") as f:
            f.write(code)
            
        return f"Success! Created {filename}.\nRun it with: python3 {filepath}"
        
    except Exception as e:
        return f"Forge Failed: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        req = sys.argv[1]
    elif not sys.stdin.isatty():
        req = sys.stdin.read().strip()
    else:
        req = input("What tool should I build? > ")

    if req:
        print(create_new_skill(req))
    else:
        print("Error: No skill description provided.")