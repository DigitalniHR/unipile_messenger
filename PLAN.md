# UniPile Messenger - Plan & TODO

## Current Status: Phase 2 Complete ✅

### Completed - Phase 1: Foundation
- [x] Project structure created
- [x] Virtual environment with dependencies
- [x] Configuration (.env, config.py)
- [x] Pydantic models for API responses
- [x] UniPile API client wrapper
- [x] CLI scripts (list_chats, view_thread, recent_messages, search_linkedin, send_to_user)
- [x] Documentation (README, CLAUDE.md)
- [x] Account ID as constant in .env (no need to query)

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
| `list_chats.py` | List conversations | `python scripts/list_chats.py` |
| `view_thread.py` | View conversation with contact details | `python scripts/view_thread.py -c CHAT_ID --show-profile` |
| `recent_messages.py` | Show messages from last N days | `python scripts/recent_messages.py --days 3` |
| `search_linkedin.py` | Search people on LinkedIn | `python scripts/search_linkedin.py "John Doe"` |

### Messaging (Write - Requires Approval ⚠️)
| Script | Purpose | Example |
|--------|---------|---------|
| `send_to_user.py` | Send message to user (creates chat if needed) | `python scripts/send_to_user.py -u USER_ID -m "Hi"` |

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

### Why Claude Code Orchestration?
- Boss uses Claude Code to orchestrate all operations
- Claude Code calls individual scripts as needed
- No need for interactive UI (main.py removed)
- Account ID stored in .env as constant

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
