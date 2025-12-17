# UniPile Messenger - Plan & TODO

## Current Status: Phase 2 Complete ✅

### Completed - Phase 1: Foundation
- [x] Project structure created
- [x] Virtual environment with dependencies
- [x] Configuration (.env, config.py)
- [x] Pydantic models for API responses
- [x] UniPile API client wrapper
- [x] Interactive Rich UI (main.py)
- [x] Basic CLI scripts (list_accounts, list_chats, send_message)
- [x] Documentation (README, CLAUDE.md)

### Completed - Phase 2: Core Features
- [x] Test API connection with real account ✅
- [x] Test list_chats with real conversations ✅
- [x] Test send_message ✅
- [x] View full conversation thread (view_thread.py)
- [x] Show recent messages (recent_messages.py)
- [x] **LinkedIn search** (search_linkedin.py) ✅
- [x] Get user profiles with details
- [x] Human-in-the-loop approval workflow
- [x] **CRITICAL: Mandatory message approval system** ⚠️

### TODO - Phase 3: Advanced Features
- [ ] Add pagination to interactive UI
- [ ] Add "Start New Conversation" feature
- [ ] Advanced LinkedIn search filters (location, company, etc.)
- [ ] Save/load search results
- [ ] Export conversations to markdown

### TODO - Phase 3: Email Integration
- [ ] Add email models to models.py
- [ ] Add email methods to unipile_client.py
- [ ] Add email menu options to main.py
- [ ] Create email CLI scripts

### TODO - Phase 4: AI Integration
- [ ] Create prompts/response_suggestions.md
- [ ] Add Claude API integration
- [ ] Add "Suggest Response" feature to messages view
- [ ] Human-in-the-loop approval workflow

### TODO - Phase 5: Outreach Sequences
- [ ] Design sequence data model
- [ ] Create sequences/ folder for templates
- [ ] Implement sequence runner
- [ ] Add SQLite for tracking sequence state

## CLI Scripts Overview

### View & Search (Read-only)
| Script | Purpose | Example |
|--------|---------|---------|
| `list_accounts.py` | List connected accounts | `python scripts/list_accounts.py` |
| `list_chats.py` | List conversations | `python scripts/list_chats.py -a ACCOUNT_ID` |
| `view_thread.py` | View conversation with contact details | `python scripts/view_thread.py -c CHAT_ID --show-profile` |
| `recent_messages.py` | Show messages from last N days | `python scripts/recent_messages.py --days 3` |
| `search_linkedin.py` | **Search people on LinkedIn** | `python scripts/search_linkedin.py "John Doe"` |

### Messaging (Write - Requires Approval ⚠️)
| Script | Purpose | Example |
|--------|---------|---------|
| `send_message.py` | Send message to chat | `python scripts/send_message.py -c CHAT_ID -m "Hi"` |
| `send_reply.py` | Send reply with suggestion | `python scripts/send_reply.py -c CHAT_ID` |

### Utilities
| Script | Purpose |
|--------|---------|
| `logger.py` | Logging utilities |
| `formatters.py` | Data filtering for token efficiency |

## Architecture Decisions

### Why Pydantic models?
- Type safety for API responses
- Easy validation
- IDE autocomplete support

### Why separate CLI scripts?
- Quick operations without full UI
- Easy to chain in shell scripts
- Debugging individual features
- Each script = single responsibility

### Why Rich + Questionary?
- Boss prefers terminal UIs over GUIs
- Arrow key navigation (not number input)
- Professional-looking output

### Why Human-in-the-Loop for messaging?
- **CRITICAL**: Boss must approve ALL outgoing messages
- Prevents accidental/incorrect messages
- Maintains full control over communication

## Learning Points

### UniPile API
- Authentication via X-API-KEY header
- Base URL includes port: `api20.unipile.com:15036`
- Pagination uses cursor (not offset)
- Different providers (LINKEDIN, EMAIL) share same endpoints

### Python 3.12 Note
- Python 3.14 breaks pydantic-core build
- Always use Python 3.12 for venv
