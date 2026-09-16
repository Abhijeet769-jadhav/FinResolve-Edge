from typing import Dict, Any, List, Optional
from datetime import datetime
from models import Incident, ResponseActionRequest
from graph_engine import graph_engine

class ResponseEngine:
    def __init__(self):
        self.action_history: List[Dict[str, Any]] = []

    def execute_approval(self, incident: Incident, request: ResponseActionRequest) -> Dict[str, Any]:
        """Executes containment response upon analyst authorization, modifying actual backend state."""
        now_ts = datetime.utcnow().isoformat()

        # Isolate entities in graph
        for dev_id in incident.affected_devices:
            graph_engine.mark_entity_contained(dev_id, request.strategy)
        for rec_id in incident.affected_recipients:
            graph_engine.mark_entity_contained(rec_id, request.strategy)
        for acc_id in incident.affected_accounts:
            graph_engine.mark_entity_contained(acc_id, f"PROTECTED_BY_{request.strategy}")

        # Update incident status
        incident.status = "CONTAINED"
        incident.current_stage = "CONTAINED"
        incident.last_updated = now_ts

        action_record = {
            "incident_id": incident.id,
            "action_type": "APPROVE",
            "strategy": request.strategy,
            "analyst_note": request.analyst_note or "Analyst approved recommended containment protocol.",
            "executed_at": now_ts,
            "isolated_entities": incident.affected_devices + incident.affected_recipients,
            "status": "SUCCESS"
        }
        incident.containment_action = action_record
        self.action_history.append(action_record)

        # Add to timeline
        incident.timeline.append({
            "timestamp": now_ts,
            "stage": "CONTAINED",
            "summary": f"Response Executed: {request.strategy}",
            "detail": f"Threat contained by SOC Analyst. Entities {action_record['isolated_entities']} isolated."
        })

        return action_record

    def execute_rejection(self, incident: Incident, request: ResponseActionRequest) -> Dict[str, Any]:
        """Records analyst rejection, leaving incident active with escalation note."""
        now_ts = datetime.utcnow().isoformat()
        incident.status = "ACTIVE"
        incident.current_stage = "REJECTED_RE-TRIAGE"
        incident.last_updated = now_ts

        action_record = {
            "incident_id": incident.id,
            "action_type": "REJECT",
            "strategy": request.strategy,
            "analyst_note": request.analyst_note or "Action declined by analyst. Seeking alternate remediation.",
            "executed_at": now_ts,
            "status": "REJECTED"
        }
        self.action_history.append(action_record)

        incident.timeline.append({
            "timestamp": now_ts,
            "stage": "REJECTED",
            "summary": f"Response Rejected: {request.strategy}",
            "detail": action_record["analyst_note"]
        })

        return action_record

response_engine = ResponseEngine()
