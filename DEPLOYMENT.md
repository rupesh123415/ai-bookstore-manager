# AI Bookstore Management - Deployment Guide

## Prerequisites

1. **OpenRouter API Key**: Get your API key from [OpenRouter](https://openrouter.ai/)
2. **Supabase Project**: Set up a Supabase project with a `BOOK` table
3. **Supabase API Key**: Use the **anon/public** key (not the service_role key)

## Local Development Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create secrets file:**
   Create `.streamlit/secrets.toml` with:
   ```toml
   OPENROUTER_API_KEY = "your_openrouter_api_key"
   SUPABASE_KEY = "your_supabase_anon_key"
   ```

3. **Run the app:**
   ```bash
   streamlit run Main_app.py
   ```

## Streamlit Cloud Deployment

1. **Push your code to GitHub**

2. **Connect to Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set the main file path to `Main_app.py`

3. **Configure Secrets:**
   - In your Streamlit Cloud app settings
   - Go to "Secrets" section
   - Add the following TOML format:
   ```toml
   OPENROUTER_API_KEY = "your_openrouter_api_key"
   SUPABASE_KEY = "your_supabase_anon_key"
   ```

## Other Deployment Platforms

### Heroku
Set environment variables:
```bash
heroku config:set OPENROUTER_API_KEY=your_key
heroku config:set SUPABASE_KEY=your_key
```

### Railway
Add environment variables in the Railway dashboard:
- `OPENROUTER_API_KEY`
- `SUPABASE_KEY`

### Docker
Create a `.env` file:
```env
OPENROUTER_API_KEY=your_openrouter_api_key
SUPABASE_KEY=your_supabase_anon_key
```

## Supabase Database Setup

Create a `BOOK` table with the following structure:
```sql
CREATE TABLE BOOK (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    price NUMERIC(10,2) NOT NULL
);
```

## Troubleshooting

### 401 Authentication Error
- Ensure you're using the **anon/public** key from Supabase (not service_role)
- Check that your Supabase project is active
- Verify the API key is correctly set in your deployment environment

### API Key Issues
- Make sure your OpenRouter API key is valid and has sufficient credits
- Check that the Supabase URL is correct
- Ensure your Supabase project has the required `BOOK` table

### Local vs Production
- The app now supports both local secrets and environment variables
- For production, prefer environment variables for security
- For local development, use the `.streamlit/secrets.toml` file
