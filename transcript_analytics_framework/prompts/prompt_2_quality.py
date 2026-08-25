from pydantic import BaseModel, Field
from typing import List

# ================================================================================================
# 1. Strict Output Schema for Prompt 2
# ================================================================================================
class Prompt2Schema(BaseModel):
    objection_present: int = Field(..., description="1 if objection is present, 0 otherwise.")
    objection_count: int = Field(..., description="Total number of objections raised.")
    
    objection_categories: List[str] = Field(default_factory=list, description="Price, Timing, Need, Trust, Competitor, Authority, Product Fit.")
    objection_handling_qualities: List[str] = Field(default_factory=list, description="Evaluation of handling quality per objection.")
    objection_resolved_flags: List[int] = Field(default_factory=list, description="1 if resolved, 0 if not, for each objection.")
    
    overall_objection_handling_quality: str = Field(..., description="Excellent, Good, Average, or Poor.")
    overall_resolution_status: str = Field(..., description="Resolved or Unresolved.")
    objection_resolution_rate: int = Field(..., description="Percentage of objections resolved (0-100).")
    
    call_interaction_quality_score: int = Field(..., description="Score 0-100.")
    call_interaction_quality_rating: str = Field(..., description="Excellent, Good, Average, or Poor.")
    call_interaction_quality_reason: str = Field(..., description="Reasoning for interaction quality score.")
    
    adaptability_score: int = Field(..., description="Score 0-100.")
    adaptability_rating: str = Field(..., description="Excellent, Good, Average, or Poor.")
    adaptability_reason: str = Field(..., description="Reasoning for adaptability score.")
    
    persuasiveness_score: int = Field(..., description="Score 0-100.")
    persuasiveness_rating: str = Field(..., description="Excellent, Good, Average, or Poor.")
    persuasiveness_reason: str = Field(..., description="Reasoning for persuasiveness score.")
    
    product_pitch_clarity_score: int = Field(..., description="Score 0-100.")
    product_pitch_clarity_rating: str = Field(..., description="Excellent, Good, Average, or Poor.")
    product_pitch_clarity_reason: str = Field(..., description="Reasoning for product pitch clarity.")
    
    product_proposition_clarity_score: int = Field(..., description="Score 0-100.")
    product_proposition_clarity_rating: str = Field(..., description="Excellent, Good, Average, or Poor.")
    product_proposition_clarity_reason: str = Field(..., description="Reasoning for product proposition clarity.")
    
    customer_query_resolution_score: int = Field(..., description="Score 0-100.")
    customer_query_resolution_rating: str = Field(..., description="Excellent, Good, Average, or Poor.")
    
    queries_asked: int = Field(..., description="Number of queries asked by the customer.")
    queries_answered: int = Field(..., description="Number of queries successfully answered by the agent.")
    query_resolution_rate: int = Field(..., description="Percentage of queries answered (0-100).")
    customer_query_resolution_reason: str = Field(..., description="Reasoning for query resolution score.")
    
    customer_comprehension_support_score: int = Field(..., description="Score 0-100.")
    customer_comprehension_support_rating: str = Field(..., description="Excellent, Good, Average, or Poor.")
    
    customer_confusion_detected: int = Field(..., description="1 if customer confusion was detected, 0 otherwise.")
    clarification_requests_count: int = Field(..., description="Number of times customer asked for clarification.")
    agent_rephrased_information: int = Field(..., description="1 if agent rephrased information to aid comprehension, 0 otherwise.")
    customer_comprehension_support_reason: str = Field(..., description="Reasoning for comprehension support score.")
    
    overall_quality_score: int = Field(..., description="Calculated weighted overall score (0-100).")
    overall_assessment: str = Field(..., description="Excellent, Good, Average, or Poor based on overall score.")
    
    engagement_level: str = Field(..., description="High, Medium, or Low.")
    engagement_drop_detected: int = Field(..., description="1 if a significant drop in engagement was detected, 0 otherwise.")
    engagement_drop_stage: str = Field(..., description="The stage where engagement dropped.")
    
    customer_participation_score: int = Field(..., description="Score evaluating customer participation (0-100).")
    agent_question_count: int = Field(..., description="Number of questions asked by the agent.")
    customer_question_count: int = Field(..., description="Number of questions asked by the customer.")
    customer_response_depth: str = Field(..., description="Detailed, Moderate, or Minimal.")

# ================================================================================================
# 2. Prompts
# ================================================================================================
SYSTEM_PROMPT = """
You are an expert Sales QA Auditor, Objection Handling Analyst and Customer Engagement Evaluator.

Analyze the transcript and evaluate:
1. Objections raised by the customer.
2. Objection handling effectiveness.
3. Quality of interaction.
4. Adaptability of the agent.
5. Persuasiveness of the agent.
6. Product pitch clarity.
7. Product proposition clarity.
8. Customer query resolution.
9. Customer comprehension support.
10. Customer engagement quality.

SCORING RULES (0-100 Scale):
90-100 = Excellent
75-89 = Good
60-74 = Average
0-59 = Poor

IMPORTANT:
- Use transcript evidence only.
- Do not evaluate voice, accent, emotion, speech speed, pauses, pitch or tone.
- Binary fields: 1 = Yes, 0 = No.
- Overall quality score must be calculated using:
  20% Call Interaction Quality
  20% Product Pitch Clarity
  15% Adaptability
  15% Persuasiveness
  15% Product Proposition Clarity
  15% Customer Query Resolution
"""

USER_PROMPT = """
Call Transcript:
{transcript}

You MUST output your response as a valid JSON object exactly matching this schema:
{schema}
"""