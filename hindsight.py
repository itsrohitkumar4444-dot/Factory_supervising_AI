import urllib.request
import json
import time

class HindsightMemory:
    def __init__(self, api_key, storage_path=None):
        # We now use the real API
        self.api_key = api_key
        self.endpoint = "https://api.hindsight.vectorize.io"
        print(f"[Hindsight] Initialized Real API Client -> {self.endpoint}")

    def _make_request(self, bank_id, path, payload):
        # Hindsight Cloud API pattern: /v1/default/banks/{bank_id}/memories/...
        url = f"{self.endpoint}/v1/default/banks/{bank_id}/memories{path}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Shadow-Floor-Engineer/1.0"
        }
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'), 
            headers=headers, 
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"[Hindsight API Error] {e.code}: {e.reason} -> {url} -> {error_body}")
            return None
        except Exception as e:
            print(f"[Hindsight Connection Error]: {e}")
            return None

    def recall(self, query, search_mode="temporal+graph", top_k=3):
        print(f"[Hindsight] Hitting API /recall for query: '{query}'")
        payload = {
            "query": query,
            "search_mode": search_mode,
            "top_k": top_k
        }
        
        # We will query the global 'factory1' bank.
        response = self._make_request("factory1", "/recall", payload)
        
        # Safely parse text specifically to avoid hitting Groq's 6000 token limit
        # The raw Vectorize graph response contains massive vector weightings/embeds!
        extracted_facts = []
        
        if isinstance(response, dict) and "results" in response:
            items = response["results"]
        elif isinstance(response, list):
            items = response
        else:
            items = []
            
        for item in items:
            if isinstance(item, dict) and "content" in item:
                extracted_facts.append(item["content"])
                
        if extracted_facts:
            # Return just a clean block of text joining the relevant narratives
            return "\n".join(extracted_facts)
            
        if isinstance(response, dict) and "results" in response and len(response["results"]) == 0:
            return "[No historical data exists for this machine]"
            
        if response:
            # Fallback if the schema is unexpected, strictly cap size at 2000 chars!
            return str(response)[:2000]
            
        print(" -> Warning: Recall API failed, generating fallback response.")
        return f"[Fallback] Failed to pull tribal knowledge for: {query}"

    def retain(self, content, tags=None, metadata=None):
        if tags is None: tags = []
        if metadata is None: metadata = {}
        
        # The user has created a global bank called 'factory1'
        bank_id = "factory1"
        
        print(f"\n[Hindsight] Hitting API /retain on bank '{bank_id}'...")
        payload = {
            "items": [
                {
                    "content": content,
                    "tags": tags,
                    "metadata": metadata
                }
            ]
        }
        return self._make_request("factory1", "", payload)

    def reflect(self, instruction, target="dispositions"):
        print(f"[Hindsight] Hitting API /reflect to update {target}...")
        payload = {
            "instruction": instruction,
            "target": target
        }
        return self._make_request("factory1", "/reflect", payload)
