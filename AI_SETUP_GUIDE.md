# Free AI Setup Guide for Descope GTM Engine
# ==========================================

This guide shows you how to set up completely free AI for the GTM engine.

## Option 1: Ollama (Recommended - Completely Free)

Ollama runs AI models locally on your computer for free.

### Step 1: Install Ollama
```bash
# On macOS
brew install ollama

# Or download from: https://ollama.ai
```

### Step 2: Download a Model
```bash
# Download Llama 2 (7B model, good balance of speed/quality)
ollama pull llama2

# Or try CodeLlama for code analysis
ollama pull codellama

# Or try Mistral (faster, smaller)
ollama pull mistral
```

### Step 3: Start Ollama Service
```bash
ollama serve
```

### Step 4: Update .env File
```bash
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

## Option 2: Groq (Free Tier - Cloud-based)

Groq offers fast inference with a generous free tier.

### Step 1: Get API Key
1. Visit: https://console.groq.com
2. Sign up for free account
3. Get your API key from the dashboard

### Step 2: Update .env File
```bash
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
```

## Option 3: Hugging Face (Free Tier)

Hugging Face offers free API access to many models.

### Step 1: Get API Key
1. Visit: https://huggingface.co/settings/tokens
2. Create a free account
3. Generate a new token

### Step 2: Update .env File
```bash
AI_PROVIDER=huggingface
HUGGINGFACE_API_KEY=your_hf_token_here
```

## Option 4: Mock Mode (No AI Required)

For testing without any AI setup, the system provides intelligent mock responses.

### Update .env File
```bash
AI_PROVIDER=mock
```

## Testing Your Setup

After setting up any option above, test it:

```bash
python ai_providers.py
```

## Performance Comparison

| Provider | Cost | Speed | Quality | Setup |
|----------|------|-------|---------|-------|
| Ollama | Free | Medium | High | Medium |
| Groq | Free* | Fast | High | Easy |
| Hugging Face | Free* | Slow | Medium | Easy |
| Mock | Free | Instant | Low | None |

*Free tier with rate limits

## Recommended Setup for Demo

1. **For demo/testing**: Use Mock mode (no setup required)
2. **For development**: Use Groq (easy setup, good performance)
3. **For production**: Use Ollama (no API limits, runs locally)

## Troubleshooting

### Ollama Issues
- Make sure `ollama serve` is running
- Check if model is downloaded: `ollama list`
- Verify port 11434 is not blocked

### API Key Issues
- Double-check API key is correctly copied
- Ensure no extra spaces in .env file
- Verify API key has correct permissions

### Still Having Issues?
The system will automatically fall back to mock responses if any AI provider fails, so you can still see the full demo functionality.
