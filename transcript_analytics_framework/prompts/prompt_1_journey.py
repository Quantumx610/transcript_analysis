from pydantic import BaseModel, Field
from typing import List, Optional

# ================================================================================================
# 1. Strict Output Schema for Prompt 1
# ================================================================================================
class Prompt1Schema(BaseModel):
    journey_completion_percentage: int = Field(..., description="Percentage of the expected script completed (0-100).")
    journey_completed: int = Field(..., description="1 if the full journey was completed, 0 otherwise.")
    last_completed_stage: str = Field(..., description="The furthest funnel stage reached.")
    completed_steps: List[str] = Field(default_factory=list, description="List of script steps completed by the agent.")
    missing_steps: List[str] = Field(default_factory=list, description="List of expected script steps missed by the agent.")
    
    qualification_information_collected_percentage: int = Field(..., description="Percentage of required customer info collected (0-100).")
    missing_information: List[str] = Field(default_factory=list, description="List of qualification info the agent failed to collect.")
    
    dropoff_stage: str = Field(..., description="The stage where the conversation dropped off, if applicable.")
    dropoff_reason: str = Field(..., description="Reason for the drop-off.")
    
    customer_intent: str = Field(..., description="Highly Interested, Interested, Considering, Hesitant, Uninterested, or Strongly Rejecting.")
    intent_confidence: int = Field(..., description="Confidence score in the customer intent (0-100).")
    interest_score: int = Field(..., description="Score evaluating the customer's interest level (0-100).")
    purchase_readiness: str = Field(..., description="Hot, Warm, Cold, or Not Applicable.")
    not_interested_reason: str = Field(..., description="Budget Constraint, No Requirement, Timing Issue, Already Using Competitor, Trust Concern, Product Mismatch, Not Decision Maker, Wrong Contact, or No Reason Provided.")
    
    pain_points: List[str] = Field(default_factory=list, description="List of customer problems or challenges extracted.")
    customer_needs: List[str] = Field(default_factory=list, description="List of what the customer is looking for.")
    
    competitor_mentioned: int = Field(..., description="1 if a competitor was mentioned, 0 otherwise.")
    competitor_name: str = Field(..., description="Name of the competitor mentioned, or empty string.")
    
    call_outcome: str = Field(..., description="Interested, Qualified Lead, Callback Requested, Follow-up Required, Not Interested, Wrong Number, Disconnected, Voicemail, or Not Reachable.")
    outcome_confidence: int = Field(..., description="Confidence score in the call outcome (0-100).")
    funnel_stage_reached: str = Field(..., description="Introduction, Qualification, Need Discovery, Product and Pricing Discussion, Objection Handling, or Closure.")

# ================================================================================================
# 2. Prompts
# ================================================================================================
SYSTEM_PROMPT = """
You are an expert Sales Journey Analyst and Customer Intent Evaluator.

Analyze the transcript against the expected sales script and customer interaction.

Your objectives are to:
1. Measure sales journey completion.
2. Identify completed and missing script steps.
3. Evaluate qualification completeness.
4. Determine where and why the conversation dropped.
5. Analyze customer intent and purchase readiness.
6. Identify pain points and customer needs.
7. Identify competitor mentions.
8. Determine final call outcome.
9. Determine the furthest funnel stage reached.

RULES:
- Use only transcript evidence.
- Do not infer facts not present.
- Binary fields must be 1 (Yes) or 0 (No).
- Journey completion percentage must reflect how much of the expected script was completed.
- Qualification percentage must reflect how much required customer information was collected.
- Return only valid JSON.
"""

USER_PROMPT = """
Call Transcript:
{transcript}

Expected Script:
{script_steps}

You MUST output your response as a valid JSON object exactly matching this schema:
{schema}
"""