# UniPile Messenger

LinkedIn messaging via UniPile API with Rich terminal UI.

## Features

- List connected LinkedIn accounts
- View conversations
- View messages in a conversation
- Send messages **with human approval workflow**
- Interactive Rich terminal interface
- CLI scripts for quick operations

## Important: Human-in-the-Loop

**All message sending requires explicit user approval:**
1. Draft message is shown
2. User reviews and approves
3. Only then message is sent

This ensures you maintain full control over all communications.

## Setup

### 1. Prerequisites

- Python 3.12+
- UniPile account with API access
- Connected LinkedIn account in UniPile dashboard

### 2. Installation

```bash
cd "/Users/matejmatolin/Claude projects/unipile-messenger"
source venv/bin/activate
```

Dependencies are already installed in venv.

### 3. Configuration

Create `.env` file (or copy from `.env.example`):

```bash
UNIPILE_DSN=api20.unipile.com:15036
UNIPILE_ACCESS_TOKEN=your_token_here
LOG_LEVEL=INFO
```

## Usage

**Always activate venv first:**
```bash
cd "/Users/matejmatolin/Claude projects/unipile-messenger"
source venv/bin/activate
```

### Interactive Mode

```bash
python src/main.py
```

Navigate with arrow keys, Enter to select.

### CLI Scripts

📖 **Full scripts documentation:** [scripts/README.md](scripts/README.md)

#### 📋 View & Search

**List connected accounts:**
```bash
python scripts/list_accounts.py
```

**List conversations:**
```bash
python scripts/list_chats.py --account-id ACCOUNT_ID --limit 20
```

**View full conversation thread:**
```bash
python scripts/view_thread.py --chat-id CHAT_ID
python scripts/view_thread.py --chat-id CHAT_ID --show-profile  # with contact details
```

**Show recent messages:**
```bash
python scripts/recent_messages.py --days 3
python scripts/recent_messages.py --days 7 --account-id ACCOUNT_ID
```

**Search people on LinkedIn:**
```bash
python scripts/search_linkedin.py "Jakub Krakovsky"
python scripts/search_linkedin.py "Product Manager Prague" --limit 20
python scripts/search_linkedin.py "John Doe" --api sales_navigator
```

#### 💬 Messaging (Requires Approval)

**Send message to user (recommended):**
```bash
python scripts/send_to_user.py --user-id USER_ID --message "Hello!"
python scripts/send_to_user.py -u USER_ID -m "Hi" --yes  # skip confirmation
```

**Send message to existing chat:**
```bash
python scripts/send_message.py --chat-id CHAT_ID --message "Hello!"
python scripts/send_message.py --chat-id CHAT_ID --message "Hi" --yes  # skip confirmation
```

**Send reply with suggestion:**
```bash
python scripts/send_reply.py --chat-id CHAT_ID  # shows suggested reply first
python scripts/send_reply.py --chat-id CHAT_ID --message "Custom message"
```

## Architecture

```
src/
├── main.py           # Interactive Rich UI
├── unipile_client.py # API client wrapper (accounts, chats, messages, search)
├── config.py         # Environment config
└── models.py         # Pydantic data models

scripts/
├── list_accounts.py     # CLI: list accounts
├── list_chats.py        # CLI: list conversations
├── view_thread.py       # CLI: view full conversation with contact details
├── recent_messages.py   # CLI: show messages from last N days
├── search_linkedin.py   # CLI: search people on LinkedIn
├── send_to_user.py      # CLI: send message to user (creates chat if needed)
├── send_message.py      # CLI: send message to existing chat
├── send_reply.py        # CLI: send reply with suggestion
├── logger.py            # Utility: logging
└── formatters.py        # Utility: data filtering
```

## Available API Methods

**UniPileClient methods:**
- `list_accounts()` - Get connected accounts
- `list_chats(account_id)` - Get conversations
- `list_messages(chat_id)` - Get messages in chat
- `send_to_user(account_id, user_id, text)` - Send message to user (creates chat if needed) **[Recommended]**
- `send_message(chat_id, text)` - Send message to existing chat
- `get_user_profile(user_id, account_id)` - Get LinkedIn profile
- `search_linkedin(account_id, keywords)` - Search people on LinkedIn
- `list_relations(account_id)` - Get LinkedIn connections

## Future Extensions

- [ ] Email integration
- [ ] AI response suggestions (Claude)
- [ ] Outreach sequences
- [ ] SQLite for conversation tracking
- [ ] Webhooks for real-time updates

## API Reference

- [UniPile Docs](https://developer.unipile.com/docs/getting-started)
- [UniPile Dashboard](https://dashboard.unipile.com)
