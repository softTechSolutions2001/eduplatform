"""
File: backend/users/utils.py
Purpose: Utility functions for user authentication and security logging
Date Created: 2025-06-20 07:30:12 UTC
Created By: sujibeautysalon
Environment: Production

This file contains utility functions for:
- IP address extraction from requests
- User agent parsing and device type detection
- Location detection from IP addresses
- Secure logging utilities for PII protection

Version: 1.0.0
Dependencies: Django, socket
"""

import socket
import logging
import hashlib
from django.conf import settings

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """
    Extract real client IP from request headers.
    Handles proxy forwarding and load balancer scenarios.

    Args:
        request: Django HttpRequest object

    Returns:
        str: Client IP address or '0.0.0.0' if unavailable
    """
    # Check for forwarded IP from load balancers/proxies
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Get first IP in chain (original client)
        ip = x_forwarded_for.split(',')[0].strip()
        logger.debug(f"IP extracted from X-Forwarded-For: {ip}")
        return ip

    # Check for real IP header (some proxies use this)
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        logger.debug(f"IP extracted from X-Real-IP: {x_real_ip}")
        return x_real_ip

    # Fallback to direct connection IP
    remote_addr = request.META.get('REMOTE_ADDR', '0.0.0.0')
    logger.debug(f"IP extracted from REMOTE_ADDR: {remote_addr}")
    return remote_addr

def get_user_agent(request):
    """
    Extract user agent string from request headers.

    Args:
        request: Django HttpRequest object

    Returns:
        str: User agent string or 'Unknown' if unavailable
    """
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    # Truncate extremely long user agents for database storage
    return user_agent[:500] if user_agent else 'Unknown'

def get_device_type(user_agent):
    """
    Determine device type from user agent string.

    Args:
        user_agent: User agent string

    Returns:
        str: Device type ('Desktop', 'Mobile', 'Tablet', 'Unknown')
    """
    if not user_agent or user_agent == 'Unknown':
        return 'Unknown'

    user_agent_lower = user_agent.lower()

    # Check for mobile devices
    mobile_keywords = ['mobile', 'android', 'iphone', 'ipod', 'blackberry', 'windows phone']
    if any(keyword in user_agent_lower for keyword in mobile_keywords):
        return 'Mobile'

    # Check for tablets
    tablet_keywords = ['ipad', 'tablet', 'kindle']
    if any(keyword in user_agent_lower for keyword in tablet_keywords):
        return 'Tablet'

    # Default to desktop
    return 'Desktop'

def get_location_from_ip(ip_address):
    """
    Get approximate location from IP address.
    This is a simplified implementation. In production, use a proper
    geolocation service like MaxMind GeoIP2.

    Args:
        ip_address: IP address string

    Returns:
        str: Location information or 'Unknown'
    """
    if not ip_address or ip_address in ['0.0.0.0', '127.0.0.1', 'localhost']:
        return 'Local/Unknown'

    try:
        # Basic hostname lookup (limited information)
        hostname = socket.gethostbyaddr(ip_address)[0]
        # Extract meaningful location info from hostname if possible
        if 'local' in hostname.lower():
            return 'Local Network'
        return hostname[:100]  # Truncate for storage
    except (socket.herror, socket.gaierror):
        logger.debug(f"Could not resolve hostname for IP: {ip_address}")
        return 'Unknown'

def sanitize_email_for_logging(email):
    """
    Sanitize email address for secure logging.
    Returns a hashed version that maintains uniqueness without exposing PII.

    Args:
        email: Email address string

    Returns:
        str: Sanitized email identifier
    """
    if not email:
        return 'unknown'

    # Create a hash of the email for logging
    email_hash = hashlib.sha256(email.encode()).hexdigest()[:8]
    # Keep the domain for context but hash the local part
    domain = email.split('@')[-1] if '@' in email else 'unknown'
    return f"user_{email_hash}@{domain}"

def get_masked_ip(ip_address):
    """
    Mask IP address for privacy-compliant logging.
    Masks the last octet for IPv4 addresses.

    Args:
        ip_address: IP address string

    Returns:
        str: Masked IP address
    """
    if not ip_address or ip_address == '0.0.0.0':
        return '0.0.0.0'

    try:
        # For IPv4, mask last octet
        if '.' in ip_address and ip_address.count('.') == 3:
            parts = ip_address.split('.')
            return f"{parts[0]}.{parts[1]}.{parts[2]}.xxx"
        # For IPv6 or other formats, mask appropriately
        elif ':' in ip_address:
            parts = ip_address.split(':')
            return f"{':'.join(parts[:4])}:xxxx:xxxx:xxxx:xxxx"
        else:
            return 'masked'
    except Exception:
        return 'masked'
