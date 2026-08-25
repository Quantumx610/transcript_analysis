import json
from typing import Dict, Any, Optional
from llm_client import default_client

# Import Prompts and Pydantic Models
from prompts.prompt_1_journey import SYSTEM_PROMPT as P1_SYS, USER_PROMPT as P1_USER, Prompt1Schema
from prompts.prompt_2_quality import SYSTEM_PROMPT as P2_SYS, USER_PROMPT as P2_USER, Prompt2Schema

class TranscriptAnalyzer:
    """
    Executes the consolidated 2-Prompt Architecture to extract analytical dimensions.
    """
    def __init__(self, llm_client=None):
        self.client = llm_client or default_client

    def analyze(self, transcript_id: str, transcript_text: str, script_text: Optional[str] = "") -> Dict[str, Any]:
        print(f"Analyzing transcript: {transcript_id}...")
        
        # ---------------------------------------------------------
        # PROMPT 1: Sales Journey, Intent & Outcome Analysis
        # ---------------------------------------------------------
        # Extract Pydantic schema as a formatted JSON string to pass to the prompt
        p1_schema_str = json.dumps(Prompt1Schema.model_json_schema(), indent=2)
        
        prompt_1_result = self.client.call_json(
            system_prompt=P1_SYS,
            user_prompt=P1_USER,
            transcript=transcript_text,
            script_steps=script_text,
            schema=p1_schema_str
        )

        # ---------------------------------------------------------
        # PROMPT 2: Call Quality, Objection & Engagement Analysis
        # ---------------------------------------------------------
        p2_schema_str = json.dumps(Prompt2Schema.model_json_schema(), indent=2)
        
        prompt_2_result = self.client.call_json(
            system_prompt=P2_SYS,
            user_prompt=P2_USER,
            transcript=transcript_text,
            schema=p2_schema_str
        )

        # Aggregate raw outputs for the Bronze layer
        return {
            "transcript_id": transcript_id,
            "prompt_1_journey_intent": prompt_1_result,
            "prompt_2_quality_objection": prompt_2_result
        }