# Topic Map Generator

A Streamlit web application that generates comprehensive, RAG-optimized topical maps for SEO and AEO content strategy. The app performs live web research using the Tavily API and structures findings into a hierarchical topic map with **Pillar > Cluster > Spoke** architecture.

Built for SEO professionals and content strategists who need research-backed topical maps that serve both traditional search engines and AI answer engines (ChatGPT, Perplexity, Google AI Overviews).

![Screenshot placeholder](https://via.placeholder.com/800x400?text=Topic+Map+Generator+Screenshot)

## Features

- **Live web research** via Tavily Search API (8+ queries per generation)
- **AI-powered topic map generation** using Claude (claude-sonnet-4-20250514)
- **Pillar > Cluster > Spoke** hierarchy with internal linking strategy
- **13 data fields per topic** including semantic entities, PAA questions, citations, RAG directions
- **Interactive data table** with filtering by level, intent, content type, and priority
- **Visual hierarchy tree** showing topic relationships
- **CSV export** with pipe-separated multi-value fields
- **Optional Google Drive upload** for team collaboration
- **Session state persistence** — results survive Streamlit rerenders

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/topical-map-generator.git
cd topical-map-generator
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API keys

Copy the example environment file and add your keys:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```
ANTHROPIC_API_KEY=your_anthropic_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### 4. Run the app

```bash
streamlit run app.py
```

## API Key Setup

### Anthropic (Required)

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Create an account or sign in
3. Navigate to API Keys and create a new key
4. Add to your `.env` as `ANTHROPIC_API_KEY`

### Tavily (Required)

1. Go to [tavily.com](https://tavily.com/)
2. Sign up for an account
3. Get your API key from the dashboard
4. Add to your `.env` as `TAVILY_API_KEY`

### Google Drive (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable the Google Drive API
3. Create OAuth 2.0 credentials (Desktop application type)
4. Add `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` to your `.env`

## Streamlit Cloud Deployment

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub repository
4. Set the main file path to `app.py`
5. Add your API keys in **Settings > Secrets**:

```toml
ANTHROPIC_API_KEY = "your_key_here"
TAVILY_API_KEY = "your_key_here"
```

## CSV Output Schema

The exported CSV uses these columns:

| Column | Description | Format |
|--------|-------------|--------|
| Level | Pillar, Cluster, or Spoke | Text |
| Content Title | SEO-optimized article title | Text |
| Primary Keyword | Main target search term | Text |
| User Intent | Informational, Navigational, Commercial Investigation, Transactional | Text |
| Semantic Entities | Related knowledge graph entities | Pipe-separated |
| Content Type | Article format (Ultimate Guide, How-To, etc.) | Text |
| RAG Directions | AI retrieval optimization instructions | Text |
| PAA Questions | People Also Ask questions to address | Pipe-separated |
| Citations | Claims and sources needing citation | Pipe-separated |
| Parent Topic | Parent topic in hierarchy | Text |
| Priority Score | 1-5 (5 = highest priority) | Integer |
| Word Count Range | Recommended word count | Text (e.g., "2500-4000") |
| Internal Link Targets | Other topics to link to | Pipe-separated |

## License

MIT
