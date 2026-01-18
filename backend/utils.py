import secrets
import string
from typing import Optional

def generate_invite_code(length: int = 8) -> str:
    """Generate a random invite code for groups"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def format_phone_number(phone: str) -> str:
    """Format phone number to international format"""
    # Remove any non-digit characters
    cleaned = ''.join(filter(str.isdigit, phone))
    
    # If it starts with 0, replace with country code (233 for Ghana)
    if cleaned.startswith('0'):
        return '233' + cleaned[1:]
    
    # If it doesn't start with 233, add it
    if not cleaned.startswith('233'):
        return '233' + cleaned
    
    return cleaned

def validate_mobile_money_provider(provider: str) -> bool:
    """Validate mobile money provider"""
    valid_providers = ['MTN', 'Vodafone', 'AirtelTigo']
    return provider in valid_providers