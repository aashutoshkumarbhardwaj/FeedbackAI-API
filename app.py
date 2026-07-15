import streamlit as st
import requests
import json
import random
import pandas as pd
from io import BytesIO

# --- Configuration ---
API_BASE_URL = "http://localhost:8000"

# --- Page Config ---
st.set_page_config(
    page_title="FeedbackAI",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================================
# DESIGN SYSTEM — Apple-style dark product UI
# Tokens:
#   bg:        #0A0A0B  (page)
#   surface:   #151517  (card)
#   surface-2: #1C1C1F  (elevated / hover)
#   border:    rgba(255,255,255,0.08)
#   text:      #F5F5F7  (primary)
#   text-2:    #86868B  (secondary)
#   accent:    #0071E3  (Apple blue)
#   good:      #30D158
#   warn:      #FF9F0A
#   bad:       #FF453A
# Type: SF Pro system stack, tight tracking, weight scale 400/510/590/680
# =========================================================================

APPLE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root{
    --bg:#0A0A0B;
    --surface:#151517;
    --surface-2:#1C1C1F;
    --border:rgba(255,255,255,0.08);
    --border-strong:rgba(255,255,255,0.14);
    --text:#F5F5F7;
    --text-2:#86868B;
    --accent:#0071E3;
    --accent-2:#42A5FF;
    --good:#30D158;
    --warn:#FF9F0A;
    --bad:#FF453A;
    --font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", "Helvetica Neue", Arial, sans-serif;
}

html, body, [data-testid="stAppViewContainer"]{
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
}

/* kill default streamlit chrome */
#MainMenu, footer, header[data-testid="stHeader"]{
    visibility: hidden;
    height: 0;
}
[data-testid="stAppViewContainer"] > .main{
    padding-top: 0 !important;
}
.block-container{
    padding-top: 2.5rem !important;
    padding-bottom: 4rem !important;
    max-width: 1180px !important;
}

/* ---------- typography ---------- */
h1, h2, h3, h4, h5, h6{
    font-family: var(--font) !important;
    color: var(--text) !important;
    letter-spacing: -0.02em !important;
    font-weight: 680 !important;
}
p, span, label, .stMarkdown, div{
    font-family: var(--font);
}
.stCaption, [data-testid="stCaptionContainer"]{
    color: var(--text-2) !important;
}

