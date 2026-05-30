"""Platform-specific routing rules for the proxy."""
import re
from shared.types import Platform

# Map URL patterns to platforms
PLATFORM_PATTERNS: list[tuple[re.Pattern, Platform]] = [
    (re.compile(r"https?://api\.openai\.com"), Platform.OPENAI),
    (re.compile(r"https?://api\.anthropic\.com"), Platform.CLAUDE),
    (re.compile(r"https?://api\.deepseek\.com"), Platform.DEEPSEEK),
    (re.compile(r"https?://dashscope\.aliyuncs\.com"), Platform.QWEN),
]

# Pricing per 1K tokens (approximate, for cost estimation)
PRICING: dict[Platform, dict[str, float]] = {
    Platform.OPENAI:   {"input": 0.01, "output": 0.03},    # gpt-4o-mini approximate
    Platform.CLAUDE:   {"input": 0.003, "output": 0.015},  # claude-3-haiku
    Platform.DEEPSEEK: {"input": 0.00014, "output": 0.00028},
    Platform.QWEN:     {"input": 0.0005, "output": 0.002},
    Platform.CUSTOM:   {"input": 0.0, "output": 0.0},
}


def detect_platform(url: str) -> Platform:
    """Detect which platform a URL belongs to."""
    for pattern, platform in PLATFORM_PATTERNS:
        if pattern.search(url):
            return platform
    return Platform.CUSTOM


def extract_token_count(response_body: dict, platform: Platform) -> int | None:
    """Try to extract token usage from API response."""
    if not isinstance(response_body, dict):
        return None
    usage = response_body.get("usage", {})
    total = usage.get("total_tokens")
    return total


def estimate_cost(platform: Platform, token_count: int | None) -> float:
    """Rough cost estimate based on token count."""
    if token_count is None:
        return 0.0
    pricing = PRICING.get(platform, PRICING[Platform.CUSTOM])
    avg_price = (pricing["input"] + pricing["output"]) / 2
    return (token_count / 1000) * avg_price
