import os
import re
import fitz  # PyMuPDF
import openai
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables (for OpenAI API key)
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text_with_formatting(pdf_path):
    """Extract text from PDF with formatting information."""
    doc = fitz.open(pdf_path)
    text_blocks = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Extract text blocks with their formatting
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_blocks.append({
                            "text": span["text"],
                            "font": span["font"],
                            "size": span["size"],
                            "flags": span["flags"],  # Bold, italic, etc.
                            "page": page_num + 1
                        })
    
    return text_blocks

def categorize_text(text_blocks):
    """Categorize text blocks by their likely type based on formatting."""
    categories = {
        "title": [],
        "heading1": [],
        "heading2": [],
        "body_text": [],
        "bullet_points": [],
        "numbered_lists": [],
        "tables": [],
        "captions": [],
        "footnotes": []
    }
    
    # Sort blocks by size to identify hierarchy
    sorted_blocks = sorted(text_blocks, key=lambda x: x["size"], reverse=True)
    
    # Get the most common font size (likely body text)
    sizes = [block["size"] for block in text_blocks]
    most_common_size = max(set(sizes), key=sizes.count)
    
    # Simple categorization rules
    for block in text_blocks:
        text = block["text"].strip()
        if not text:
            continue
            
        # Check for bullet points or numbered lists
        if text.startswith("•") or text.startswith("-") or re.match(r"^\d+\.", text):
            if text.startswith("•") or text.startswith("-"):
                categories["bullet_points"].append(block)
            else:
                categories["numbered_lists"].append(block)
        # Title/headings (based on font size)
        elif block["size"] > most_common_size * 1.5:
            categories["title"].append(block)
        elif block["size"] > most_common_size * 1.2:
            categories["heading1"].append(block)
        elif block["size"] > most_common_size * 1.1:
            categories["heading2"].append(block)
        # Footnotes (smaller text)
        elif block["size"] < most_common_size * 0.9:
            categories["footnotes"].append(block)
        # Default to body text
        else:
            categories["body_text"].append(block)
    
    return categories

def get_sample_sections(categories):
    """Get representative samples from each text category."""
    samples = {}
    
    for category, blocks in categories.items():
        if blocks:
            # Get up to 3 samples from each category
            sample_blocks = blocks[:min(3, len(blocks))]
            samples[category] = [block["text"] for block in sample_blocks]
    
    return samples

def get_ai_recommendations(categories, samples):
    """Use OpenAI API to get recommendations on optimal search structure."""
    
    # Prepare the prompt with category information and samples
    prompt = "I have extracted text from a PDF document and categorized it as follows:\n\n"
    
    for category, blocks in categories.items():
        if blocks:
            prompt += f"- {category}: {len(blocks)} instances\n"
    
    prompt += "\nHere are some samples from each category:\n\n"
    
    for category, texts in samples.items():
        prompt += f"{category.upper()}:\n"
        for text in texts:
            prompt += f"- \"{text}\"\n"
        prompt += "\n"
    
    prompt += """Based on these text categories and samples, please recommend:
1. The optimal way to structure this text for search functionality
2. How different text types should be weighted in search results
3. Any preprocessing steps that would improve search accuracy
4. The best approach for handling user queries against this document structure"""

    # Make the API call
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert in document analysis and search optimization."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )
    
    return response.choices[0].message.content

def create_searchable_index(categories, recommendations):
    """
    Create a searchable index based on the AI recommendations.
    This is a placeholder function - the actual implementation would depend on the AI's recommendations.
    """
    # This would be implemented based on the AI's recommendations
    print("Creating searchable index based on AI recommendations...")
    print("Recommendations:", recommendations)
    
    # Example implementation (to be modified based on actual recommendations)
    searchable_index = {
        "metadata": {
            "categories": {k: len(v) for k, v in categories.items() if v},
            "recommendations": recommendations
        },
        "content": {}
    }
    
    for category, blocks in categories.items():
        searchable_index["content"][category] = [
            {"text": block["text"], "page": block["page"], "metadata": {
                "font": block["font"],
                "size": block["size"],
                "flags": block["flags"]
            }}
            for block in blocks
        ]
    
    return searchable_index

def search_document(index, query):
    """
    Search the document using the created index.
    This is a placeholder function - the actual implementation would depend on the AI's recommendations.
    """
    # This would be implemented based on the AI's recommendations
    print(f"Searching for: {query}")
    # Implement search logic here
    
    return {"results": "Search results would appear here"}

def main(pdf_path):
    """Main function to process PDF and create searchable structure."""
    print(f"Processing PDF: {pdf_path}")
    
    # Extract text with formatting
    text_blocks = extract_text_with_formatting(pdf_path)
    print(f"Extracted {len(text_blocks)} text blocks")
    
    # Categorize text
    categories = categorize_text(text_blocks)
    print("Text categorized into:")
    for category, blocks in categories.items():
        if blocks:
            print(f"- {category}: {len(blocks)} instances")
    
    # Get samples for AI analysis
    samples = get_sample_sections(categories)
    
    # Get AI recommendations
    print("Getting AI recommendations...")
    recommendations = get_ai_recommendations(categories, samples)
    print("\nAI RECOMMENDATIONS:")
    print(recommendations)
    
    # Create searchable index
    index = create_searchable_index(categories, recommendations)
    
    # Example search
    # search_results = search_document(index, "example query")
    
    return {
        "categories": categories,
        "recommendations": recommendations,
        "index": index
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python pdf_analyzer.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    results = main(pdf_path)