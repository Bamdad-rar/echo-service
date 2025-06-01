import os
import ast
import subprocess
import httpx
import sys
import json



GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', None)
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}" 

if GEMINI_API_KEY is None:
    print("no gemini api key provided, cant create documents, exiting...")
    sys.exit(1)

def generate_staged_document():
    data = {
            "contents": [{"parts": [{"text": "git diff --cached here"}]}]
            }

    
