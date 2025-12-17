"""
Data formatters for UniPile API responses.
Reduces token usage by filtering unnecessary fields.
"""
from typing import Dict, Any, List


def filter_account(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Filter account data to essential fields."""
    return {
        "id": raw.get("id"),
        "provider": raw.get("type", raw.get("provider")),
        "name": raw.get("name"),
        "identifier": raw.get("identifier"),
        "status": raw.get("connection_params", {}).get("status", "OK")
        if isinstance(raw.get("connection_params"), dict) else "OK",
    }


def filter_chat(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Filter chat data to essential fields."""
    attendees = []
    for att in raw.get("attendees", []):
        attendees.append({
            "name": att.get("name"),
            "profile_url": att.get("profile_url"),
        })

    last_message = raw.get("last_message", {})

    return {
        "id": raw.get("id"),
        "attendees": attendees,
        "last_message_text": last_message.get("text") if isinstance(last_message, dict) else None,
        "unread_count": raw.get("unread_count", 0),
    }


def filter_message(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Filter message data to essential fields."""
    sender = raw.get("sender", {})

    return {
        "id": raw.get("id"),
        "sender_name": sender.get("name") if isinstance(sender, dict) else None,
        "text": raw.get("text"),
        "timestamp": raw.get("timestamp"),
        "is_sender": raw.get("is_sender", False),
    }


def filter_list(items: List[Dict[str, Any]], filter_fn) -> List[Dict[str, Any]]:
    """Apply filter function to list of items."""
    return [filter_fn(item) for item in items]
