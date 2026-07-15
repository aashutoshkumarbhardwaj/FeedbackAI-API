from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Literal
import os
from dotenv import load_dotenv
import streamlit as st
from pydantic import BaseModel, Field

load_dotenv()

# The user mentioned using OpenRouter. To use OpenRouter, you can configure the client like this:
model = ChatOpenAI(
    model_name="nvidia/nemotron-3-ultra-550b-a55b:free", 
    # model_name="mistralai/mistral-7b-instruct",  # Alternative model
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENAI_API_KEY"),  # Load the key from the .env file
)
# model = ChatOpenAI(model_name="gpt-3.5-turbo")


class SentimentSchema(BaseModel):
    sentiment: Literal['positive', 'negative'] = Field(description="The sentiment of the review.")


class DiagnosisSchema(BaseModel):
    issue_type: Literal['UX', 'performance', 'bug'] = Field(description="The category of the issue.")
    tone: Literal["calm", "disappointed"] = Field(description="The emotional tone of the user.")
    urgency: Literal['high', 'low'] = Field(description="How urgent or critical the issue is.")


# Create two separate structured models for each schema
sentiment_model = model.with_structured_output(SentimentSchema)
diagnosis_model = model.with_structured_output(DiagnosisSchema)


class ReviewState(TypedDict):
    review: str
    sentiment: Literal['positive', 'negative']
    diagnosis: dict
    response: str


def find_sentiment(state: ReviewState):
    print("---Finding Sentiment---")
    prompt = f"Determine the sentiment of the following review:\n\n'{state['review']}'"
    result = sentiment_model.invoke(prompt)
    print(f"Sentiment: {result.sentiment}")
    return {"sentiment": result.sentiment}

def check_sentiment(state: ReviewState) -> Literal['positive_response', 'run_diagnosis']:
    if state["sentiment"] == "positive":
        return "positive_response"
    else:
        return "run_diagnosis"


def positive_response(state: ReviewState):
    print("---Generating Positive Response---")
    prompt = f"""Write a warm and appreciative thank you message in response to this positive review:
    \nReview: {state["review"]}"""
    response = model.invoke(prompt).content
    return {"response": response}


def run_diagnosis(state: ReviewState):
    print("---Running Diagnosis on Negative Review---")
    prompt = f"""Diagnose the following negative review. Extract the issue type, user tone, and urgency.
    \nReview: {state['review']}"""
    response = diagnosis_model.invoke(prompt)
    print(f"Diagnosis: {response.model_dump()}")
    return {"diagnosis": response.model_dump()}


def negative_response(state: ReviewState):
    print("---Generating Negative Response---")
    diagnosis = state['diagnosis']
    prompt = f"""You are a customer support assistant. A user has an issue and sounds '{diagnosis['tone']}'.
    The issue is related to '{diagnosis['issue_type']}' and has an urgency of '{diagnosis['urgency']}'.
    Write an empathetic and helpful response that acknowledges the problem and offers a path to resolution."""
    response=model.invoke(prompt).content
    return {"response":response}


# Define the graph
workflow = StateGraph(ReviewState)

# Add nodes
workflow.add_node('find_sentiment', find_sentiment)
workflow.add_node('positive_response', positive_response)
workflow.add_node('run_diagnosis', run_diagnosis)
workflow.add_node('negative_response', negative_response)

# Define the graph edges
workflow.set_entry_point('find_sentiment')
workflow.add_conditional_edges(
    'find_sentiment',
    check_sentiment,
    {
        "positive_response": "positive_response",
        "run_diagnosis": "run_diagnosis"
    }
)
workflow.add_edge('run_diagnosis', 'negative_response')
workflow.add_edge('positive_response', END)
workflow.add_edge('negative_response', END)

# Compile the graph
app = workflow.compile()

# --- Streamlit UI ---

st.title("Sentiment Analysis and Response Generator")
st.write("Enter a customer review below to analyze its sentiment and generate an appropriate response.")

# Add an expander to show the graph diagram
with st.expander("View Workflow Diagram"):
    try:
        # Generate the graph image from the compiled app
        graph_image = app.get_graph().draw_mermaid_png()
        st.image(graph_image, caption="Workflow Graph")
        st.info("This diagram shows the conditional flow of the review analysis process, from sentiment analysis to the final response.")
    except Exception as e:
        st.warning(f"Could not generate graph diagram. Please install the necessary dependencies by running:\n\npip install pygraphviz playwright\nplaywright install")


review_text = st.text_area("Customer Review", height=150)

if st.button("Analyze Review"):
    if review_text:
        with st.spinner("Analyzing review and generating response..."):
            # The print statements in your functions will appear in the terminal
            # where streamlit is running.
            initial_state = {'review': review_text}
            final_state = app.invoke(initial_state)
            
            st.subheader("Analysis Complete!")
            
            # Display the final generated response on the web page
            st.markdown("### Generated Response:")
            st.write(final_state.get('response', 'No response generated.'))

    else:
        st.warning("Please enter a review to analyze.")