from datetime import datetime
from typing import List, Dict, Any, Optional

class TelemetryTracker:
    def __init__(self, max_points: int = 60):
        self.max_points = max_points
        self.history: List[Dict[str, Any]] = []
        self.current_sec_events = 0
        self.current_sec_anomalies = 0

    def record_event(self, is_anomaly: bool = False):
        self.current_sec_events += 1
        if is_anomaly:
            self.current_sec_anomalies += 1

    def tick(self, active_incident: Optional[Any] = None) -> Dict[str, Any]:
        now_str = datetime.utcnow().strftime('%H:%M:%S')
        risk_score = 0.0
        exposure = 0.0
        threat_level = 'NOMINAL'

        if active_incident:
            risk_score = getattr(active_incident, 'risk_score', 0.0)
            threat_level = getattr(active_incident, 'severity', 'NOMINAL')
            forecast = getattr(active_incident, 'propagation_forecast', None)
            if forecast:
                horizons = getattr(forecast, 'horizons', [])
                if horizons:
                    exposure = getattr(horizons[0], 'estimated_exposure', 0.0)
            if getattr(active_incident, 'status', '') == 'CONTAINED':
                threat_level = 'CONTAINED'

        point = {
            'timestamp': now_str,
            'events': self.current_sec_events,
            'anomalies': self.current_sec_anomalies,
            'risk': round(risk_score, 1),
            'exposure': round(exposure, 2),
            'threat_level': threat_level
        }
        self.current_sec_events = 0
        self.current_sec_anomalies = 0

        self.history.append(point)
        if len(self.history) > self.max_points:
            self.history.pop(0)

        return point

telemetry_tracker = TelemetryTracker(max_points=60)
