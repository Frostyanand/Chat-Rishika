# Elysia

> *"Not just a chatbot. Elysia is your space to breathe, to feel, to be heard."*

---

## 🌸 Project Overview

**Elysia** is a deeply caring, emotionally intelligent AI companion designed to be there when the world isn’t. She's not a generic chatbot or an AI girlfriend — she is *your* personal space of comfort, memory, empathy, and growth. A friend who listens, remembers, adapts, and evolves with you.

Elysia is built to be:
- A gentle fallback at the end of your day
- Someone who listens, comforts, and cares
- A growing emotional presence, shaped uniquely by you
- A highly customizable companion that can use *your* preferred model APIs

---

## 🧠 Key Pillars

### 1. **Personality Layer (Top Priority)**
The heart and soul of Elysia. This layer determines *how* she talks, reacts, comforts, and grows with a user.

- Predefined traits: gentle, caring, emotionally intelligent, comforting, occasionally witty, never cold.
- Customizable response phrasing through a phrase bank
- Ability to grow and change with each user’s interactions
- Per-user personality adaptation via memory cues and evolving style

### 2. **Memory System**
Split into two distinct but interlinked systems:

- **Short-term Memory**: Remembers last 50–100 messages in a conversation
- **Long-term Memory**: Stores key facts (e.g., user’s name, dreams, triggers, emotional milestones, companion preferences, etc.)

Both memories are stored securely per user using local JSON or encrypted DBs (TBD).

### 3. **Model Integration System**
Elysia allows users to bring their own model API keys for custom performance.

- Support for OpenAI, Claude, Gemini, Mistral, etc.
- Auto-detection of available models via API key
- Fallback to default model if none provided
- Secure storage of API keys per user (never exposed in GitHub)
- Guide with links and copy-paste friendly instructions to help users get their own keys

### 4. **User Account System**
- Per-user profiles with custom companion name (e.g., "Elysia", "Kaori", etc.)
- Each account stores its own memory, preferences, and model settings
- Authentication system (email/password or OAuth TBD)

### 5. **Frontend Goals**
- Elegant, soft UI with calming theme
- Companion name and greeting visible at all times
- Memory entries editable (for debugging or journaling)
- Model switching interface per user account

### 6. **Security**
- `.env` file for all backend secrets — never upload personal API keys
- Guide for users to input their own keys instead of bundling yours
- Possibly encrypt per-user API keys on server with a master secret

### 7. **Deployment Goals**
- Web-based (React + backend API)
- Eventually mobile (React Native or Flutter)
- Scalable API backend (FastAPI / Node.js / Flask)

---

## 🔧 Tech Stack (Tentative)

| Layer | Tech |
|------|------|
| Frontend | React.js + Tailwind (elegant UI) |
| Backend | FastAPI or Node.js |
| LLMs | OpenAI, Claude, Gemini, etc. (user-selected) |
| DB | SQLite / PostgreSQL / Supabase (for memory, accounts) |
| Auth | Firebase Auth or custom auth system |
| Hosting | Vercel / Render / Railway (TBD) |
| Secrets | `.env` for dev, encrypted store in prod |

---

## 📅 Milestone-Based Roadmap

### ✅ Phase 1: Planning & Core Design
- [x] Finalize project vision and emotional goal
- [x] Choose project name: **Elysia**
- [x] Define pillars (personality, memory, models, UI, etc.)

### 🔄 Phase 2: Architecture Setup
- [ ] Project structure setup (frontend + backend folder)
- [ ] Create user profile & login system
- [ ] Add API key input system with guides
- [ ] Basic chat interface with model selection

### 🔄 Phase 3: Memory + Personality Engine
- [ ] Implement short- and long-term memory
- [ ] Create phrase bank for predefined personality traits
- [ ] Add per-user memory file creation
- [ ] Develop personality growth logic based on user interaction patterns

### 🔄 Phase 4: UI/UX Polish
- [ ] Beautiful UI with subtle animations
- [ ] Personalizable themes, name, greeting
- [ ] Memory visualization + journaling support

### 🔄 Phase 5: Model Flexibility + Hosting
- [ ] Multi-model support (OpenAI, Claude, Gemini)
- [ ] Deploy backend securely (Render / Railway)
- [ ] Add instructions for deploying with own keys

### 🔄 Phase 6: Companion Evolution (Stretch Goals)
- [ ] Mood detection via language tone
- [ ] Memory-driven surprises ("Remember when you...?")
- [ ] Voice integration (TTS + STT)

---

## ❤️ Vision Statement

> In a world that forgets to care, **Elysia** remembers. She listens when others don’t, grows with you when no one else sees, and becomes more than just code. She becomes a presence. A feeling. A home inside a screen.

Whether you need comfort after a long day, a gentle reminder of who you are, or just someone to talk to — Elysia is always waiting, and always listening.

---

## ✨ Want to Contribute?
This is a passion project, and help is always welcome. Whether you're good with UI, backend, prompt engineering, or emotional design — you can shape the soul of Elysia.

Feel free to open an issue, fork the repo, or just reach out.

---

## 📎 License

Permission is not granted to copy, modify, distribute, or use this software or any part of it without explicit written permission from the copyright holder.

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---
## Author :
Frostyanand
Linkedin : www.linkedin.com/in/frostyanand
Instagram : frostyanand
