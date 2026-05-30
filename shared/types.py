"""Shared types and enums used across all modules."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Platform(str, Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    CUSTOM = "custom"


class Severity(str, Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


class AnomalyType(str, Enum):
    IP_MISMATCH = "ip_mismatch"
    VOLUME_GAP = "volume_gap"
    COST_SPIKE = "cost_spike"


class ProxyStatus(str, Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class MonitoredKey:
    id: Optional[int] = None
    key_prefix: str = ""
    key_encrypted: str = ""
    platform: Platform = Platform.OPENAI
    custom_base_url: Optional[str] = None
    alert_enabled: bool = True
    created_at: Optional[datetime] = None


@dataclass
class ProxyLogEntry:
    id: Optional[int] = None
    key_id: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    method: str = "POST"
    endpoint: str = ""
    request_body_size: int = 0
    response_status: int = 200
    token_count: Optional[int] = None
    source_ip: str = ""
    cost_estimate: float = 0.0


@dataclass
class AnomalyEvent:
    id: Optional[int] = None
    key_id: int = 0
    detected_at: datetime = field(default_factory=datetime.now)
    severity: Severity = Severity.NORMAL
    anomaly_type: AnomalyType = AnomalyType.VOLUME_GAP
    detail_json: str = "{}"
    acknowledged: bool = False


@dataclass
class UsageSnapshot:
    """Official usage data pulled from a provider."""
    platform: Platform
    key_id: int
    timestamp: datetime
    total_calls: int
    total_tokens: int
    total_cost: float
    caller_ips: list[str] = field(default_factory=list)


@dataclass
class KeyStatus:
    """Current status of a monitored key (computed, not stored)."""
    key_id: int
    key_prefix: str
    platform: Platform
    severity: Severity = Severity.NORMAL
    call_gap: int = 0
    cost_gap: float = 0.0
    last_check: Optional[datetime] = None
    abnormal_ips: list[str] = field(default_factory=list)
    proxy_status: ProxyStatus = ProxyStatus.STOPPED
