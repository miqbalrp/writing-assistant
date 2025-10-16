# AI Writing Assistant 📝

A streamlined writing enhancement tool that helps improve your text with grammar corrections, clarity improvements, and tone adjustments.

## Features ✨

- **Grammar Correction**: Fixes spelling, punctuation, and grammatical errors
- **Clarity Enhancement**: Makes text more concise and easier to understand
- **Tone Adjustment**: Adapts writing style to match desired tone (formal, casual, professional, etc.)
- **Real-time Preview**: See changes with color-coded differences
- **Educational Feedback**: Learn from detailed suggestions and improvements

## Getting Started 🚀

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (for AI functionality)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/writing-assistant.git
cd writing-assistant
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

### Running the App

Launch the application using Streamlit:
```bash
streamlit run app.py
```

## Usage 💡

1. Select the improvements you want to apply:
   - Grammar fixing
   - Clarity improvement
   - Tone adjustment

2. If tone adjustment is selected, choose your desired tone:
   - Formal
   - Casual
   - Professional
   - Friendly
   - Technical
   - Simple

3. Enter or paste your text
4. Click "✨ Improve Writing"
5. Review the improvements:
   - Original vs. improved text
   - Detailed changes with color coding
   - Learning points and suggestions

## Project Structure 📁

```
writing-assistant/
├── app.py           # Main application file
├── agents.py        # AI agents implementation
├── requirements.txt # Project dependencies
└── .env            # Environment variables (not in repo)
```

## Contributing 🤝

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](link-to-issues).

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
