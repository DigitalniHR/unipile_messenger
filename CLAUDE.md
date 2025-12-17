# UniPile Messenger - Claude Code Instructions

You orchestrate LinkedIn messaging through the UniPile API.

## Quick Commands

**Always activate venv first:**
```bash
cd "/Users/matejmatolin/Claude projects/unipile-messenger"
source venv/bin/activate
```

### View & Search

**List Accounts:**
```bash
python scripts/list_accounts.py
```

**List Conversations:**
```bash
python scripts/list_chats.py --account-id ACCOUNT_ID --limit 20
```

**View Thread:**
```bash
python scripts/view_thread.py --chat-id CHAT_ID --show-profile
```

**Recent Messages (last 3 days):**
```bash
python scripts/recent_messages.py --days 3
```

**Search LinkedIn:**
```bash
python scripts/search_linkedin.py "Jakub Krakovsky"
python scripts/search_linkedin.py "Product Manager Prague" --limit 20
```

### Messaging (REQUIRES APPROVAL)

**Send Message:**
```bash
python scripts/send_to_user.py --user-id USER_ID --message "Your message"
```

### Interactive Mode
```bash
python src/main.py
```

## Project Structure

```
unipile-messenger/
├── src/
│   ├── main.py              # Interactive Rich UI
│   ├── unipile_client.py    # Core API client
│   ├── config.py            # Environment config
│   └── models.py            # Pydantic models
├── scripts/
│   ├── list_accounts.py     # CLI: list accounts
│   ├── list_chats.py        # CLI: list conversations
│   ├── view_thread.py       # CLI: view full conversation
│   ├── recent_messages.py   # CLI: show recent messages
│   ├── search_linkedin.py   # CLI: search people on LinkedIn
│   ├── send_to_user.py      # CLI: send message to user (creates chat)
│   ├── logger.py            # Utility: logging
│   └── formatters.py        # Utility: data filtering
├── .env                     # API credentials
└── prompts/                 # Future: AI prompts
```

## Workflow

1. Always activate venv first: `source venv/bin/activate`
2. Check credentials: `python scripts/list_accounts.py`
3. Use interactive mode for exploration: `python src/main.py`
4. Use CLI scripts for quick operations

## Message Sending Workflow (MANDATORY)

**CRITICAL: Always follow this exact sequence:**

1. **Draft message**: Generate or show proposed message text
2. **Present to user**: Display message as plain text with context
3. **WAIT for explicit approval**: User must say "yes", "send", "ok" or similar
4. **Only then execute**: Run send command after approval
5. **Confirm sent**: Show confirmation with message ID

❌ **NEVER skip step 3 - waiting for approval!**

## Error Handling

- **401 Authentication failed**: Check UNIPILE_ACCESS_TOKEN in .env
- **Connection failed**: Verify UNIPILE_DSN is correct
- **404 Not found**: Check if the ID (account/chat) is correct

## API Endpoints Used

- `GET /accounts` - List connected accounts
- `GET /chats` - List conversations
- `GET /chats/{id}/messages` - Get messages
- `POST /chats/{id}/messages` - Send message
- `POST /chats` - Start new conversation

## Pre-approved Actions (NO USER APPROVAL NEEDED)

- List accounts, chats, messages (read-only operations)
- Run scripts with `--help` flag
- Test API connectivity
- View conversation threads
- Show message drafts/suggestions

## ⛔ CRITICAL: NEVER DO WITHOUT EXPLICIT USER APPROVAL

**SENDING MESSAGES:**
1. NEVER run `send_message.py` or any send operation without explicit user approval
2. ALWAYS show the message draft as plain text first
3. WAIT for user to explicitly say "yes", "send it", "ok" or similar confirmation
4. Only then execute the send command
5. If user says "ukaž návrh a pošli" - this means: show draft → WAIT for approval → then send

**Example workflow:**
❌ WRONG: Show draft → immediately send with --yes flag
✅ CORRECT: Show draft → wait for "yes send it" → then send

**Other operations requiring approval:**
- Starting new conversations
- Deleting messages
- Any write operations to API
