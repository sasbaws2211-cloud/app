from typing import Final

# Canonical Hubtel provider codes
HUBTEL_PROVIDERS: Final = {
    "mtn": "mtn",
    "MTN Mobile Money": "mtn",
    "mtn momo": "mtn",
    "mtn-momo": "mtn",
    "momo": "mtn",

    "vod": "vod", 
    "vodafone": "vod",
    "vodafone cash": "vod",
    "voda": "vod",

    "tgo": "tgo",
    "airteltigo": "tgo",
    "airtel": "tgo",
    "tigo": "tgo",
    "AirtelTigo Money": "tgo",
    "airtel tigo": "tgo",
    "airtel-tigo": "tgo",
}


def normalize_provider(provider: str) -> str:
    """
    Normalize user/network provider input to Hubtel-compatible code.

    Raises:
        ValueError: if provider is unsupported
    """
    if not provider:
        raise ValueError("Provider is required")

    key = provider.strip().lower()

    if key not in HUBTEL_PROVIDERS:
        raise ValueError(f"Unsupported mobile money provider: {provider}")

    return HUBTEL_PROVIDERS[key]
