"""Command-line run on any new input; standard library only.
python demo.py "I ordered a phone online and it never arrived"
"""
import argparse
import json
from engine import analyze

p = argparse.ArgumentParser()
p.add_argument("story", nargs="?", help="User's own description")
p.add_argument("--ai", action="store_true", help="Enable an OpenAI-compatible model endpoint")
a = p.parse_args()
if not a.story:
    a.story = input("Tell me about your online shopping/refund issue: ")
print(json.dumps(analyze(a.story, use_model=a.ai), ensure_ascii=False, indent=2))
