# Import the required libraries
import streamlit as st
from openai import OpenAI
from supabase import create_client
import json
import pandas as pd

# Set the Appliction page configuration
st.set_page_config(
    page_title="AI Bookstore Management",
    page_icon="📚",
    layout="wide",
)

# Supabase and OpenAI API Configuration
OPENROUTER_API_KEY = "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"
SUPABASE_URL = "https://nstsuzabnztqriureeoi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5zdHN1emFibnp0cXJpdXJlZW9pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYxNTE1MTksImV4cCI6MjA3MTcyNzUxOX0.lHjfHAQVCnxGePPAQAFkOkR0nsF29A7gqCaox67InZE"

# Initialize clients
@st.cache_resource
def init_clients():
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return client, supabase

client, supabase = init_clients()

# The function takes a natural language prompt as input and returns a list of books that match the prompt

def filter_books_with_llm(prompt):
    """Filter books using natural language prompt interpreted by LLM"""
    
    schema_info = """
    Table: BOOK
    Columns:
    - id: integer (primary key)
    - title: text (book title)
    - stock: integer (quantity in stock)
    - price: numeric (book price)
    """
    
    system_prompt = f"""
    You are a database query assistant. Based on the user's request, generate a JSON object with filter criteria for a Supabase query.
    
    {schema_info}
    
    Available filter operators:
    - eq: equals
    - gt: greater than
    - gte: greater than or equal
    - lt: less than
    - lte: less than or equal
    - neq: not equal
    - like: contains (for text)
    - ilike: case-insensitive contains (for text)
    
    Return ONLY a JSON object with this structure:
    {{
        "filters": [
            {{
                "column": "column_name",
                "operator": "operator",
                "value": "value"
            }}
        ]
    }}
    
    Examples:
    - "books with price 1000" → {{"filters": [{{"column": "price", "operator": "eq", "value": 1000}}]}}
    - "books cheaper than 500" → {{"filters": [{{"column": "price", "operator": "lt", "value": 500}}]}}
    - "books with stock more than 10" → {{"filters": [{{"column": "stock", "operator": "gt", "value": 10}}]}}
    """
    
    try:
        with st.spinner("🤖 AI is processing your query..."):
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
        
        llm_response = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        start_idx = llm_response.find('{')
        end_idx = llm_response.rfind('}') + 1
        json_str = llm_response[start_idx:end_idx]
        
        filter_config = json.loads(json_str)
        
        # Build Supabase query
        query = supabase.table("BOOK").select("*")
        
        # Apply filters
        for filter_item in filter_config.get("filters", []):
            column = filter_item["column"]
            operator = filter_item["operator"]
            value = filter_item["value"]
            
            # Convert value to appropriate type
            if column in ["price", "stock"]:
                try:
                    value = float(value) if "." in str(value) else int(value)
                except:
                    pass
            
            # Apply the filter
            if operator == "eq":
                query = query.eq(column, value)
            elif operator == "gt":
                query = query.gt(column, value)
            elif operator == "gte":
                query = query.gte(column, value)
            elif operator == "lt":
                query = query.lt(column, value)
            elif operator == "lte":
                query = query.lte(column, value)
            elif operator == "neq":
                query = query.neq(column, value)
            elif operator == "like":
                query = query.like(column, f"%{value}%")
            elif operator == "ilike":
                query = query.ilike(column, f"%{value}%")
        
        result = query.execute()
        return result.data
        
    except Exception as e:
        st.error(f"❌ Error processing filter: {str(e)}")
        return None

def display_books(books, title="Books"):
    """Display books in a nice format"""
    if not books:
        st.warning("No books found.")
        return
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(books)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Books", len(books))
    with col2:
        st.metric("Average Price", f"{df['price'].mean():.2f}")
    with col3:
        st.metric("Total Stock", df['stock'].sum())
    with col4:
        st.metric("Low Stock Books", len(df[df['stock'] < 5]))
    
    # Display table
    st.subheader(f"📚 {title}")
    st.dataframe(
        df,
        column_config={
            "id": "ID",
            "title": "Title",
            "stock": "Stock",
            "price": st.column_config.NumberColumn("Price", format="%.2f")
        },
        hide_index=True,
        use_container_width=True
    )

# --- MAIN APP ---
def main():
    # Main title of the application
    st.title("📚 AI Bookstore Management System")
    st.markdown("---")
    
    # Subtitle of the application
    
    st.header("🔍 AI-Powered Book Filter")
    st.markdown("Ask questions in natural language to filter books!")
        
    # Example queries
    st.markdown("**💡 Example queries:**")
    st.markdown("- books with price 1000")
    st.markdown("- books cheaper than 500")
    st.markdown("- books with stock more than 10")
    st.markdown("- books with title containing Harry Potter")
        
    # Query input
    query = st.text_input(
            "🎯 Enter your filter query:",
            placeholder="e.g., books cheaper than 500"
    )
        
    if st.button("🔍 Search", type="primary"):
            if query:
                filtered_books = filter_books_with_llm(query)
                if filtered_books is not None:
                    display_books(filtered_books, f"Results for: '{query}'")
                else:
                    st.error("Failed to process the query. Please try again.")
            else:
                st.warning("Please enter a query.")
        
    # Quick filters
    st.subheader("⚡ Quick Filters")
    col1, col2, col3 = st.columns(3)
        
    with col1:
            if st.button("💰 Expensive Books (>1000)"):
                filtered_books = filter_books_with_llm("books with price greater than 1000")
                if filtered_books is not None:
                    display_books(filtered_books, "Expensive Books (>1000)")
        
    with col2:
            if st.button("📦 Low Stock (<5)"):
                filtered_books = filter_books_with_llm("books with stock less than 5")
                if filtered_books is not None:
                    display_books(filtered_books, "Low Stock Books (<5)")
        
    with col3:
            if st.button("💸 Cheap Books (<500)"):
                filtered_books = filter_books_with_llm("books with price less than 500")
                if filtered_books is not None:
                    display_books(filtered_books, "Cheap Books (<500)")
    
    

if __name__ == "__main__":
    main()
