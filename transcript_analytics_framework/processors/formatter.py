import json
import csv
from typing import Dict, Any, List
from config import BRONZE_DIR, SILVER_DIR, GOLD_DIR

class OutputFormatter:
    """
    Manages the 3-Layer Data Storage Architecture (Bronze, Silver, Gold).
    """

    def save_bronze(self, transcript_id: str, raw_results: Dict[str, Any]):
        """Layer 1: Raw Prompt Outputs for auditability."""
        filepath = BRONZE_DIR / f"{transcript_id}_raw.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(raw_results, f, indent=4)
        print(f"  -> Bronze layer saved: {filepath.name}")

    def save_silver(self, transcript_id: str, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """Layer 2: Merged JSON - Single source of truth."""
        merged_record = {
            "transcript_id": transcript_id,
            "journey_and_intent": raw_results.get("prompt_1_journey_intent", {}),
            "quality_and_objections": raw_results.get("prompt_2_quality_objection", {})
        }

        filepath = SILVER_DIR / f"{transcript_id}_merged.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(merged_record, f, indent=4)
        print(f"  -> Silver layer saved: {filepath.name}")
        
        return merged_record

    def save_gold(self, silver_records: List[Dict[str, Any]], batch_name: str = "analytics_export"):
        """Layer 3: Flattened Analytics Table formatted for SQL/BI."""
        if not silver_records:
            return

        filepath = GOLD_DIR / f"{batch_name}.csv"
        flattened_data = []
        
        for record in silver_records:
            p1 = record.get("journey_and_intent", {})
            p2 = record.get("quality_and_objections", {})
            
            flat_row = {
                "transcript_id": record.get("transcript_id"),
                "journey_completed": p1.get("journey_completed", ""),
                "customer_intent": p1.get("customer_intent", ""),
                "not_interested_reason": p1.get("not_interested_reason", ""),
                "call_outcome": p1.get("call_outcome", ""),
                "dropoff_stage": p1.get("dropoff_stage", ""),
                "objection_present": p2.get("objection_present", ""),
                "overall_objection_handling_quality": p2.get("overall_objection_handling_quality", ""),
                "overall_quality_score": p2.get("overall_quality_score", ""),
                "engagement_level": p2.get("engagement_level", "")
            }
            flattened_data.append(flat_row)

        headers = list(flattened_data[0].keys())

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(flattened_data)
            
        print(f"  -> Gold layer (CSV) saved: {filepath.name} with {len(silver_records)} rows.")