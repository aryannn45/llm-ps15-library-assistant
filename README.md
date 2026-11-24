# Library Assistant Bot

**Roll No. 15**

Library Assistant Bot is an AI-powered web application that helps students discover relevant books from a structured library catalogue. It combines weighted local search with Google Gemini recommendations and provides a clear fallback when the AI service is unavailable.

## Features

- Search books by title, author, topic, category, or keywords
- View ranked catalogue matches and availability
- Generate student-friendly book recommendations using Gemini
- Fall back to catalogue-based recommendations when Gemini is unavailable
- Maintain chat history during the active session
- Display total and available book counts in the sidebar
- Provide quick topic suggestions

## Technology Stack

- Python
- Streamlit
- Pandas
- Google Gen AI SDK
- python-dotenv

## Project Structure

```text
Library_Assistant_Bot/
|-- app.py
|-- library_catalogue.csv
|-- requirements.txt
|-- .env
|-- .gitignore
|-- README.md
`-- screenshots/
    |-- test1.png
    |-- test2.png
    |-- test3.png
    |-- test4.png
    `-- test5.png
```

## Getting Started

### 1. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Environment

Create a `.env` file in the project root and add a Gemini API key:

```text
GEMINI_API_KEY=your_api_key_here
```

Keep API keys private and do not commit the `.env` file.

### 4. Run the Application

```bash
streamlit run app.py
```

Open the local URL displayed by Streamlit in your browser.

## Usage

Enter a topic, book title, or author in the chat field. The application searches the catalogue, ranks relevant records, and recommends suitable books. Use the **Clear Chat** button in the sidebar to reset the conversation.

## Catalogue

Book records are stored in `library_catalogue.csv`. Each record includes:

- Book ID
- Title
- Author
- Category
- Keywords
- Description
- Availability

## Testing Screenshots

The `screenshots` directory contains placeholders for test evidence:

- `test1.png`
- `test2.png`
- `test3.png`
- `test4.png`
- `test5.png`

Replace these placeholders with actual application screenshots after testing.

## Author

Library Assistant Bot - Roll No. 15
