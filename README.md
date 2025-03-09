# Handbook Agent

A tool for analyzing, indexing, and searching PDF documents with intelligent text categorization and enhanced search capabilities.

## Overview

Handbook Agent is designed to extract structured information from PDF documents, categorize text based on formatting, and provide intelligent search functionality. It uses AI to analyze document structure and optimize search results.

## Features

- **PDF Text Extraction**: Extract text with formatting information (font, size, style)
- **Text Categorization**: Automatically categorize text into titles, headings, body text, lists, etc.
- **AI-Powered Analysis**: Get recommendations for optimal search structure using OpenAI's GPT-4
- **Intelligent Indexing**: Create searchable indexes with text type classification
- **Enhanced Search**: Multiple search modes including general, headings-focused, topic-based, and weighted search

## Requirements

- Python 3.7+
- Required packages:
  - PyMuPDF (fitz)
  - OpenAI
  - Whoosh
  - python-dotenv

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/handbook-agent.git
   cd handbook-agent
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install pymupdf openai whoosh python-dotenv
   ```

4. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

### Analyzing a PDF

To analyze a PDF and get AI recommendations for search optimization:

bash
python pdf_analyzer.py path/to/your/document.pdf

This will:
- Extract text with formatting information
- Categorize text based on formatting
- Get AI recommendations for search optimization
- Create a searchable index structure

### Indexing a PDF

To create a searchable index for a PDF:
bash
python index_pdf.py

Note: You may need to modify the PDF path in the script to point to your document.

### Searching a PDF

After indexing, you can search the PDF using various search modes:

bash
python search_pdf.py

This will start an interactive search interface with the following commands:
- `search <query>` - General search across all content
- `headings <query>` - Search focusing on headings
- `topics <query>` - Find key topics related to your query
- `weighted <query>` - Use weighted fields for more relevant results
- `help` - Display help information
- `exit` - Exit the program

## Example

$ python search_pdf.py
PDF Search Tool - Type 'help' for available commands
Enter your search command: weighted business strategy
Found 15 relevant results:
Page 42 [Contains: heading1, heading2, body] (Score: 6.78)
Link: file:///path/to/your/document.pdf#page=42
Page 87 [Contains: heading2, bold_text, body] (Score: 5.92)
Link: file:///path/to/your/document.pdf#page=87

## Notes

- The PDF indexing is optimized for documents with clear formatting hierarchy
- Large PDFs may take longer to process
- The `.gitignore` file excludes PDFs from version control due to potential size