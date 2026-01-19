# UniPile Messenger - Claude Code Instructions

You orchestrate LinkedIn messaging through the UniPile API.

## Quick Commands

**Always activate venv first:**
```bash
cd "/Users/matejmatolin/Claude projects/unipile-messenger"
source venv/bin/activate
```

### View & Search

**List Conversations:**
```bash
python scripts/list_chats.py --limit 20
```
*Account ID loaded automatically from .env*

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

### Comment Engagement (AI-Orchestrated)

**NEW: AI orchestrates the entire workflow** - Python scripts are simple, atomic tools.

**Usage:**
1. When you want to respond to LinkedIn comments, just say: "zkontroluj linkedin commenty" or "odpověz na komentáře"
2. I will automatically:
   - Fetch unanswered comments (default: last 3 posts)
   - Show you summary
   - Present comments ONE BY ONE with AI-generated responses
   - Wait for your approval for each one

**Default behavior:**
- Checks last 3 posts (you can specify: "zkontroluj posledních 5 postů")
- Shows comment + AI response
- You respond: "pošli" (send), "skip", or write your own text
- Continues until all comments are processed

**Why this works better:**
- Full AI control over the conversation flow
- Natural approval process (no scripts blocking for input)
- Flexible - you can edit responses on the fly
- Rate limiting handled automatically (1s between sends)

**Technical Details** (for reference):
- `list_unanswered_comments.py` - Returns JSON with unanswered comments
- `generate_comment_response.py` - Generates AI response for one comment
- `send_comment.py` - Sends one approved comment to LinkedIn

## Project Structure

```
unipile-messenger/
├── src/
│   ├── unipile_client.py              # Core API client (messaging + posts + comments)
│   ├── config.py                      # Environment config (.env loader)
│   ├── models.py                      # Pydantic models (Account, Chat, Post, Comment, etc.)
│   └── ai_responder.py                # Claude AI response generator (for comment engagement)
├── scripts/
│   ├── list_chats.py                  # CLI: list conversations
│   ├── view_thread.py                 # CLI: view full conversation
│   ├── recent_messages.py             # CLI: show recent messages
│   ├── search_linkedin.py             # CLI: search people on LinkedIn
│   ├── send_to_user.py                # CLI: send message to user (creates chat)
│   ├── list_unanswered_comments.py    # CLI: fetch unanswered comments (JSON)
│   ├── generate_comment_response.py   # CLI: generate AI response for one comment
│   └── send_comment.py                # CLI: send one approved comment
├── prompts/
│   └── comment_response.md            # System prompt for Claude (engagement guidelines)
├── .env                               # API credentials + account IDs
└── requirements.txt                   # Python dependencies (includes anthropic)
```

## Workflow

1. Always activate venv first: `source venv/bin/activate`
2. Claude Code orchestrates and calls scripts as needed
3. Account ID is loaded automatically from .env (UNIPILE_ACCOUNT_ID)

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

**Messaging:**
- `GET /accounts` - List connected accounts
- `GET /chats` - List conversations
- `GET /chats/{id}/messages` - Get messages
- `POST /chats/{id}/messages` - Send message
- `POST /chats` - Start new conversation

**Posts & Comments:**
- `GET /users/{id}/posts` - List user's posts
- `GET /posts/{id}/comments` - List post comments
- `POST /posts/{id}/comments` - Send comment/reply

## Pre-approved Actions (NO USER APPROVAL NEEDED)

**Read-only operations** (safe, no API writes):
- List accounts, chats, messages
- List posts and comments
- Search LinkedIn people
- View conversation threads
- Show message/response drafts/suggestions
- Run scripts with `--help` flag
- Test API connectivity
- Dry-run mode (`--dry-run` flag)

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

**Sending Comment Responses:**
- I will orchestrate the entire workflow
- You will see each comment + AI response ONE BY ONE
- You approve each response individually ("pošli", "skip", or custom text)
- NO auto-sending - every response requires explicit approval

**Other operations requiring approval:**
- Starting new conversations
- Deleting messages
- Any write operations to API
