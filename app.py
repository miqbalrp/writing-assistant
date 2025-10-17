from agents import Agent, Runner
import asyncio
import streamlit as st
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent

from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
import difflib

# Page configuration
st.set_page_config(
    page_title="AI Writing Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
        /* Main page background and font */
        .stApp {
            font-family: 'Inter', sans-serif;
        }
        
        [data-testid="stSidebar"] {
            padding: 2rem 1rem;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            font-weight: 600;
        }
        
        /* Input fields */
        .stTextInput input, .stTextArea textarea {
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        [data-testid="stTextArea"] textarea {
            padding: 0.5rem;
        }
        
        /* Loading spinner container */
        .loading-container {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin: 1rem 0;
        }
        
        /* Loading spinner animation */
        .loading-spinner {
            width: 20px;
            height: 20px;
            border: 3px solid rgba(0, 0, 0, 0.1);
            border-top: 3px solid #0066FF;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        [data-theme="dark"] .loading-spinner {
            border: 3px solid rgba(255, 255, 255, 0.1);
            border-top: 3px solid #3498db;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Buttons */
        .stButton button {
            font-weight: 500;
            transition: transform 0.15s ease;
            border-radius: 50px !important;
        }
        .stButton button:hover {
            transform: translateY(-1px);
        }
        
        /* Code blocks and output */
        .stCodeBlock {
            border-radius: 8px;
        }
        
        /* Dark mode specific styles */
        [data-theme="dark"] .main-title {
            background: linear-gradient(120deg, #64b5f6, #2196f3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        [data-theme="dark"] .subtitle {
            color: rgba(250, 250, 250, 0.7);
        }
        
        [data-theme="dark"] .stCodeBlock {
            background: rgba(0, 0, 0, 0.2);
        }
        
        /* Light mode specific styles */
        [data-theme="light"] .main-title {
            background: linear-gradient(120deg, #1e88e5, #005cb2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        [data-theme="light"] .subtitle {
            color: rgba(49, 51, 63, 0.7);
        }
        
        /* Comment box styling for both themes */
        .comment-box {
            border-radius: 8px;
            padding: 1em 1.5em;
            margin: 1em 0;
        }
        
        [data-theme="dark"] .comment-box {
            background: rgba(255, 255, 255, 0.05);
            border-left: 4px solid #64b5f6;
        }
        
        [data-theme="light"] .comment-box {
            background: #f8f9fa;
            border-left: 4px solid #1e88e5;
        }
        
        /* Progress bar */
        .stProgress > div > div {
            background: linear-gradient(90deg, #1e88e5, #64b5f6);
        }
    </style>
""", unsafe_allow_html=True)

def create_colored_diff(old_text: str, new_text: str) -> str:
    """Create HTML diff with color coding for word-level changes."""
    def split_into_words(text):
        return text.replace('\n', ' \n ').split()
    
    def join_words(words):
        return ' '.join(words).replace(' \n ', '\n')
    
    old_words = split_into_words(old_text)
    new_words = split_into_words(new_text)
    
    matcher = difflib.SequenceMatcher(None, old_words, new_words)
    html_diff = []
    
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == 'equal':
            html_diff.extend(old_words[i1:i2])
        elif op == 'delete':
            html_diff.append(f'<span style="color: #f44336; text-decoration: line-through;">{" ".join(old_words[i1:i2])}</span>')
        elif op == 'insert':
            html_diff.append(f'<span style="background-color: #c8e6c9; padding: 2px 4px;">{" ".join(new_words[j1:j2])}</span>')
        elif op == 'replace':
            html_diff.append(f'<span style="color: #f44336; text-decoration: line-through;">{" ".join(old_words[i1:i2])}</span>')
            html_diff.append(f'<span style="background-color: #c8e6c9; padding: 2px 4px;">{" ".join(new_words[j1:j2])}</span>')
    
    return join_words(html_diff)

load_dotenv()

# Define output model for agent responses
class EditResponse(BaseModel):
    edited_text: str = Field(
        ..., 
        description="The edited version of the input text, formatted in markdown. Use markdown to highlight changes, corrections, or suggestions."
    )
    comments: str = Field(
        None, 
        description="Clear and educative comments or suggestions regarding the edits made, formatted in markdown. Comments should explain the reasoning behind changes, provide grammar or style tips, and help the user learn from the corrections."
    )

# --- UI Layout ---
st.markdown("""
<style>
/* Main layout */
.main-title {font-size:2.5rem; font-weight:700; margin-bottom:0.2em; background: linear-gradient(120deg, #1e88e5, #005cb2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.subtitle {font-size:1.1rem; color:#666; margin-bottom:2em; opacity:0.8;}
.stTextArea textarea {font-size:1.1rem; border-radius:10px; border-color:#e0e0e0; padding:1em;}
.stTextArea textarea:focus {border-color:#1e88e5; box-shadow:0 0 0 2px rgba(30,136,229,0.2);}

/* Button styling */
.stButton button {
    background: linear-gradient(90deg, #1e88e5, #005cb2);
    color: white;
    border: none;
    padding: 0.5em 2em;
    border-radius: 50px;
    font-weight: 500;
    transition: all 0.3s ease;
}
.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* Sections */
.section-divider {
    margin: 2em 0;
    height: 2px;
    background: linear-gradient(90deg, rgba(30,136,229,0.2), rgba(30,136,229,0), rgba(30,136,229,0.2));
}

/* Output area */
.output-container {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 1.5em;
    border: 1px solid #e0e0e0;
    margin-top: 2em;
}

/* Sidebar */
.sidebar .stSelectbox [data-baseweb="select"] {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">✨ AI Writing Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Polish your writing with grammar, clarity, and tone improvements</div>', unsafe_allow_html=True)


# --- Sidebar Options ---
with st.sidebar:
    # Input text area
    st.markdown("## ⌨️ Input Text")
    
    options = ["Fix grammar", "Improve clarity", "Adjust tone"]
    selections = st.segmented_control("Select options to apply:", options, default=["Fix grammar"], selection_mode="multi")
    
    if "Adjust tone" in selections:
        tone = st.selectbox(
            "",
            ["Formal", "Casual", "Professional", "Friendly", "Technical", "Simple", "Persuasive", "Empathetic", "Humorous", "Inspirational"],
            index=0
        ).lower()
    else:
        tone = "Formal"
    
    # Input text area and run button
    text = st.text_area("", height=500, placeholder="Paste or write your text here with markdown formatting...")
    
    run_button = st.button("✨ Improve Writing", use_container_width=False)

# Define agents with specific instructions
GrammarFixerAgent = Agent(
    name="Grammar Fixer",
    instructions="""
        You are a grammar correction assistant. 
        Correct all grammar, spelling, and punctuation errors without changing the tone, meaning, or writing style. 
        Keep word choice and sentence structure unless necessary for correctness.
        """,
    output_type=EditResponse
)

ClarityImproverAgent = Agent(
    name="Clarity Improver",
    instructions="""
        You are a clarity improvement assistant. 
        Rewrite sentences only when they are confusing, wordy, or ambiguous. 
        Preserve the author’s tone and intent. 
        Avoid adding new ideas.
        """,
    output_type=EditResponse
)

def get_tone_agent(tone):
    return Agent(
        name="Tone Adjuster",
        instructions=f"""
            You are a tone adjustment assistant. 
            Rewrite text to match the requested tone: {tone}. 
            Do not change the meaning. 
            Keep vocabulary level and style consistent with the original writer unless tone requires otherwise.
            """,
        output_type=EditResponse
    )


# Helper function to run an agent and get the final output
async def run_agent(agent, user_input: str):
    result = await Runner.run(agent, user_input)
    return result.final_output

# Function to run agents asynchronously based on user selection
async def process_text(text, selections, tone, progress_placeholder):
    current_text = text
    comments = []
    
    total_steps = len(selections)
    current_step = 0
    
    if "Fix grammar" in selections:
        current_step += 1
        progress_placeholder.markdown(f'<div class="loading-container"><div class="loading-spinner"></div><span> Step {current_step}/{total_steps}: Running Grammar Fixer...</span></div>', unsafe_allow_html=True)
        result = await run_agent(GrammarFixerAgent, current_text)
        current_text = result.edited_text
        if result.comments:
            comments.append(f"#### Grammar\n{result.comments}")
    
    if "Improve clarity" in selections:
        current_step += 1
        progress_placeholder.markdown(f'<div class="loading-container"><div class="loading-spinner"></div><span> Step {current_step}/{total_steps}: Improving Clarity...</span></div>', unsafe_allow_html=True)
        result = await run_agent(ClarityImproverAgent, current_text)
        current_text = result.edited_text
        if result.comments:
            comments.append(f"#### Clarity\n{result.comments}")
    
    if "Adjust tone" in selections:
        current_step += 1
        progress_placeholder.markdown(f'<div class="loading-container"><div class="loading-spinner"></div><span> Step {current_step}/{total_steps}: Adjusting Tone to {tone.title()}...</span></div>', unsafe_allow_html=True)
        ToneAdjusterAgent = get_tone_agent(tone)
        result = await run_agent(ToneAdjusterAgent, current_text)
        current_text = result.edited_text
        if result.comments:
            comments.append(f"#### Tone\n{result.comments}")
    
    progress_placeholder.markdown("""### ✅ **All done!** Here are your results:""", unsafe_allow_html=True)
    return current_text, "\n".join(comments)


# --- Output Section ---
if run_button:
    if text.strip():
        # Create a placeholder for progress updates
        progress_placeholder = st.empty()
        final_text, all_comments = asyncio.run(process_text(text, selections, tone, progress_placeholder))        
        
        # Show improved text
        st.markdown("**✨ Improved Text**")
        st.write(final_text)
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # Show color-coded differences
        st.markdown("**🔍 Detailed Changes**")
        diff_html = create_colored_diff(text, final_text)
        st.markdown(f'''
            <div style="padding: 1.5em; 
                        border: 1px solid #e0e0e0; 
                        border-radius: 10px; 
                        margin: 1em 0 2em 0;
                        background: white;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                {diff_html}
            </div>
        ''', unsafe_allow_html=True)
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # Show comments if available
        st.markdown("**💡 Comments / Suggestions:**")
        if all_comments:
            with st.expander("Show"):
                st.markdown(all_comments, unsafe_allow_html=True)
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # Show code block of edited text for easy copying
        st.markdown("**📋 Copy Edited Text:**")
        st.code(final_text, language="markdown", line_numbers=False, wrap_lines=True)
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    else:
        st.warning("Please enter some text.")