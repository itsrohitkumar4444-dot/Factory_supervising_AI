import json
import time

# Assuming hindsight.py is in the local directory based on earlier configurations
from hindsight import HindsightMemory

def seed_factory_knowledge(json_path: str):
    """
    Reads the historical data from JSON and uses hindsight.retain()
    to populate the agent's specific memory banks.
    """
    print(f"Loading tribal knowledge from: {json_path}...")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print("\nInitializing Hindsight Memory...")
    HINDSIGHT_API_KEY = "hsk_9cd76a7b37fb9c9c08c89826bb5602e9_8ec736d30d8a5a90"
    hindsight = HindsightMemory(api_key=HINDSIGHT_API_KEY, storage_path="./hindsight_db")
    
    # 1. Retain the System Persona
    persona = data.get("system_persona", {})
    if persona:
        print("\n--- Seeding System Persona ---")
        hindsight.retain(
            content=f"CORE MISSION: {persona['mission']}",
            tags=["core_directive", "supervisor", "persona"],
            metadata={"bankId": "system_core"}
        )
        
    # 2. Iterate through Memory Banks and Retain Narrative Facts
    memory_banks = data.get("memory_banks", {})
    for bank_id, narratives in memory_banks.items():
        print(f"\n--- Seeding Machine Bank: {bank_id} ---")
        for idx, fact in enumerate(narratives):
            # Attach the machine specific tag to the fact
            combined_tags = fact["tags"] + [bank_id, fact["type"]]
            
            # Use hindsight retain to save the narrative fact
            hindsight.retain(
                content=f"[{fact['type'].upper()}]: {fact['narrative']}",
                tags=combined_tags,
                metadata={
                    "bankId": bank_id,
                    "fact_index": str(idx),
                    "source": "Tribal Knowledge Legacy Import"
                }
            )
            # Short sleep to visually pace the output
            time.sleep(0.2)
            
    print("\n✅ Successfully ingrained all factory tribal knowledge into Hindsight Memory!")

if __name__ == "__main__":
    import os
    # Dynamic path handling ensuring it looks in the same directory
    json_location = os.path.join(os.path.dirname(__file__), 'factory_tribal_knowledge.json')
    seed_factory_knowledge(json_location)
