# chng
**chng** is a simple AI-powered changelog generator for your terminal. Feed it a diff file, get a professional changelog — powered by OpenAI or your local LLM.
> Stop writing changelogs. Start shipping code.
---
## ✨ Features
- Generate changelogs from any diff file  
- Works with OpenAI API or local models (Ollama, LocalAI)  
- Clean markdown output following conventional format  
- Simple two-command interface  
- Saves output as `changelog-<filename>.md`  
---
## 📦 Installation

[get yanked](https://github.com/codinganovel/yanked)

---
### Available Commands
| Command         | Description                          |
|----------------|--------------------------------------|
| `chng --setup`  | Configure API settings (first run)   |
| `chng <file>`   | Generate changelog from diff file    |

Settings are saved to `~/.apikey` and remembered between sessions.
---
## 🚀 Quick Start

### Using OpenAI
```bash
$ python chng.py --setup
API URL: https://api.openai.com/v1
Port: [enter]
API Key: sk-...
Model: gpt-4

$ python chng.py feature.diff
✓ Saved to changelog-feature.md
```

### Using Local Model
```bash
$ python chng.py --setup
API URL: http://localhost:11434/v1
Port: [enter]
API Key: [enter]
Model: llama2

$ python chng.py changes.diff
✓ Saved to changelog-changes.md
```
---
## 🤖 Supported Models

### Cloud
- OpenAI: `gpt-3.5-turbo`, `gpt-4`
- Any OpenAI-compatible API

### Local  
- Ollama: `llama2`, `mistral`, `mixtral`
- LocalAI, LM Studio, Text Generation WebUI
---
## 📋 Example

**Input** (`feature.diff`):
```diff
+    def enable_2fa(self, user_id):
+        """Enable two-factor authentication"""
-    def login(self, username, password):
+    def login(self, username, password, otp=None):
```

**Output** (`changelog-feature.md`):
```markdown
# Changelog

## Added
- Two-factor authentication (2FA) support

## Changed  
- Login method now accepts optional OTP parameter
```
---
## 🔒 Privacy
- API keys stored locally with 0600 permissions
- Use local models to keep code 100% private
- No telemetry or usage tracking
---
## 📁 License
MIT
---
## ✍️ Created with 🦀 by developers  
Who have better things to do than write changelogs.