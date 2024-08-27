from pathlib import Path
from random import choice
import requests
import json

def to_lmc(content: str, role: str = "assistant") -> dict: 
    return {"role": role, "content": content}

def available() -> set:
    return {"Meta-Llama-3.1-8B-Instruct", "Meta-Llama-3.1-70B-Instruct", "Meta-Llama-3.1-405B-Instruct", "Samba CoE", "Mistral-T5-7B-v1", "v1olet_merged_dpo_7B", "WestLake-7B-v2-laser-truthy-dpo", "DonutLM-v1", "SambaLingo Arabic", "SambaLingo Bulgarian", "SambaLingo Hungarian", "SambaLingo Russian", "SambaLingo Serbian (Cyrillic)", "SambaLingo Slovenian", "SambaLingo Thai", "SambaLingo Turkish", "SambaLingo Japanese"}

class SnSdk:
    def __init__(self, 
                 model="Meta-Llama-3.1-8B-Instruct", 
                 messages=[],
                 system="You are a helpful assistant.",
                 priority=4,
                 remember=False):
    
        if model in available(): self.model = model
        else: self.model = "Meta-Llama-3.1-8B-Instruct"
        
        src = Path(Path(__file__).parent, "src")
        with open(Path(src, "user_agents.txt"), "r") as f:
            self.user_agent = choice(f.read().split("\n"))
            
        with open(Path(src, "mask_lmc.json"), "r") as f:
            self.mask = json.loads(f.read())
            
        with open(Path(src, "headers.json"), "r") as f:
            self.headers = json.loads(f.read())
            self.headers["User-Agent"] = self.user_agent
            self.headers["Priority"] = "u=" + str(priority)
            
        with open(Path(src, "body.json"), "r") as f:
            self.template = json.loads(f.read())
            self.template["body"]["model"] = self.model
            
        self.messages = messages
        self.remember = remember
        self.system = to_lmc(system, role="system")
        self.endpoint = "https://fast.snova.ai/api/completion"
        
    def mask_lmc(self, lmc: dict, i) -> dict:
        return lmc | self.mask | {"id": f"{(i//2)+1}-id", "ref": f"{(i//2)+1}-ref"}
            
    def _stream_chat(self, data, remember=False):        
        response = requests.post(self.endpoint, headers=self.headers, data=json.dumps(data), stream=True)
        message, meta = "", {}
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')[6:]
                if decoded_line == "[DONE]":
                    continue

                json_line = json.loads(decoded_line)
                if not json_line.get("choices"):
                    meta = json_line
                    continue

                options = json_line.get("choices")[0]
                if options.get("finish_reason") == "end_of_text":
                    continue

                chunk = options.get('delta', {}).get('content', '')
                if self.remember or remember:
                    message += chunk
                yield chunk
                
        if self.remember or remember:
            self.messages.append(to_lmc(message) | meta)
        
    def chat(self, 
             message: str, 
             role="user", 
             stream=False,
             max_tokens=2048,
             remember=False, 
             lmc=False,
             system: str = None):
        
        system = to_lmc(system, role="system") if system else self.system
        message = message if lmc else to_lmc(message, role=role)
        
        
        
        data = dict(self.template)
        data["body"]["messages"] = [system] + [self.mask_lmc(i, j) for j, i in enumerate(self.messages)] + [self.mask_lmc(message, len(self.messages))]
        data["body"]["max_tokens"] = max_tokens
            
        if self.remember or remember:
            self.messages.append(message)
        
        if stream: return self._stream_chat(data, remember)
        else: return "".join(chunk for chunk in self._stream_chat(data, remember))
