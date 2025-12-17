"""
UniPile API Client - Core wrapper for UniPile messaging API.
"""
import time
from typing import List, Optional, Dict, Any
import requests

from src.config import Config
from src.models import Account, Chat, Message, ChatParticipant


class UniPileError(Exception):
    """Custom exception for UniPile API errors."""

    def __init__(self, message: str, status_code: int = 0, suggestion: str = ""):
        self.message = message
        self.status_code = status_code
        self.suggestion = suggestion
        super().__init__(self.message)

    def __str__(self) -> str:
        s = f"[{self.status_code}] {self.message}" if self.status_code else self.message
        if self.suggestion:
            s += f"\n💡 Suggestion: {self.suggestion}"
        return s


class UniPileClient:
    """Client for interacting with UniPile API."""

    def __init__(self):
        """Initialize client with credentials from environment."""
        Config.validate()

        self.base_url = Config.get_base_url()
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": Config.UNIPILE_ACCESS_TOKEN,
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make API request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., /accounts)
            params: Query parameters
            json: JSON body for POST requests

        Returns:
            Parsed JSON response

        Raises:
            UniPileError: On API errors
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=30,
            )

            elapsed = round(time.time() - start_time, 2)

            # Handle errors
            if response.status_code == 401:
                raise UniPileError(
                    "Authentication failed",
                    status_code=401,
                    suggestion="Check your UNIPILE_ACCESS_TOKEN in .env file",
                )
            elif response.status_code == 404:
                raise UniPileError(
                    f"Resource not found: {endpoint}",
                    status_code=404,
                    suggestion="Check if the ID is correct",
                )
            elif response.status_code >= 400:
                error_msg = response.text[:200] if response.text else "Unknown error"
                raise UniPileError(
                    f"API error: {error_msg}",
                    status_code=response.status_code,
                )

            return response.json()

        except requests.exceptions.Timeout:
            raise UniPileError(
                "Request timed out",
                suggestion="Check your internet connection or try again",
            )
        except requests.exceptions.ConnectionError:
            raise UniPileError(
                "Connection failed",
                suggestion="Check UNIPILE_DSN in .env and your internet connection",
            )

    # ==================== ACCOUNTS ====================

    def list_accounts(self) -> List[Account]:
        """
        List all connected accounts.

        Returns:
            List of Account objects
        """
        data = self._request("GET", "/accounts")
        items = data.get("items", data) if isinstance(data, dict) else data

        accounts = []
        for item in items:
            try:
                accounts.append(Account(
                    id=item.get("id", ""),
                    provider=item.get("type", item.get("provider", "LINKEDIN")),
                    name=item.get("name"),
                    identifier=item.get("identifier"),
                    status=item.get("connection_params", {}).get("status", "OK")
                    if isinstance(item.get("connection_params"), dict) else "OK",
                ))
            except Exception:
                continue

        return accounts

    def get_account(self, account_id: str) -> Account:
        """Get single account by ID."""
        data = self._request("GET", f"/accounts/{account_id}")
        return Account(
            id=data.get("id", account_id),
            provider=data.get("type", data.get("provider", "LINKEDIN")),
            name=data.get("name"),
            identifier=data.get("identifier"),
            status=data.get("connection_params", {}).get("status", "OK")
            if isinstance(data.get("connection_params"), dict) else "OK",
        )

    # ==================== CHATS ====================

    def list_chats(
        self,
        account_id: str,
        limit: int = 20,
        cursor: Optional[str] = None,
    ) -> tuple[List[Chat], Optional[str]]:
        """
        List chats/conversations for an account.

        Args:
            account_id: UniPile account ID
            limit: Max number of chats to return
            cursor: Pagination cursor

        Returns:
            Tuple of (list of chats, next cursor or None)
        """
        params = {"account_id": account_id, "limit": limit}
        if cursor:
            params["cursor"] = cursor

        data = self._request("GET", "/chats", params=params)
        items = data.get("items", [])

        chats = []
        for item in items:
            # Handle attendees - API returns single attendee_provider_id, not array
            attendees = []
            if item.get("attendees"):
                for att in item.get("attendees", []):
                    attendees.append(ChatParticipant(
                        attendee_id=att.get("attendee_id"),
                        attendee_provider_id=att.get("attendee_provider_id"),
                        name=att.get("name"),
                        profile_url=att.get("profile_url"),
                        profile_picture_url=att.get("profile_picture_url"),
                    ))
            elif item.get("attendee_provider_id"):
                # Single attendee from flat structure
                attendees.append(ChatParticipant(
                    attendee_provider_id=item.get("attendee_provider_id"),
                ))

            # Chat name: use name, subject, or content_type as fallback
            chat_name = item.get("name") or item.get("subject")
            content_type = item.get("content_type", "")
            if content_type == "inmail" and not chat_name:
                chat_name = "[InMail]"

            chats.append(Chat(
                id=item.get("id", ""),
                account_id=account_id,
                provider=item.get("account_type", item.get("provider", "LINKEDIN")),
                name=chat_name,
                attendees=attendees,
                last_message_text=item.get("last_message", {}).get("text")
                if isinstance(item.get("last_message"), dict) else None,
                last_message_timestamp=item.get("timestamp"),  # Use chat timestamp
                unread_count=item.get("unread_count", 0),
                is_group=item.get("type", 0) > 0,  # type > 0 indicates group
            ))

        return chats, data.get("cursor")

    def get_chat(self, chat_id: str) -> Chat:
        """Get single chat by ID."""
        data = self._request("GET", f"/chats/{chat_id}")

        attendees = []
        for att in data.get("attendees", []):
            attendees.append(ChatParticipant(
                attendee_id=att.get("attendee_id"),
                attendee_provider_id=att.get("attendee_provider_id"),
                name=att.get("name"),
                profile_url=att.get("profile_url"),
            ))

        return Chat(
            id=data.get("id", chat_id),
            account_id=data.get("account_id", ""),
            provider=data.get("provider", "LINKEDIN"),
            name=data.get("name"),
            attendees=attendees,
            unread_count=data.get("unread_count", 0),
            is_group=data.get("is_group", False),
        )

    def start_chat(self, account_id: str, attendee_id: str) -> Chat:
        """
        Start a new chat with a connection.

        Args:
            account_id: Your UniPile account ID
            attendee_id: Provider ID of the person to message

        Returns:
            New Chat object
        """
        data = self._request(
            "POST",
            "/chats",
            json={
                "account_id": account_id,
                "attendees_ids": [attendee_id],
            },
        )

        return Chat(
            id=data.get("chat_id", data.get("id", "")),
            account_id=account_id,
            provider="LINKEDIN",
        )

    # ==================== MESSAGES ====================

    def list_messages(
        self,
        chat_id: str,
        limit: int = 50,
        cursor: Optional[str] = None,
    ) -> tuple[List[Message], Optional[str]]:
        """
        List messages in a chat.

        Args:
            chat_id: Chat ID
            limit: Max messages to return
            cursor: Pagination cursor

        Returns:
            Tuple of (list of messages, next cursor or None)
        """
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor

        data = self._request("GET", f"/chats/{chat_id}/messages", params=params)
        items = data.get("items", [])

        messages = []
        for item in items:
            messages.append(Message(
                id=item.get("id", ""),
                chat_id=chat_id,
                sender_id=item.get("sender_id"),
                sender_name=item.get("sender", {}).get("name")
                if isinstance(item.get("sender"), dict) else None,
                text=item.get("text", ""),
                timestamp=item.get("timestamp"),
                is_sender=item.get("is_sender", False),
                attachments=item.get("attachments", []),
            ))

        return messages, data.get("cursor")

    def send_message(self, chat_id: str, text: str) -> Message:
        """
        Send a message to a chat.

        Args:
            chat_id: Chat ID to send to
            text: Message text

        Returns:
            Sent Message object
        """
        data = self._request(
            "POST",
            f"/chats/{chat_id}/messages",
            json={"text": text},
        )

        return Message(
            id=data.get("message_id", data.get("id", "")),
            chat_id=chat_id,
            text=text,
            is_sender=True,
        )

    # ==================== USERS ====================

    def get_user_profile(self, user_id: str, account_id: str) -> Dict[str, Any]:
        """
        Get user/contact profile details by provider ID.

        Args:
            user_id: User provider ID (e.g., LinkedIn member URN)
            account_id: UniPile account ID

        Returns:
            User profile data dict
        """
        params = {"account_id": account_id}
        return self._request("GET", f"/users/{user_id}", params=params)

    def search_linkedin(
        self,
        account_id: str,
        keywords: str,
        api: str = "classic",
        limit: int = 10,
    ) -> tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Search for people on LinkedIn.

        Args:
            account_id: UniPile account ID
            keywords: Search terms (e.g., person's name, company)
            api: LinkedIn interface ("classic", "sales_navigator", "recruiter")
            limit: Max results to return (default: 10)

        Returns:
            Tuple of (list of people/results, next cursor or None)
        """
        # Build payload (account_id goes in query params)
        payload = {
            "api": api,
            "category": "people",
            "keywords": keywords,
            "page_count": limit,
        }

        # account_id goes as query parameter, not in body
        endpoint = f"/linkedin/search?account_id={account_id}"

        data = self._request("POST", endpoint, json=payload)
        items = data.get("items", [])
        cursor = data.get("cursor")

        return items, cursor

    # ==================== CONNECTIONS ====================

    def list_relations(
        self,
        account_id: str,
        limit: int = 50,
        cursor: Optional[str] = None,
    ) -> tuple[List[Dict[str, Any]], Optional[str]]:
        """
        List LinkedIn connections/relations.

        Args:
            account_id: UniPile account ID
            limit: Max results
            cursor: Pagination cursor

        Returns:
            Tuple of (list of connections, next cursor or None)
        """
        params = {"account_id": account_id, "limit": limit}
        if cursor:
            params["cursor"] = cursor

        data = self._request("GET", f"/users/{account_id}/relations", params=params)
        return data.get("items", []), data.get("cursor")
