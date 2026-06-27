# 🛡️ FreeFire Bad Word Checker Bot

A Discord bot that checks whether a nickname/word is **banned or allowed** in Garena Free Fire by querying the official Garena dirty-word filter API.

---

## 📖 How It Works

### Bad Word Check Flow (Garena Server)

```
User types /check word:test
        │
        ▼
┌─────────────────────────┐
│  1. Encode the word to  │
│     UTF-8 (max 12 bytes)│
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  2. Build a 16-byte     │
│     payload with header │
│     bytes (0x0A 0x0A)   │
│     + word + padding    │
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  3. AES-128-CBC encrypt │
│     using Garena's key  │
│     and IV              │
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  4. POST encrypted data │
│     to Garena endpoint: │
│     /CheckDirtyWords    │
│     with JWT auth token │
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  5. Parse response:     │
│  • 200 + empty body     │
│    → ✅ Word is CLEAN   │
│  • 400 + DIRTY_WORD     │
│    → 🚫 Word is BANNED  │
└─────────────────────────┘
```

### Garena API Details

| Parameter      | Value                                            |
|----------------|--------------------------------------------------|
| **Endpoint**   | `https://client.ind.freefiremobile.com/CheckDirtyWords` |
| **Method**     | `POST`                                           |
| **Auth**       | `Bearer <JWT Token>`                             |
| **Encryption** | AES-128-CBC                                      |
| **Response**   | Empty body = clean, `BR_CONTENT_DIRTY_WORD` = banned |

> The JWT token is a session token from a valid Free Fire account login. It **expires periodically** and must be refreshed.

---

## ⚙️ What You Need to Change in the Script

### 🔴 CRITICAL — Before Pushing to GitHub

**Remove all hardcoded secrets from `bot.py`!** The following must be loaded from environment variables only:

| What to Change | Line | Current (INSECURE) | What to Do |
|---|---|---|---|
| **Discord Bot Token** | Line 9 | Hardcoded token string | Use `os.getenv('DISCORD_BOT_TOKEN')` only |
| **JWT Token** | Line 11 | Hardcoded JWT string | Use `os.getenv('FF_JWT_TOKEN')` only |

### 🟡 Optional Customizations

| What | Line | Description |
|---|---|---|
| **API URL** | Line 14 | Change region by modifying the subdomain (e.g., `client.ind.` for India) |
| **AES Key/IV** | Lines 15–16 | These are Garena's encryption constants — do NOT change unless Garena updates them |
| **Release Version** | Line 39 | Update `OB50` to match the current Free Fire OB version |
| **Max Word Length** | Line 26–27 | Currently 12 bytes — Free Fire's nickname limit |
| **Bulk Check Limit** | Line 105 | Currently max 10 words — adjust as needed |

### 🟢 How to Refresh the JWT Token

The JWT token expires. To get a new one:
1. Log into Free Fire on an emulator with a packet sniffer (e.g., HTTP Toolkit, Charles Proxy)
2. Capture the `Authorization: Bearer <token>` header from any API request
3. Set it as the `FF_JWT_TOKEN` environment variable

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.9+
- A Discord Bot Token ([Discord Developer Portal](https://discord.com/developers/applications))
- A valid Free Fire JWT Token

### 1. Clone the Repository

```bash
git clone https://github.com/khawarahemad/bad-word-checker-freefire.git
cd bad-word-checker-freefire
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

**Linux / macOS:**
```bash
export DISCORD_BOT_TOKEN="your_discord_bot_token_here"
export FF_JWT_TOKEN="your_freefire_jwt_token_here"
```

**Windows (PowerShell):**
```powershell
$env:DISCORD_BOT_TOKEN = "your_discord_bot_token_here"
$env:FF_JWT_TOKEN = "your_freefire_jwt_token_here"
```

**Windows (CMD):**
```cmd
set DISCORD_BOT_TOKEN=your_discord_bot_token_here
set FF_JWT_TOKEN=your_freefire_jwt_token_here
```

### 4. Run the Bot

```bash
python bot.py
```

---

## 🤖 Bot Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/check` | Check a single word against Garena's filter | `/check word:HelloFF` |
| `/bulk` | Check up to 10 words at once | `/bulk words:Test Hello World` |
| `/help_ff` | Show bot help and usage info | `/help_ff` |

### Response Meanings

| Icon | Status | Meaning |
|------|--------|---------|
| ✅ | **Clean** | Word is allowed in Free Fire nicknames |
| 🚫 | **Bad Word** | Word is blocked by Garena's filter |
| ⚠️ | **Unknown** | Unexpected API response (token may be expired) |

---

## 📁 Project Structure

```
bad-word-checker-freefire/
├── bot.py              # Main bot script with Garena API integration
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore rules
├── .env.example        # Example environment variables template
└── README.md           # This file
```

---

## 🔒 Security Notes

- **NEVER** commit your Discord bot token or JWT token to Git
- Use environment variables or a `.env` file (excluded via `.gitignore`)
- The `.gitignore` file in this repo already excludes `.env` files
- Rotate your Discord bot token immediately if it's been exposed

---

## 📄 License

This project is for **educational purposes only**. Use responsibly and in accordance with Garena's Terms of Service.

---

## 👤 Author

**Khawar Ahemad** — [@khawarahemad](https://github.com/khawarahemad)
