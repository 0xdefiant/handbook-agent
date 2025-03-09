from whoosh.qparser import QueryParser, OrGroup, MultifieldParser
from whoosh.index import open_dir
from whoosh.query import Term, And, Or
import os
import webbrowser
from collections import defaultdict

def search_pdf(query, search_type="general"):
    """
    Search the PDF with enhanced capabilities based on text types.
    
    Args:
        query (str): The search query
        search_type (str): Type of search - "general", "headings", "topics", "weighted"
    """
    index = open_dir("indexdir")  # Open the index directory
    
    with index.searcher() as searcher:
        results = None
        
        if search_type == "general":
            # Standard search across all content
            parser = QueryParser("content", index.schema)
            parsed_query = parser.parse(query)
            results = searcher.search(parsed_query, limit=20)
            
        elif search_type == "headings":
            # Search specifically in headings by filtering for pages with heading text types
            parser = QueryParser("content", index.schema)
            content_query = parser.parse(query)
            
            # Filter for pages that have heading text types
            heading_types = ["heading1", "heading2", "heading3"]
            text_type_queries = [Term("text_types", t) for t in heading_types]
            type_query = Or(text_type_queries)
            
            # Combine content query with text type filter
            final_query = And([content_query, type_query])
            results = searcher.search(final_query, limit=20)
            
        elif search_type == "topics":
            # Identify key topics by prioritizing headings and bold text
            parser = MultifieldParser(["content"], schema=index.schema, group=OrGroup)
            content_query = parser.parse(query)
            
            # Get all matching results
            all_results = searcher.search(content_query, limit=None)
            
            # Group and score results by topic relevance
            topic_scores = defaultdict(int)
            topic_pages = defaultdict(list)
            
            for hit in all_results:
                page_num = int(hit['title'].split()[-1])
                text_types = hit.get('text_types', '').split(',')
                
                # Score based on text types present
                score = hit.score
                if 'heading1' in text_types:
                    score *= 3.0  # Major headings get highest priority
                elif 'heading2' in text_types:
                    score *= 2.5
                elif 'heading3' in text_types:
                    score *= 2.0
                elif 'bold_text' in text_types:
                    score *= 1.5  # Bold text gets medium priority
                
                # Use the page as a proxy for the topic
                topic_scores[page_num] = score
                topic_pages[page_num].append(hit)
            
            # Sort topics by score
            sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Take top results
            results = []
            for page_num, _ in sorted_topics[:10]:
                results.extend(topic_pages[page_num])
                
        elif search_type == "weighted":
            # Use the weighted fields from the index for more relevant results
            fields = ["title_content", "heading1_content", "heading2_content", 
                     "heading3_content", "body_content", "bold_content"]
            
            # Create a MultifieldParser with field weights from the schema
            weights = {
                "title_content": 7,
                "heading1_content": 6,
                "heading2_content": 5,
                "heading3_content": 4,
                "body_content": 3,
                "bold_content": 4
            }
            
            parser = MultifieldParser(fields, schema=index.schema, fieldboosts=weights)
            parsed_query = parser.parse(query)
            results = searcher.search(parsed_query, limit=20)
        
        if results:
            pdf_path = "bus-comb.pdf"  # Path to your uploaded file
            print(f"\nFound {len(results)} relevant results:")
            
            # Group results by page for better organization
            results_by_page = defaultdict(list)
            for result in results:
                page_number = int(result['title'].split()[-1])
                results_by_page[page_number].append(result)
            
            # Display results organized by page
            for page_number, page_results in sorted(results_by_page.items(), key=lambda x: max(hit.score for hit in x[1]), reverse=True):
                file_url = f"file://{os.path.abspath(pdf_path)}#page={page_number}"
                
                # Get text types for this page
                text_types = page_results[0].get('text_types', '').split(',')
                text_type_info = f" [Contains: {', '.join(text_types)}]" if text_types else ""
                
                # Get the highest score for this page
                max_score = max(hit.score for hit in page_results)
                
                # Printing clickable link (works in compatible terminals like iTerm, VSCode, etc.)
                print(f"\nPage {page_number}{text_type_info} (Score: {max_score:.2f})")
                print(f"Link: {file_url}")
                
                # Option to open the PDF
                # webbrowser.open(file_url)
            return True
        else:
            print("No relevant information found.")
            return False

def display_help():
    """Display help information about search commands"""
    print("\n=== PDF Search Help ===")
    print("Available commands:")
    print("  search <query>     - General search across all content")
    print("  headings <query>   - Search focusing on headings")
    print("  topics <query>     - Find key topics related to your query")
    print("  weighted <query>   - Use weighted fields for more relevant results")
    print("  help               - Display this help information")
    print("  exit               - Exit the program")
    print("\nExample: 'weighted business strategy'")

# Continuously ask the user for a search query
print("PDF Search Tool - Type 'help' for available commands")
while True:
    user_input = input("\nEnter your search command: ").strip()
    
    if user_input.lower() == 'exit':
        break
    elif user_input.lower() == 'help':
        display_help()
        continue
    
    # Parse command and query
    parts = user_input.split(maxsplit=1)
    if len(parts) < 2:
        if user_input.lower() not in ['exit', 'help']:
            print("Please enter a command and search query. Type 'help' for assistance.")
        continue
    
    command, query = parts
    
    if command.lower() == 'search':
        search_pdf(query, "general")
    elif command.lower() == 'headings':
        search_pdf(query, "headings")
    elif command.lower() == 'topics':
        search_pdf(query, "topics")
    elif command.lower() == 'weighted':
        search_pdf(query, "weighted")
    else:
        print(f"Unknown command: '{command}'. Type 'help' for available commands.")