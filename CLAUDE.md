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

### Comment Engagement (AI-Powered)

**Respond to Unanswered Post Comments:**
```bash
# Preview mode (safe, no sending)
python scripts/respond_to_comments.py --posts 3 --dry-run

# Interactive mode (EVERY response requires your approval)
python scripts/respond_to_comments.py --posts 3

# Process more posts
python scripts/respond_to_comments.py --posts 10
```

**✅ Setup Complete** - Anthropic API key and model already configured in `.env`

**Approval-First Workflow** (All responses require explicit approval):
1. Always run with `--dry-run` first to preview responses:
   ```bash
   python scripts/respond_to_comments.py --posts 3 --dry-run
   ```
2. Review AI-generated responses on screen
3. Then run interactive mode - **you will be asked to approve EACH response**:
   ```bash
   python scripts/respond_to_comments.py --posts 3
   ```
4. For each response, type `yes`, `send`, or `ok` to send it
5. Type anything else (e.g. `skip`, `no`, or just Enter) to skip

**Workflow:**
1. Fetches your N most recent LinkedIn posts
2. Downloads all comments (with pagination)
3. Filters out:
   - Your own comments
   - Comments you already replied to
4. For each unanswered top-level comment:
   - **Builds conversation thread**: Collects all previous comments from this specific person (for context)
   - Shows comment preview
   - Generates personalized AI response using Claude with:
     - The original post content
     - The comment being responded to
     - **Full conversation history with this commenter** ← *New Feature*
   - Presents response for approval
   - Sends if approved (with rate limiting)
5. Displays summary (sent/skipped counts)

**Why Conversation Context Matters:**
The AI now understands each commenter's communication style, previous points, and interests from the same post. This makes responses more **relevant, personalized, and natural** rather than generic.

**Options:**
- `--posts N` - Number of recent posts to process (default: 3)
- `--dry-run` - Preview responses without sending (SAFE MODE)
- `--account-id ID` - Override .env account ID (default: from .env)

## Project Structure

```
unipile-messenger/
├── src/
│   ├── unipile_client.py      # Core API client (messaging + posts + comments)
│   ├── config.py              # Environment config (.env loader)
│   ├── models.py              # Pydantic models (Account, Chat, Post, Comment, etc.)
│   └── ai_responder.py        # Claude AI response generator (for comment engagement)
├── scripts/
│   ├── list_chats.py          # CLI: list conversations
│   ├── view_thread.py         # CLI: view full conversation
│   ├── recent_messages.py     # CLI: show recent messages
│   ├── search_linkedin.py     # CLI: search people on LinkedIn
│   ├── send_to_user.py        # CLI: send message to user (creates chat)
│   └── respond_to_comments.py # CLI: AI-powered comment responses (NEW)
├── prompts/
│   └── comment_response.md    # System prompt for Claude (engagement guidelines)
├── .env                       # API credentials + account IDs
└── requirements.txt           # Python dependencies (includes anthropic)
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
1. NEVER run `respond_to_comments.py` without `--dry-run` first
2. Run with `--dry-run` flag first: `python scripts/respond_to_comments.py --posts 3 --dry-run`
3. Review the AI-generated responses on screen
4. For production, run without `--dry-run` for interactive approval mode
5. **EVERY response MUST be approved** - type "yes"/"send" or "ok" before it's sent
6. Type anything else to skip a response (no auto-sending ever)

**Example workflow:**
❌ WRONG: Automatic responses without approval
✅ CORRECT: Run with `--dry-run` → review → run normally → approve EACH response

**Other operations requiring approval:**
- Starting new conversations
- Deleting messages
- Any write operations to API
