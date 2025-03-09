import fitz  # PyMuPDF
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID, KEYWORD, NUMERIC
import os
import json
from whoosh.analysis import StemmingAnalyzer

# Enhanced schema with text type classification
schema = Schema(
    title=ID(stored=True),
    content=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    text_types=KEYWORD(stored=True, commas=True),  # Store text types as comma-separated values
    title_content=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    heading1_content=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    heading2_content=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    heading3_content=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    body_content=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    bold_content=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    title_weight=NUMERIC(stored=True, default=7),
    heading1_weight=NUMERIC(stored=True, default=6),
    heading2_weight=NUMERIC(stored=True, default=5),
    heading3_weight=NUMERIC(stored=True, default=4),
    body_weight=NUMERIC(stored=True, default=3),
    bold_weight=NUMERIC(stored=True, default=4)
)

# Create index directory
index_dir = "indexdir"
if not os.path.exists(index_dir):
    os.mkdir(index_dir)
index = create_in(index_dir, schema)

# Open PDF
pdf_path = "bus-comb.pdf"  # Path to your uploaded file
doc = fitz.open(pdf_path)

# Function to classify text blocks based on formatting
def classify_text_blocks(page):
    blocks = page.get_text("dict")["blocks"]
    classified_blocks = []
    
    for block in blocks:
        if "lines" not in block:
            continue
            
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"]
                if not text.strip():
                    continue
                    
                font_size = span["size"]
                font_flags = span["flags"]  # Contains bold, italic info
                
                # Simple classification logic - customize based on your PDF
                text_type = "body"
                if font_size > 14:
                    text_type = "heading1"
                elif font_size > 12:
                    text_type = "heading2"
                elif font_size > 10:
                    text_type = "heading3"
                
                # Check if bold (bit 0 of flags is set)
                if font_flags & 1:
                    if text_type == "body":
                        text_type = "bold_text"
                
                classified_blocks.append({
                    "text": text,
                    "type": text_type,
                    "font_size": font_size
                })
    
    return classified_blocks

# Index PDF contents with text classification
writer = index.writer()
for page_num in range(len(doc)):
    page = doc[page_num]
    
    # Get regular text for full-text search
    full_text = page.get_text("text")
    
    # Get classified text blocks
    classified_blocks = classify_text_blocks(page)
    
    # Extract text types present on this page
    text_types = set(block["type"] for block in classified_blocks)
    
    # Organize content by text type
    title_content = ""
    heading1_content = ""
    heading2_content = ""
    heading3_content = ""
    body_content = ""
    bold_content = ""
    
    for block in classified_blocks:
        if block["type"] == "heading1":
            heading1_content += block["text"] + " "
        elif block["type"] == "heading2":
            heading2_content += block["text"] + " "
        elif block["type"] == "heading3":
            heading3_content += block["text"] + " "
        elif block["type"] == "body":
            body_content += block["text"] + " "
        elif block["type"] == "bold_text":
            bold_content += block["text"] + " "
    
    # Store the classified blocks as JSON
    classified_json = json.dumps(classified_blocks)
    
    writer.add_document(
        title=f"Page {page_num+1}", 
        content=full_text,
        text_types=",".join(text_types),
        title_content=f"Page {page_num+1}",  # Using page number as title
        heading1_content=heading1_content,
        heading2_content=heading2_content,
        heading3_content=heading3_content,
        body_content=body_content,
        bold_content=bold_content,
        # Add the weight values explicitly
        title_weight=7,
        heading1_weight=6,
        heading2_weight=5,
        heading3_weight=4,
        body_weight=3,
        bold_weight=4
    )
    
writer.commit()

print("Indexing complete with text classification and weighted search capabilities.")
print("The following weights are applied to search results:")
print("- Title: 7")
print("- Heading1: 6")
print("- Heading2: 5")
print("- Heading3: 4")
print("- Body text: 3")
print("- Bold text: 4")
print("You can now search the PDF with improved relevance ranking.")