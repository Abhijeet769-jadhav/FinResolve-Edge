from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class EventType(str, Enum):
    LOGIN = "LOGIN"
    FAILED_LOGIN = "FAILED_LOGIN"
    OTP_FAILURE = "OTP_FAILURE"
    TRANSACTION = "TRANSACTION"
    DEVICE_CHANGE = "DEVICE_CHANGE"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    NEW_RECIPIENT = "NEW_RECIPIENT"
    MERCHANT_PAYMENT = "MERCHANT_PAYMENT"
    API_ERROR = "API_ERROR"

class FinancialEvent(BaseModel):
    event_id: str
    timestamp: str
    type: EventType
    account_id: str
    device_id: str
    merchant_id: Optional[str] = None
    recipient_id: Optional[str] = None
    amount: float = 0.0
    location: str
    ip: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EdgeNodeSignal(BaseModel):
    signal_id: str
    edge_node: str
    signal_type: str
    risk_score: float
    affected_entities: int
    timestamp: str
    payload_hash: str
    signature_status: str = "VERIFIED"
    algorithm: str = "ML-DSA-65 (Demonstrational Abstraction)"
    raw_preview: Optional[str] = None

class AnomalyFactor(BaseModel):
    rule: str
    score_contribution: float
    description: str

class AnomalyReport(BaseModel):
    event_id: str
    account_id: str
    device_id: str
    risk_score: float
    classification: str # NORMAL, ELEVATED, HIGH, CRITICAL
    reasons: List[str]
    factors: List[AnomalyFactor]
    timestamp: str

class ThreatDNA(BaseModel):
    attack_type: str
    characteristics: List[str]
    velocity: str # LOW, MEDIUM, HIGH, CRITICAL
    coordination: str # LOW, MEDIUM, HIGH, CRITICAL
    geographic_spread: str # LOW, MEDIUM, HIGH
    recipient_concentration: str # LOW, MEDIUM, HIGH
    historical_similarity: float
    notes: Optional[str] = None

class ForecastHorizon(BaseModel):
    label: str # NOW, 15m, 30m, 60m
    minutes: int
    affected_accounts: int
    transactions_at_risk: int
    estimated_exposure: float # in INR
    propagation_level: str

class PropagationForecast(BaseModel):
    incident_id: str
    generated_at: str
    horizons: List[ForecastHorizon]
    primary_propagation_vector: str
    velocity_score: float

class SimulationResult(BaseModel):
    strategy: str
    label: str
    description: str
    estimated_affected_accounts: int
    estimated_transactions_at_risk: int
    estimated_financial_exposure: float
    propagation: str # LOW, MEDIUM, HIGH, CRITICAL
    customer_friction: str # LOW, MEDIUM, HIGH
    containment_score: float
    is_recommended: bool = False
    recommendation_reason: Optional[str] = None

class Incident(BaseModel):
    id: str
    threat_type: str
    severity: str # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float
    risk_score: float
    first_detected: str
    last_updated: str
    affected_accounts: List[str] = Field(default_factory=list)
    affected_devices: List[str] = Field(default_factory=list)
    affected_recipients: List[str] = Field(default_factory=list)
    affected_merchants: List[str] = Field(default_factory=list)
    regions: List[str] = Field(default_factory=list)
    current_stage: str
    status: str # ACTIVE, CONTAINED, REJECTED
    event_ids: List[str] = Field(default_factory=list)
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    threat_dna: Optional[ThreatDNA] = None
    propagation_forecast: Optional[PropagationForecast] = None
    recommended_action: Optional[Dict[str, Any]] = None
    containment_action: Optional[Dict[str, Any]] = None

class SimulateRequest(BaseModel):
    incident_id: str
    horizon: str = "60m"
    strategy: Optional[str] = None

class ResponseActionRequest(BaseModel):
    incident_id: str
    action_type: str # APPROVE or REJECT
    strategy: str
    target_entities: List[str] = Field(default_factory=list)
    analyst_note: Optional[str] = None

class InjectAttackRequest(BaseModel):
    scenario: str = "account_takeover" # account_takeover, mule_network, coordinated_fraud, recipient_attack, credential_stuffing, gateway_outage, merchant_failure, mixed_attack, weak_signals, normal

class WorkflowStage(BaseModel):
    stage_id: int
    code: str
    title: str
    subtitle: str
    status: str # IDLE, ACTIVE, TRIGGERED, CONTAINED
    timestamp: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
