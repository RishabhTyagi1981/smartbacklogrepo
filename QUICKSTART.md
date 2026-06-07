# Smart Backlog Assistant - Quick Start Guide

## Prerequisites

- **Python 3.8+** installed on your system
- **OpenAI API Key** (free credits available at https://platform.openai.com)
- **Git** (for cloning the repository)

---

## Step-by-Step Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/RishabhTyagi1981/smartbacklogrepo.git
cd smartbacklogrepo
```

### Step 2: Create a Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `openai>=1.3.0` - OpenAI Python SDK
- `python-dotenv>=1.0.0` - Environment variable management

### Step 4: Get Your OpenAI API Key

1. Go to https://platform.openai.com/account/api-keys
2. Click **"Create new secret key"**
3. Copy the generated key (you won't be able to see it again)
4. Save it safely

### Step 5: Configure Environment Variables

1. Copy the template file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your API key:
   ```bash
   # macOS/Linux
   nano .env
   
   # Windows (Notepad)
   notepad .env
   ```

3. Update the file:
   ```
   OPENAI_API_KEY=sk-your_actual_key_here
   OPENAI_MODEL=gpt-4o
   LOG_LEVEL=INFO
   ```

4. Save and close

---

## Running the Program

### Method 1: Quick Test (Recommended First Time)

```bash
python main.py --input examples/sample_meeting_notes.txt
```

### Method 2: Process Your Own File

1. Create a text file with meeting notes or requirements (e.g., `notes.txt`)

2. Run the program:
   ```bash
   python main.py --input notes.txt
   ```

3. View the output in your terminal

### Method 3: Save Output to File

**Save as JSON:**
```bash
python main.py --input notes.txt --output backlog.json --format json
```

**Save as detailed text:**
```bash
python main.py --input notes.txt --output backlog.txt --format detailed
```

### Method 4: Use Different OpenAI Model

```bash
# Using GPT-4 (good quality, lower cost than GPT-4o)
python main.py --input notes.txt --model gpt-4

# Using GPT-3.5-turbo (fastest and cheapest)
python main.py --input notes.txt --model gpt-3.5-turbo
```

### Method 5: Enable Debug Logging

```bash
python main.py --input notes.txt --log-level DEBUG
```

---

## Example Usage in Python Code

```python
from backlog_assistant import BacklogAssistant

# Initialize the assistant
assistant = BacklogAssistant()

# Your requirements or meeting notes
meeting_notes = """
We discussed adding dark mode to our app.
Users want a toggle in settings.
We also need to improve performance for slow networks.
"""

# Process the requirements
result = assistant.process_requirements(meeting_notes)

# View results
print(f"Summary: {result.summary}")
print(f"\nGenerated {len(result.user_stories)} user stories:")
for story in result.user_stories:
    print(f"  - {story.title} (Priority: {story.priority.value})")

# View key requirements
print(f"\nKey Requirements:")
for req in result.key_requirements:
    print(f"  - {req}")
```

---

## Complete Command Examples

### Example 1: Simple Meeting Notes Processing

```bash
python main.py --input meeting_notes.txt
```

**Input file `meeting_notes.txt`:**
```
We discussed implementing user authentication.
We need email verification.
Two-factor authentication should be optional initially.
We should support social login (Google, GitHub).
```

**Output:** Displays formatted user stories in terminal

### Example 2: Process and Save as JSON

```bash
python main.py --input requirements.md --output backlog.json --format json
```

Generated `backlog.json` will contain:
```json
{
  "summary": "Implement user authentication system...",
  "user_stories": [
    {
      "title": "Add email-based user registration",
      "description": "As a user...",
      "acceptance_criteria": [...],
      "priority": "High",
      "category": "Feature"
    }
  ],
  "key_requirements": [...],
  "processing_metadata": {...}
}
```

### Example 3: Complex Requirements with Detailed Output

```bash
python main.py --input complex_requirements.txt --output results.txt --format detailed --log-level INFO
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'openai'"

**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "OpenAI API key not provided"

**Solution:** Check your `.env` file has the correct key:
```bash
cat .env  # View current configuration
```

### Issue: "Input file not found"

**Solution:** Verify file path is correct:
```bash
ls -la notes.txt  # Check file exists
python main.py --input ./notes.txt  # Use full path
```

### Issue: "Rate limit error" from OpenAI

**Solution:** The program automatically retries with exponential backoff. If you're hitting rate limits:
- Wait a few minutes before retrying
- Consider using `gpt-3.5-turbo` instead of `gpt-4o`
- Use the free tier initially and upgrade if needed

### Issue: "Invalid JSON response from OpenAI"

**Solution:** The program will retry up to 3 times. If this persists:
1. Check your `.env` file is correct
2. Try with a simpler input
3. Use `--log-level DEBUG` to see detailed error messages

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | - | Your OpenAI API key |
| `OPENAI_MODEL` | ❌ No | gpt-4o | Model to use (gpt-4o, gpt-4, gpt-3.5-turbo) |
| `LOG_LEVEL` | ❌ No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |

---

## Input Format Requirements

Your input file should contain:
- Meeting notes or requirements
- At least 20 characters of meaningful text
- Maximum 10,000 characters
- Plain text or Markdown format

**Valid input examples:**
```
✅ "We need to add dark mode and improve performance"
❌ "fix bug" (too short)
```

---

## Output Files

### JSON Format (`--format json`)
Perfect for integration with other tools. Contains:
- Summary of requirements
- Array of user stories with full details
- Key requirements list
- Processing metadata (model used, time taken, etc.)

### Detailed Text Format (`--format detailed`)
Human-readable output with:
- Summary section
- Key requirements section
- Formatted user stories with acceptance criteria
- Easy to copy-paste into documentation

---

## Tips for Best Results

1. **Be Specific**: More detailed meeting notes produce better results
   ```
   ✅ Good: "Users requested dark mode to reduce eye strain at night"
   ❌ Poor: "dark mode"
   ```

2. **Include Context**: Mention who the users are
   ```
   ✅ "Mobile users need offline functionality"
   ❌ "Need offline"
   ```

3. **Mention Constraints**: Include timing or technical constraints
   ```
   ✅ "Feature needed by Q2, must support iOS 14+"
   ❌ "Feature needed soon"
   ```

4. **Test with Different Models**:
   - `gpt-4o`: Best quality, slightly more expensive (~$0.015/1K tokens)
   - `gpt-4`: Good quality, balanced cost (~$0.006/1K tokens)
   - `gpt-3.5-turbo`: Fast and cheap (~$0.0015/1K tokens)

---

## Cost Estimation

- **Typical processing cost**: $0.01 - $0.03 per backlog item
- **100 items**: ~$1-3
- **1000 items**: ~$10-30
- **Free tier**: Usually $5-18 in credits (check current offer)

---

## Getting Help

1. Check `.env` configuration
2. Verify API key is valid
3. Try with simpler input first
4. Use `--log-level DEBUG` for detailed error messages
5. Review the README.md for architecture details

---

**Ready to start?** Run this command:
```bash
python main.py --input examples/sample_meeting_notes.txt
```