/* ---------- hero ---------- */
.hero-wrap{
    position: relative;
    padding: 64px 8px 40px 8px;
    margin-bottom: 8px;
    overflow: hidden;
    border-radius: 28px;
}
.hero-mesh{
    position: absolute;
    inset: -40%;
    background:
        radial-gradient(38% 45% at 22% 30%, rgba(0,113,227,0.28), transparent 70%),
        radial-gradient(32% 40% at 78% 20%, rgba(120,80,255,0.20), transparent 70%),
        radial-gradient(45% 45% at 60% 85%, rgba(0,113,227,0.14), transparent 70%);
    filter: blur(60px);
    animation: drift 22s ease-in-out infinite alternate;
    z-index: 0;
}
@keyframes drift{
    0%   { transform: translate(0,0) scale(1); }
    100% { transform: translate(-3%, 2%) scale(1.05); }
}
.hero-content{
    position: relative;
    z-index: 1;
    text-align: center;
}
.hero-eyebrow{
    display:inline-block;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.02em;
    color: var(--accent-2);
    background: rgba(0,113,227,0.12);
    border: 1px solid rgba(0,113,227,0.25);
    padding: 5px 14px;
    border-radius: 999px;
    margin-bottom: 22px;
}
.hero-title{
    font-size: 64px;
    line-height: 1.04;
    font-weight: 680;
    letter-spacing: -0.03em;
    margin: 0 0 18px 0;
    background: linear-gradient(180deg, #FFFFFF 0%, #C7C7CC 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub{
    font-size: 21px;
    font-weight: 400;
    color: var(--text-2);
    max-width: 560px;
    margin: 0 auto;
    letter-spacing: -0.01em;
}

/* ---------- tabs → segmented pill control ---------- */
[data-testid="stTabs"] [data-baseweb="tab-list"]{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 5px;
    gap: 4px;
    justify-content: center;
    flex-wrap: wrap;
}
[data-testid="stTabs"] button[data-baseweb="tab"]{
    height: 40px;
    border-radius: 10px !important;
    color: var(--text-2) !important;
    font-weight: 510;
    font-size: 14.5px;
    letter-spacing: -0.01em;
    background: transparent !important;
    border: none !important;
    transition: all 0.15s ease;
}
[data-testid="stTabs"] button[data-baseweb="tab"]:hover{
    color: var(--text) !important;
    background: rgba(255,255,255,0.04) !important;
}
[data-testid="stTabs"] button[aria-selected="true"]{
    background: var(--surface-2) !important;
    color: var(--text) !important;
    box-shadow: 0 1px 0 var(--border-strong) inset, 0 4px 14px rgba(0,0,0,0.35);
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{
    display:none;
}
[data-testid="stTabs"] [data-baseweb="tab-border"]{
    display:none;
}

/* ---------- cards / bordered containers ---------- */
[data-testid="stVerticalBlockBorderWrapper"]{
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 18px !important;
    transition: border-color 0.2s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover{
    border-color: var(--border-strong) !important;
}

/* ---------- buttons ---------- */
.stButton > button{
    background: var(--surface-2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 12px !important;
    font-weight: 510 !important;
    letter-spacing: -0.01em;
    padding: 0.55rem 1.1rem !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
}
.stButton > button:hover{
    background: #26262A !important;
    border-color: rgba(255,255,255,0.22) !important;
    transform: translateY(-1px);
}
.stButton > button[kind="primary"]{
    background: var(--accent) !important;
    border: 1px solid var(--accent) !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover{
    background: var(--accent-2) !important;
    border-color: var(--accent-2) !important;
}

/* ---------- inputs ---------- */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input,
[data-testid="stFileUploader"] section{
    background: var(--surface-2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,113,227,0.18) !important;
}
[data-testid="stFileUploader"] section{
    border-style: dashed !important;
}

/* radio → pill segmented */
[data-testid="stRadio"] > div{
    gap: 6px;
}
[data-testid="stRadio"] label{
    background: var(--surface-2);
    border: 1px solid var(--border);
    padding: 6px 14px;
    border-radius: 999px;
    margin-right: 2px;
}

/* selectbox */
[data-baseweb="select"] > div{
    background: var(--surface-2) !important;
    border-color: var(--border) !important;
    border-radius: 12px !important;
}

/* ---------- metrics ---------- */
[data-testid="stMetric"]{
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 16px 18px;
}
[data-testid="stMetricLabel"]{
    color: var(--text-2) !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}
[data-testid="stMetricValue"]{
    color: var(--text) !important;
    font-weight: 650 !important;
    letter-spacing: -0.02em;
}
[data-testid="stMetricDelta"]{
    font-weight: 550 !important;
}

/* ---------- progress ---------- */
[data-testid="stProgress"] > div > div{
    background: var(--surface-2) !important;
    border-radius: 999px !important;
}
[data-testid="stProgress"] > div > div > div{
    background: linear-gradient(90deg, var(--accent), var(--accent-2)) !important;
    border-radius: 999px !important;
}

/* ---------- expander ---------- */
[data-testid="stExpander"]{
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    overflow: hidden;
}
[data-testid="stExpander"] summary{
    color: var(--text) !important;
    font-weight: 500;
}

/* ---------- code blocks ---------- */
[data-testid="stCodeBlock"] pre{
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
}

/* ---------- dataframe / table ---------- */
[data-testid="stDataFrame"], [data-testid="stTable"]{
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    overflow: hidden;
}

/* ---------- alerts (info/success/warning/error) ---------- */
[data-testid="stAlert"]{
    border-radius: 14px !important;
    border: 1px solid var(--border) !important;
    background: var(--surface-2) !important;
}

/* ---------- section headers ---------- */
.section-label{
    font-size: 12px;
    font-weight: 650;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--accent-2);
    margin-bottom: 6px;
}
.section-title{
    font-size: 26px;
    font-weight: 620;
    letter-spacing: -0.02em;
    color: var(--text);
    margin-bottom: 4px;
}
.section-sub{
    color: var(--text-2);
    font-size: 15px;
    margin-bottom: 24px;
}

hr{
    border-color: var(--border) !important;
}
</style>
"""

st.markdown(APPLE_CSS, unsafe_allow_html=True)

# --- Hero ---
st.markdown(
    """
    <div class="hero-wrap">
        <div class="hero-mesh"></div>
        <div class="hero-content">
            <span class="hero-eyebrow">FeedbackAI API</span>
            <div class="hero-title">Understand every<br/>customer, instantly.</div>
            <div class="hero-sub">Sentiment, urgency, and suggested replies from a single API call.</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


def section_header(label, title, sub):
    st.markdown(
        f"""
        <div class="section-label">{label}</div>
        <div class="section-title">{title}</div>
        <div class="section-sub">{sub}</div>
        """,
        unsafe_allow_html=True,
    )


# --- Tabbed Interface ---
tab_playground, tab_dashboard, tab_batch, tab_history, tab_automation, tab_docs, tab_pricing = st.tabs(
    ["Playground", "Dashboard", "Batch Analysis", "History", "Automation", "Docs", "Pricing"]
)

# --- Initialize Session State for History ---
if "history" not in st.session_state:
    st.session_state.history = []


def generate_code_snippets(api_url, text, api_key="YOUR_API_KEY"):
    """Generates Python, cURL, and JS code snippets."""
    escaped_text = json.dumps(text)

    python_code = f"""import requests

response = requests.post(
    "{api_url}",
    headers={{"Authorization": f"Bearer {{api_key}}"}},
    json={{"text": {escaped_text}}}
)

print(response.json())"""

    curl_code = f"""curl -X POST "{api_url}" \\
-H "Content-Type: application/json" \\
-H "Authorization: Bearer {api_key}" \\
-d '{{
    "text": {escaped_text}
}}'"""

    js_code = f"""fetch('{api_url}', {{
    method: 'POST',
    headers: {{
        'Content-Type': 'application/json'
        'Authorization': `Bearer ${{api_key}}`
    }},
    body: JSON.stringify({{
        text: {escaped_text}
    }})
}})
.then(response => response.json())
.then(data => console.log(data));"""

    return python_code, curl_code, js_code


with tab_playground:
    section_header("Playground", "Try it live", "Enter any customer feedback and see the full analysis.")
    col1, col2 = st.columns([2, 3], gap="large")

    with col1:
        with st.container(border=True):
            st.markdown("**Input**")
            input_text = st.text_area(
                "Text Input",
                height=200,
                placeholder="e.g., The delivery was late but the support team was very helpful.",
                label_visibility="collapsed",
            )

            st.markdown("**Response tone**")
            tone = st.radio(
                "Choose a response tone:",
                ["Professional", "Friendly", "Luxury", "Technical", "Startup", "Formal"],
                horizontal=True,
                label_visibility="collapsed"
            )

            analyze_button = st.button(
                "Run Analysis",
                type="primary",
                use_container_width=True,
                key="playground_button",
            )

            st.caption("Your input is sent to the API like this:")
            st.code(f'{{\n  "text": "{input_text[:50]}..."\n}}', language="json")

    with col2:
        with st.container(border=True):
            st.markdown("**Output**")
            st.caption("The API returns a structured JSON response.")

            if analyze_button:
                if not input_text:
                    st.warning("Please enter some text to analyze.")
                else:
                    with st.spinner("Calling FeedbackAI API..."):
                        try:
                            # --- Call the /analyze endpoint for the main data ---
                            analyze_res = requests.post(f"{API_BASE_URL}/analyze", json={"text": input_text})
                            analyze_res.raise_for_status()
                            main_data = analyze_res.json()

                            # --- Call the /reply endpoint ---
                            reply_res = requests.post(
                                f"{API_BASE_URL}/reply",
                                json={"text": input_text, "tone": tone},
                            )

                            # --- Call the /actions endpoint ---
                            actions_res = requests.post(
                                f"{API_BASE_URL}/actions",
                                json={"text": input_text},
                            )

                            # --- Construct the final JSON for display ---
                            output_json = {
                                "sentiment": main_data.get("sentiment"),
                                "confidence": main_data.get("confidence"),
                                "emotions": main_data.get("emotions"),
                                "urgency": main_data.get("urgency"),
                                "category": main_data.get("category"),
                                "summary": main_data.get("summary"),
                                "suggested_reply": reply_res.json() if reply_res.ok else "Could not generate reply.",
                            }

                            # Add to history
                            st.session_state.history.insert(0, {"input": input_text, "output": output_json})
                            if len(st.session_state.history) > 10:  # Keep history to 10 items
                                st.session_state.history.pop()

                            # --- Display Output and Code Snippets in Tabs ---
                            output_tabs = st.tabs(["AI Actions", "Python", "cURL", "JavaScript", "JSON"])

                            with output_tabs[4]:
                                st.json(output_json)

                            # Display AI Suggested Actions
                            with output_tabs[0]:
                                if actions_res.ok:
                                    actions_data = actions_res.json()
                                    st.info(f"**Recommended Action:** {actions_data.get('recommended_action', 'N/A').replace('_', ' ').title()}")
                                    c1, c2, c3 = st.columns(3)
                                    c1.metric("Priority", actions_data.get('priority', 'N/A'))
                                    c2.metric("Escalate?", "Yes" if actions_data.get('escalate') else "No")
                                    c3.metric("Est. CSAT", f"{actions_data.get('estimated_customer_satisfaction', 0)*100:.0f}%")
                                else:
                                    st.warning("Could not generate AI suggested actions.")

                            python_code, curl_code, js_code = generate_code_snippets(f"{API_BASE_URL}/analyze", input_text)
                            with output_tabs[1]:
                                st.code(python_code, language="python")
                            with output_tabs[2]:
                                st.code(curl_code, language="bash")
                            with output_tabs[3]:
                                st.code(js_code, language="javascript")

                            # --- Export Buttons ---
                            ec1, ec2 = st.columns(2)
                            with ec1:
                                st.download_button("Export JSON", json.dumps(output_json, indent=2), "analysis.json", "application/json", use_container_width=True)
                            with ec2:
                                st.download_button("Export CSV", pd.DataFrame([output_json]).to_csv(index=False), "analysis.csv", "text/csv", use_container_width=True)

                        except requests.exceptions.RequestException as e:
                            st.error(f"API Connection Error: Could not connect to the backend at `{API_BASE_URL}`.")
                            st.info("Please make sure the FastAPI server is running in a separate terminal using the command: `python main.py`")
            else:
                # Show a placeholder
                st.json({
                    "sentiment": "Mixed",
                    "confidence": 0.96,
                    "emotions": ["Frustrated", "Satisfied"],
                    "urgency": "Medium",
                    "category": "Delivery",
                    "summary": "Customer experienced delayed delivery but appreciated support.",
                    "suggested_reply": "We sincerely apologize for the delay..."
                })

with tab_dashboard:
    section_header("Dashboard", "Your usage, at a glance", "Live metrics for today and your current plan.")

    st.markdown("##### Today's Usage")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("API Requests", "152", "+12%", help="Total requests made today.")
    c2.metric("Positive Sentiment", "48%", "4%", help="Percentage of reviews with positive sentiment.")
    c3.metric("Negative Sentiment", "21%", "-2%", help="Percentage of reviews with negative sentiment.")
    c4.metric("Avg. Response Time", "210 ms", "-30ms", help="Average API response time.")

    st.write("")

    with st.container(border=True):
        st.markdown("##### Current Plan Usage")
        plan = "Free"
        used = 483
        limit = 1000
        remaining = limit - used

        c1, c2, c3 = st.columns(3)
        c1.metric("Plan", plan)
        c2.metric("Requests Used", f"{used:,}")
        c3.metric("Requests Remaining", f"{remaining:,}")
        st.progress(used / limit, text=f"You have used {used/limit:.1%} of your monthly requests.")

    st.write("")

    with st.container(border=True):
        st.markdown("##### API Keys")
        c1, c2 = st.columns([3, 1])
        with c1:
        with c2:
            st.button("Regenerate Key", use_container_width=True)

        c1, c2 = st.columns([3, 1])
        with c1:
            st.text_input("Development Key", "sk_test_p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e", type="password", disabled=True, label_visibility="collapsed")
        with c2:
            st.button("Regenerate Key", use_container_width=True, key="dev_regen")

with tab_batch:
    section_header("Batch Analysis", "Analyze in bulk", "Upload a CSV or Excel file with a 'text' column to analyze multiple reviews at once.")

    with st.container(border=True):
        uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                if 'text' not in df.columns:
                    st.error("File must contain a 'text' column.")
                else:
                    st.success(f"File '{uploaded_file.name}' uploaded successfully with {len(df)} reviews.")
                    if st.button("Start Batch Analysis", use_container_width=True, type="primary"):
                        results = []
                        progress_bar = st.progress(0, text="Analyzing reviews...")
                        for i, row in df.iterrows():
                            try:
                                res = requests.post(f"{API_BASE_URL}/analyze", json={"text": row['text']})
                                if res.ok:
                                    results.append(res.json())
                                else:
                                    results.append({"error": "API call failed"})
                            except Exception:
                                results.append({"error": "Connection failed"})
                            progress_bar.progress((i + 1) / len(df), text=f"Analyzing review {i+1}/{len(df)}")

                        results_df = pd.DataFrame(results)
                        st.dataframe(results_df, use_container_width=True)

                        output = BytesIO()
                        results_df.to_csv(output, index=False)
                        st.download_button("Download Results as CSV", data=output.getvalue(), file_name="batch_analysis_results.csv", mime="text/csv", use_container_width=True)

            except Exception as e:
                st.error(f"Error processing file: {e}")

with tab_history:
    section_header("History", "Recent analyses", "Everything you've run in this session.")
    if not st.session_state.history:
        st.info("No analyses performed in this session yet.")
    else:
        for i, item in enumerate(st.session_state.history):
            with st.expander(f"Analysis #{i+1}: {item['input'][:50]}..."):
                st.json(item['output'])

with tab_automation:
    section_header("Automation", "Webhooks", "Send analysis results to other services automatically.")

    with st.container(border=True):
        st.markdown("##### Create a New Webhook")
        c1, c2 = st.columns([1, 2])
        with c1:
            event_type = st.selectbox("When this event happens...", ("Negative Review", "High Urgency", "Spam Detected"))
        with c2:
            target_url = st.text_input("Send a POST request to this URL", placeholder="https://yourservice.com/webhook-receiver")

        if st.button("Create Webhook", use_container_width=True, type="primary"):
            st.success(f"Webhook created! It will trigger on '{event_type}' and send data to '{target_url}'.")

    st.write("")

    with st.container(border=True):
        st.markdown("##### Active Webhooks")
        st.info("This section is under construction. It will list all your active webhooks with options to edit or delete them.")

with tab_docs:
    section_header("Docs", "API documentation", "Our API is built on standard REST principles.")

    with st.container(border=True):
        st.markdown("##### Available Endpoints")
        endpoints_data = {
            "Method": ["POST", "POST", "POST", "POST", "POST", "POST"],
            "Endpoint": ["/analyze", "/reply", "/actions", "/batch", "/emotion", "/summarize-reviews"],
            "Description": [
                "Performs a full analysis of a single text.",
                "Generates a contextual reply in a specified tone.",
                "Provides AI-suggested actions for a piece of feedback.",
                "Analyzes a batch of reviews from a file upload.",
                "Detects emotions in a piece of text.",
                "Summarizes a list of reviews."
            ]
        }
        st.table(pd.DataFrame(endpoints_data))
        st.markdown("For a complete, interactive experience with all endpoints, use our auto-generated documentation:")
        st.markdown("- **[Interactive REST API Docs (Swagger)](http://localhost:8000/docs)**")
        st.markdown("- **[GraphQL Playground](http://localhost:8000/graphql)**")

with tab_pricing:
    section_header("Pricing", "Plans", "Choose the plan that fits your usage.")
    with st.container(border=True):
        st.info("This section is under construction. It will detail the available subscription tiers.")