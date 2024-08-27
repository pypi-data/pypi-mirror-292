from pathlib import Path
import requests
import json

def to_lmc(content: str, role: str = "assistant") -> dict: 
    return {"role": role, "content": content}
        
class SnSdk:
    def __init__(self, 
                 model="Meta-Llama-3.1-8B-Instruct", 
                 messages=[],
                 system="You are a helpful assistant."):
    
        self.model = model
        self.messages = messages
        self.system = to_lmc(system, role="system")
        self.endpoint = "https://fast.snova.ai/api/completion"
        
        src = Path(Path(__file__).parent, "src")
        with open(Path(src, "headers.json"), "r") as f:
            self.headers = json.loads(f.read())
            
        with open(Path(src, "body.json"), "r") as f:
            self.template = json.loads(f.read())
            self.template["body"]["model"] = self.model
            
    def _stream_chat(self, data, remember=False):        
        response = requests.post(self.endpoint, headers=self.headers, data=json.dumps(data), stream=True)
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')[6:]
                if decoded_line == "[DONE]":
                    continue

                json_line = json.loads(decoded_line)
                if not json_line.get("choices"):
                    continue

                options = json_line.get("choices")[0]
                if options.get("finish_reason") == "end_of_text":
                    continue

                chunk = options.get('delta', {}).get('content', '')
                if remember:
                    self.messages[-1]["content"] += chunk
                    
                yield chunk
        
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
        data["body"]["messages"] = [system] + self.messages + [message]
        data["body"]["max_tokens"] = max_tokens
            
        if remember:
            self.messages.append(message)
        
        if stream: return self._stream_chat(data, remember)
        else: return "".join(chunk for chunk in self._stream_chat(data, remember))
