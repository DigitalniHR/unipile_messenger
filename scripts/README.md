# UniPile Messenger - CLI Scripts

All scripts require activated virtual environment:
```bash
cd "/Users/matejmatolin/Claude projects/unipile-messenger"
source venv/bin/activate
```

---

## 📋 View & Search (Read-only)

### `list_chats.py`
List conversations for an account.

```bash
python scripts/list_chats.py --limit 20
```

**Options:**
- `--account-id, -a` (optional): UniPile account ID (default: from .env)
- `--limit, -l` (default: 20): Max conversations to show

**Output:** Table with Chat ID, Name/Subject, Provider, Unread count

---

### `view_thread.py`
View full conversation thread with contact details.

```bash
python scripts/view_thread.py --chat-id CHAT_ID
python scripts/view_thread.py --chat-id CHAT_ID --show-profile
```

**Options:**
- `--chat-id, -c` (required): Chat ID
- `--show-profile, -p`: Show contact's LinkedIn profile
- `--account-id, -a` (optional): Account ID (default: from .env)

**Output:** Full conversation with timestamps and sender names

---

### `recent_messages.py`
Show messages from last N days across all conversations.

```bash
python scripts/recent_messages.py --days 3
```

**Options:**
- `--days, -d` (default: 3): Number of past days
- `--account-id, -a` (optional): Account ID (default: from .env)

**Output:** Table with Time, Chat, From, Message preview

---

### `search_linkedin.py` 🆕
Search for people on LinkedIn and get their User IDs.

```bash
python scripts/search_linkedin.py "Jakub Krakovsky"
python scripts/search_linkedin.py "Product Manager Prague" --limit 20
python scripts/search_linkedin.py "John Doe" --api sales_navigator
```

**Options:**
- `keywords` (required): Person name, title, company, etc.
- `--account-id, -a` (optional): Account ID (default: from .env)
- `--limit, -l` (default: 10): Max results
- `--api`: LinkedIn interface (classic, sales_navigator, recruiter)

**Output:** Table with Name, Headline, Location, User ID

**Use Case:** Get User ID → Start chat → Send message

---

## 💬 Messaging (Write Operations - Requires Approval ⚠️)

### `send_to_user.py`
Send a message directly to a LinkedIn user (creates chat if needed).

```bash
python scripts/send_to_user.py --user-id USER_ID --message "Hello!"
python scripts/send_to_user.py -u USER_ID -m "Hi" --yes  # skip confirmation
```

**Options:**
- `--user-id, -u` (required): Recipient's provider user ID (from search)
- `--message, -m` (required): Message text
- `--account-id, -a` (optional): Account ID (default: from .env)
- `--yes, -y`: Skip confirmation prompt

**⚠️ IMPORTANT:** Always review message before sending!

---

## Common Workflows

### 1. Find and message someone
```bash
# Step 1: Search for person
python scripts/search_linkedin.py "John Doe"

# Step 2: Copy User ID from results
# User ID: ACoAABRD1jk...

# Step 3: Send message (creates chat automatically)
python scripts/send_to_user.py --user-id ACoAABRD1jk... --message "Hi John!"
```

### 2. Check and respond to recent messages
```bash
# Step 1: See recent messages
python scripts/recent_messages.py --days 3

# Step 2: View full thread and get user details
python scripts/view_thread.py --chat-id CHAT_ID --show-profile

# Step 3: Send reply (use user_id from step 2)
python scripts/send_to_user.py --user-id USER_ID --message "Your reply"
```

### 3. Review all conversations
```bash
# Step 1: List all chats
python scripts/list_chats.py --limit 50

# Step 2: View specific thread
python scripts/view_thread.py --chat-id CHAT_ID
```

---

## Safety Rules ⚠️

**CRITICAL - Message Sending:**
1. ❌ NEVER send messages without explicit approval
2. ✅ ALWAYS show message draft first
3. ✅ WAIT for "yes", "send", "ok" confirmation
4. ✅ Only then execute send command

**This ensures Boss maintains full control over all communications.**
