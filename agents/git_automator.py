import subprocess
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ollama import Client

router = APIRouter()
client = Client(host='http://host.docker.internal:11434')

class GitRequest(BaseModel):
    diff: str
    context: str = ""

@router.post("/api/git/commit-msg")
async def generate_commit(request: GitRequest):
    if not request.diff.strip():
        raise HTTPException(status_code=400, detail="No changes detected in diff.")

    prompt = get_prompt('commit', 'llama3.1:latest')
    
    response = client.chat(messages=[{'role': 'user', 'content': prompt}])
    raw_msg = response['message']['content'].strip()
    clean_msg = raw_msg.replace("Here is the commit message:", "").replace("Here's the commit message:", "").strip()
    return {"message": response['message']['content']}

@router.post("/api/git/pr-description")
async def generate_pr(request: GitRequest):
    prompt = get_prompt('pr', 'llama3')
    response = client.chat(messages=[{'role': 'user', 'content': prompt}])
    return {"markdown": response['message']['content']}

@router.post("/api/git/safety-check")
async def safety_check(request: GitRequest):
    patterns = {
        "AWS Key": r"AKIA[0-9A-Z]{16}",
        "Private Key": r"-----BEGIN PRIVATE KEY-----",
        "Generic API Key": r"api_key\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]",
        "GitHub Token": r"ghp_[a-zA-Z0-9]{36}"
    }
    
    leaks = []
    for name, pattern in patterns.items():
        if re.search(pattern, request.diff):
            leaks.append(name)
            
    return {"safe": not leaks, "leaks": leaks}

def get_prompt(prompt_type: str, model: str) -> str:
    prompt = f"""
You are a rigorous {prompt_type} Message Generator.
Output ONLY the raw commit message. 
    
Rules:
1. Do NOT include conversational text like "Here is the message".
2. Do NOT use Markdown code blocks.
3. Start directly with the type (feat:, fix:, chore:).
4. Use imperative mood and keep it under 72 chars.
    
Diff:
{request.diff[:4000]} 
"""
    return prompt