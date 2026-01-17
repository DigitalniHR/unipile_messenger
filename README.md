# UniPile Messenger

LinkedIn messaging via UniPile API, orchestrated by Claude Code.

## Features

- View conversations
- View messages in a conversation
- Send messages **with human approval workflow**
- CLI scripts for operations
- Claude Code orchestration

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
UNIPILE_ACCOUNT_ID=your_account_id_here
LOG_LEVEL=INFO
```

## Usage

**Orchestrated by Claude Code** - Claude Code calls these scripts as needed.

**Always activate venv first:**
```bash
cd "/Users/matejmatolin/Claude projects/unipile-messenger"
source venv/bin/activate
```

### CLI Scripts

📖 **Full scripts documentation:** [scripts/README.md](scripts/README.md)

#### 📋 View & Search

**List conversations:**
```bash
python scripts/list_chats.py [--limit 20]
```
*Account ID loaded automatically from .env*

**View full conversation thread:**
```bash
python scripts/view_thread.py --chat-id CHAT_ID
python scripts/view_thread.py --chat-id CHAT_ID --show-profile  # with contact details
```

**Show recent messages:**
```bash
python scripts/recent_messages.py --days 3
```
*Account ID loaded automatically from .env*

**Search people on LinkedIn:**
```bash
python scripts/search_linkedin.py "Jakub Krakovsky"
python scripts/search_linkedin.py "Product Manager Prague" --limit 20
python scripts/search_linkedin.py "John Doe" --api sales_navigator
```

#### 💬 Messaging (Requires Approval)

**Send message:**
```bash
python scripts/send_to_user.py --user-id USER_ID --message "Hello!"
python scripts/send_to_user.py -u USER_ID -m "Hi" --yes  # skip confirmation
```

## Architecture

```
src/
├── unipile_client.py # API client wrapper (accounts, chats, messages, search)
├── config.py         # Environment config (.env loader)
└── models.py         # Pydantic data models

scripts/
├── list_chats.py        # CLI: list conversations
├── view_thread.py       # CLI: view full conversation with contact details
├── recent_messages.py   # CLI: show messages from last N days
├── search_linkedin.py   # CLI: search people on LinkedIn
└── send_to_user.py      # CLI: send message to user (creates chat if needed)
```

## Available API Methods

**UniPileClient methods:**
- `list_accounts()` - Get connected accounts
- `list_chats(account_id)` - Get conversations
- `list_messages(chat_id)` - Get messages in chat
- `send_to_user(account_id, user_id, text)` - Send message to user (creates chat if needed)
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
