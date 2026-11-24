
import os
import re
import time
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Page configuration
st.set_page_config(
    page_title="Library Assistant Bot",
    page_icon="📚",
    layout="centered"
)

# Application heading
st.title("📚 Library Assistant Bot")
st.write("Your AI-powered personal library assistant.")
st.caption("Find books by topic, title or author.")

# Load catalogue
@st.cache_data
def load_books():
    return pd.read_csv("library_catalogue.csv").fillna("")

try:
    books = load_books()
except Exception as e:
    st.error(f"Unable to load catalogue: {e}")
    st.stop()

# Search books intelligently
def search_books(query):

    columns = [
        "title", "author", "category",
        "keywords", "description"
    ]

    stopwords = {
        "recommend", "recommendation", "recommendations",
        "book", "books", "the", "a", "an", "for",
        "and", "or", "to", "of", "in", "on", "with",
        "from", "about", "me", "my", "i", "want",
        "suggest", "find", "search", "best", "top",
        "give", "please", "learning", "learn",
        "written", "by", "can", "you", "level"
    }

    words = re.findall(r"[a-zA-Z0-9]+", query.lower())

    keywords = [
        word for word in words
        if word not in stopwords and len(word) > 1
    ]

    if not keywords:
        return books.iloc[0:0]

    # Weighted search scoring
    weights = {
        "title": 5,
        "author": 5,
        "category": 4,
        "keywords": 3,
        "description": 1
    }

    scores = pd.Series(0, index=books.index, dtype="int64")

    for column, weight in weights.items():

        text = books[column].astype(str)

        for word in keywords:

            matches = text.str.contains(
                re.escape(word),
                case=False,
                na=False,
                regex=True
            )

            scores += matches.astype(int) * weight

    results = books.loc[scores > 0].copy()

    if results.empty:
        return results

    results["_score"] = scores.loc[results.index]

    results = results.sort_values(
        "_score",
        ascending=False
    )

    return results.drop(columns=["_score"]).head(10)


# Local fallback if Gemini is unavailable
def local_recommendations(matching_books):

    output = (
        "### 📚 Catalogue-Based Recommendations\n\n"
        "**Gemini is currently unavailable. "
        "These are catalogue matches, not AI-generated recommendations.**\n\n"
    )

    for index, (_, book) in enumerate(
        matching_books.head(3).iterrows(), 1
    ):

        output += (
            f"**{index}. {book['title']}**\n\n"
            f"- Author: {book['author']}\n"
            f"- Category: {book['category']}\n"
            f"- Availability: {book['availability']}\n"
            f"- Description: {book['description']}\n\n"
        )

    return output


# Gemini recommendation function
def get_recommendations(query, matching_books):

    if not API_KEY:
        return local_recommendations(matching_books)

    if matching_books.empty:
        return "No matching books found. Try another topic or author."

    try:

        client = genai.Client(api_key=API_KEY)

        catalogue = matching_books.to_string(index=False)

        prompt = f"""
You are an intelligent Library Assistant Bot.

Student query: {query}

AVAILABLE LIBRARY CATALOGUE:
{catalogue}

YOUR TASK:
Recommend the best 3 books for the student.

RULES:
1. Recommend only books from the supplied catalogue.
2. Never invent book titles or authors.
3. Explain why each book is relevant.
4. Include title, author, category and availability.
5. Use simple, student-friendly language.
6. Recommend fewer than 3 if fewer relevant books exist.
7. Do not repeat recommendations.
8. Format the response using headings and bullet points.
"""

        # Use the model identified by the earlier API error
        model = "gemini-3.8-flash"

        # One retry for temporary server errors
        for attempt in range(2):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if response.text:
                    return response.text

                return local_recommendations(matching_books)

            except Exception as e:

                error_message = str(e)
                error_code = getattr(e, "code", None)

                temporary = (
                    error_code in (429, 500, 502, 503, 504)
                    or any(
                        code in error_message
                        for code in ["429", "500", "502", "503", "504"]
                    )
                )

                if temporary and attempt == 0:
                    time.sleep(2)
                    continue

                if temporary:
                    return local_recommendations(matching_books)

                return (
                    f"Gemini API error: {error_message}\n\n"
                    + local_recommendations(matching_books)
                )

    except Exception as e:

        return (
            f"Unable to initialize Gemini: {e}\n\n"
            + local_recommendations(matching_books)
        )


# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_query = st.chat_input(
    "Ask about books, authors or topics..."
)

if user_query:

    st.session_state.messages.append({
        "role": "user",
        "content": user_query
    })

    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):

        matching_books = search_books(user_query)

        if matching_books.empty:

            answer = (
                "I couldn't find matching books in our catalogue. "
                "Please try another topic, title or author."
            )

        else:

            with st.spinner(
                "Searching the catalogue and consulting Gemini..."
            ):

                answer = get_recommendations(
                    user_query,
                    matching_books
                )

        st.markdown(answer)

        if not matching_books.empty:

            with st.expander("📖 View matching catalogue records"):

                st.dataframe(
                    matching_books,
                    use_container_width=True
                )

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })


# Sidebar
with st.sidebar:

    st.header("📖 Library Information")

    st.metric("Total Books", len(books))

    available = books[
        books["availability"].astype(str).str.lower()
        == "available"
    ]

    st.metric("Available Books", len(available))

    st.markdown("---")

    st.write("**Try these searches:**")
    st.write("- Python programming")
    st.write("- Artificial Intelligence")
    st.write("- Morgan Housel")
    st.write("- Database")
    st.write("- Personal finance")

    if st.button("Clear Chat"):

        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    st.caption(
        "Library Assistant Bot | LLM Mini Project | Roll No. 15"
    )
