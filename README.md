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

## ⚙️ What You Need to Change

### 🔴 CRITICAL — Version Headers (Update with Every OB Patch!)

These three values **change with every Free Fire update**. If they're outdated, the API will reject your requests. Set them via environment variables or update the defaults in `bot.py`:

| Env Variable | Header | Current Default | How to Find Latest |
|---|---|---|---|
| `FF_UNITY_VERSION` | `X-Unity-Version` | `2018.4.11f1` | Sniff game traffic with HTTP Toolkit / Charles Proxy |
| `FF_GA_VERSION` | `X-GA` | `v1 1` | Same — capture from any FF API request |
| `FF_RELEASE_VERSION` | `ReleaseVersion` | `OB50` | Check the current OB version in-game or patch notes |

> **How to get the latest values:** Run Free Fire on an emulator (e.g., BlueStacks) with a packet sniffer (HTTP Toolkit, Charles Proxy, or mitmproxy). Capture any API request and copy the header values.

### 🟡 Other Configurable Values

| What | Env Variable | Description |
|---|---|---|
| **Discord Bot Token** | `DISCORD_BOT_TOKEN` | Your bot token from the Discord Developer Portal |
| **JWT Token** | `FF_JWT_TOKEN` | Session token from a valid FF login (expires periodically) |
| **API URL** | *(edit in code)* | Change region by modifying the subdomain (e.g., `client.ind.` for India) |
| **AES Key/IV** | *(do NOT change)* | Garena's encryption constants — only change if Garena updates them |
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
# Update these to match the latest Free Fire version:
export FF_UNITY_VERSION="2018.4.11f1"
export FF_GA_VERSION="v1 1"
export FF_RELEASE_VERSION="OB50"
```

**Windows (PowerShell):**
```powershell
$env:DISCORD_BOT_TOKEN = "your_discord_bot_token_here"
$env:FF_JWT_TOKEN = "your_freefire_jwt_token_here"
# Update these to match the latest Free Fire version:
$env:FF_UNITY_VERSION = "2018.4.11f1"
$env:FF_GA_VERSION = "v1 1"
$env:FF_RELEASE_VERSION = "OB50"
```

**Windows (CMD):**
```cmd
set DISCORD_BOT_TOKEN=your_discord_bot_token_here
set FF_JWT_TOKEN=your_freefire_jwt_token_here
REM Update these to match the latest Free Fire version:
set FF_UNITY_VERSION=2018.4.11f1
set FF_GA_VERSION=v1 1
set FF_RELEASE_VERSION=OB50
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
