import os
from openclaw import Agent, CascadeFlow
from openclaw.providers import OllamaProvider, GroqProvider
from hindsight import HindsightMemory

# ==========================================
# 1. Initialize Large Language Models
# ==========================================

# Local Drafter (Ollama): 
# Handles routine log monitoring with near-zero latency and minimal token costs.
# Running phi3:mini ensures orchestration fits easily in the 4GB RTX 3050 VRAM.
local_drafter = OllamaProvider(
    model="phi3:mini",
    base_url="http://localhost:11434"
)

# Verifier Cascade (Groq): 
# Offloads complex anomalies to a much larger model.
# Needs GROQ_API_KEY configured in your environment.
groq_verifier = GroqProvider(
    model="openai/gpt-oss-120b",
    api_key="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"
)

# ==========================================
# 2. Configure Hindsight Memory & Flow
# ==========================================

hindsight = HindsightMemory(
    storage_path="./hindsight_db"
)

# CascadeFlow Logic: 
# The local phi3 drafter processes first. If it detects a complex anomaly 
# (e.g. low confidence or explicitly flagged as "anomaly"), it cascades to Qwen3.
cascade = CascadeFlow(
    drafter=local_drafter,
    verifier=groq_verifier,
    escalation_trigger=lambda response, context: (
        response.confidence_score < 0.85 or 
        "anomaly cascade" in response.text.lower()
    )
)

# Assemble the "Shadow Floor Engineer" OpenClaw Agent
agent = Agent(
    name="Shadow Floor Engineer",
    role="Manufacturing Facility Sensor Log Monitor",
    flow=cascade,
    memory=hindsight
)

# ==========================================
# 3. Incident Processing Logic
# ==========================================

def handle_sensor_spike(sensor_data: dict, technician_notes: str = None):
    """
    Handles a sensor spike incident by leveraging historical tribal knowledge
    and cascading inference to resolve anomalies.
    """
    print(f"--- Processing Incident: {sensor_data['sensor_id']} ---")
    
    # A. RECALL: 4-Way Search (Temporal + Graph)
    # Search history for previous instances of this behavior, looking for "Not in the Manual" fixes
    search_query = f"Spike pattern {sensor_data['pattern']} at {sensor_data['location']}"
    past_incidents = hindsight.recall(
        query=search_query,
        search_mode="temporal+graph",
        top_k=3
    )
    
    # B. ANALYZE 
    prompt = f"""
    Analyze the recent sensor anomaly.
    Sensor Data: {sensor_data}
    
    Past 'Tribal Knowledge' Context:
    {past_incidents}
    
    Current Technician Notes:
    {technician_notes if technician_notes else 'None'}
    
    Determine if this is a known issue (like a coolant blockage) or a new mechanical failure.
    """
    
    analysis_result = agent.run(prompt)
    print("\n[Agent Analysis]")
    print(f"Resolved by: {analysis_result.provider_used}") # Will report Ollama or Groq
    print(f"Conclusion: {analysis_result.text}\n")
    
    # C. RETAIN & REFLECT
    if technician_notes:
        # Retain the narrative facts to preserve the technician's manual findings
        hindsight.retain(
            content=f"Technician Observation: {technician_notes}. Analysis Conclusion: {analysis_result.text}",
            tags=["tribal_knowledge", "maintenance", sensor_data['location']],
            metadata={"sensor_id": sensor_data['sensor_id'], "pattern": sensor_data['pattern']}
        )
        print("-> Narrative facts retained in Hindsight.")
        
        # Reflect to update agent Dispositions if a red herring is identified
        if "red herring" in technician_notes.lower() or "false positive" in technician_notes.lower():
            hindsight.reflect(
                instruction=f"UPDATE DISPOSITION: Treat sensor pattern '{sensor_data['pattern']}' at {sensor_data['location']} as a red herring caused by external factors (e.g., coolant blockage). Do not trigger high-severity hardware wear alerts for this pattern.",
                target="dispositions"
            )
            print("-> Agent dispositions updated to ignore this red herring in the future.")

# ==========================================
# 4. Simulation Execution
# ==========================================

if __name__ == "__main__":
    # Simulating the "Line 3 Sensor Spike" incident
    spike_event = {
        "sensor_id": "L3-BRG-07",
        "location": "Line 3 Extruder Bearing",
        "pattern": "Rapid 400Hz oscillation with 15% temperature increase",
        "severity": "high"
    }
    
    # Messy real-world note from a technician
    maria_notes = (
        "The official log said bearing failure imminent, but Maria found a coolant "
        "blockage under the housing causing localized heat soak. The bearing is fine, "
        "it's a red herring sensor pattern."
    )
    
    handle_sensor_spike(spike_event, technician_notes=maria_notes)
