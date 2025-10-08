# 🎯 Kilo Code Custom Prompt Setup Guide

## Quick Answer: 3 Ways to Set Custom Prompt

### ✅ Method 1: VS Code Settings UI (EASIEST - RECOMMENDED)

1. **Open Settings:**
   ```
   Press: Ctrl+, (Linux/Windows) or Cmd+, (Mac)
   ```

2. **Search for Kilo Code:**
   ```
   Type in search: "kilo code"
   ```

3. **Find Custom Instructions setting:**
   - Look for: `Kilo Code: Custom Instructions`
   - Or: `Kilo Code › Custom Instructions`

4. **Copy & Paste the Prompt:**
   - Open: `docs/KILO_CODE_MASTER_PROMPT.md`
   - Select ALL content (Ctrl+A)
   - Copy (Ctrl+C)
   - Paste into the Custom Instructions text box

5. **Save:**
   - Settings auto-save in VS Code
   - Reload window if needed: `Ctrl+Shift+P` → `Developer: Reload Window`

---

### ✅ Method 2: User Settings JSON

1. **Open User Settings JSON:**
   ```
   Press: Ctrl+Shift+P (or Cmd+Shift+P)
   Type: "Preferences: Open User Settings (JSON)"
   ```

2. **Add Kilo Code configuration:**
   ```json
   {
     "kiloCode.customInstructions": "PASTE_ENTIRE_PROMPT_HERE",
     "kiloCode.temperature": 0.1,
     "kiloCode.maxTokens": 8000
   }
   ```

3. **Format the prompt as JSON string:**
   - Escape all double quotes: `"` → `\"`
   - Escape backslashes: `\` → `\\`
   - Convert newlines to `\n`
   - OR use a JSON string formatter tool

---

### ✅ Method 3: Workspace Settings (Project-Specific)

**Already set up for you in:** `.vscode/settings.json`

Current configuration:
```json
{
  "kiloCode.customInstructions": "See docs/KILO_CODE_MASTER_PROMPT.md",
  "kiloCode.systemPrompt": "",
  "kiloCode.temperature": 0.1,
  "kiloCode.maxTokens": 8000
}
```

**To activate:**
1. Open: `.vscode/settings.json`
2. Replace the `"kiloCode.customInstructions"` value with the full prompt
3. Or use the Settings UI to edit (easier)

---

## 🔧 Settings Explained

### Available Kilo Code Settings:

| Setting | Purpose | Recommended Value |
|---------|---------|-------------------|
| `kiloCode.customInstructions` | Your custom prompt/context | Full master prompt |
| `kiloCode.systemPrompt` | System-level instructions | Empty (use custom instead) |
| `kiloCode.temperature` | Model creativity (0-2) | `0.1` (precise, reliable) |
| `kiloCode.maxTokens` | Max response length | `8000` (comprehensive) |
| `kiloCode.model` | AI model to use | `gpt-4` or `claude-3-5-sonnet` |

---

## 📋 Copy to Clipboard (Linux)

Run the setup script:
```bash
./scripts/setup-kilo-prompt.sh
```

Or manually:
```bash
# Install xclip if needed
sudo apt install xclip

# Copy prompt to clipboard
cat docs/KILO_CODE_MASTER_PROMPT.md | xclip -selection clipboard

# Then paste in Kilo Code settings (Ctrl+V)
```

---

## 🎨 What the Master Prompt Includes

The prompt at `docs/KILO_CODE_MASTER_PROMPT.md` contains:

✅ **Complete Tech Stack** (Python FastAPI, React TypeScript, 80+ dependencies)  
✅ **Architecture Patterns** (async-first, layered backend, atomic design frontend)  
✅ **Modern UI/UX System** (glassmorphism, animations, design tokens)  
✅ **Performance Targets** (<100ms backend, <120ms frontend)  
✅ **Security Standards** (OWASP 100% compliance, code examples)  
✅ **Real Implementation Examples** (components, APIs, hooks)  
✅ **Code Quality Rules** (type safety, error handling, testing)  
✅ **Complete File Organization** (project structure for 10 directories)

---

## ✨ After Setup

Once configured, Kilo Code will:

1. **Understand your entire architecture** automatically
2. **Generate production-ready code** (no placeholders or TODOs)
3. **Follow your exact patterns** (async, Pydantic, Zustand, etc.)
4. **Create beautiful UI** (glassmorphic designs, smooth animations)
5. **Optimize for performance** (2-4x speedups with orjson, uvloop)
6. **Implement security** (OWASP compliant, input validation)
7. **Match your code style** (formatting, naming conventions)

---

## 🐛 Troubleshooting

### "I don't see Kilo Code settings"
- **Solution:** Make sure Kilo Code extension is installed
- Go to: Extensions (`Ctrl+Shift+X`) → Search "Kilo Code" → Install

### "Settings not taking effect"
- **Solution:** Reload VS Code window
- Press: `Ctrl+Shift+P` → Type "Reload Window" → Enter

### "Prompt is too long"
- **Solution:** Some AI models have context limits
- Try using Claude 3.5 Sonnet (200K context) or GPT-4 Turbo (128K)
- Set model in Kilo Code settings: `kiloCode.model`

### "JSON formatting errors"
- **Solution:** Use Settings UI instead of manual JSON
- Or use an online JSON escape tool for the prompt

---

## 📚 Additional Resources

- **Master Prompt:** `docs/KILO_CODE_MASTER_PROMPT.md` (474 lines)
- **Project README:** `README.md` (architecture overview)
- **Roadmap:** `docs/PROJECT_ROADMAP.md` (features, phases)
- **Tech Stack:** `pyproject.toml` (backend) + `web/package.json` (frontend)

---

## 💡 Pro Tips

1. **Use workspace settings** for project-specific prompts
2. **Use user settings** for global coding standards
3. **Update prompt** as your architecture evolves
4. **Include examples** in the prompt for better code generation
5. **Set temperature low** (0.1) for consistent, reliable code
6. **Test the prompt** by asking Kilo Code to generate a component

---

**Ready to generate world-class code!** 🚀

Run: `./scripts/setup-kilo-prompt.sh` to get started!
