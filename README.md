# Liga ng mga Barangay Multilingual Chatbot 🇵🇭

A multilingual AI chatbot assistant serving as the knowledge interface for Liga ng mga Barangay (League of Barangays), built with Google ADK and advanced document search capabilities.

## 🎯 Features

### 🧠 Knowledge Retrieval
- **Local Documentation**: Uses `liga_documentation.md` file containing Liga ng mga Barangay Constitution, By-Laws, and FAQs
- **Hybrid Search**: Combines keyword matching and semantic search for accurate information retrieval
- **Q&A Processing**: Specialized handling of FAQ sections with structured question-answer pairs
- **Multilingual Embeddings**: Uses paraphrase-multilingual-MiniLM-L12-v2 for semantic understanding

### 🗣️ Multilingual Support
- **Filipino** - Native Filipino language support with keyword detection
- **English** - Full English language support  
- **Tag-lish** - Code-switched Filipino-English conversation style
- **Language Detection**: Automatically matches response language to user input
- **Natural Conversation**: Maintains conversational tone across all languages

### 🤖 Intelligent Behavior
- **Context-Aware**: Understands Liga ng mga Barangay domain (barangay governance, SK elections, local government)
- **Document-First**: Always searches documentation before using general knowledge
- **Graceful Fallback**: Uses general knowledge when documents don't contain relevant information
- **Query Handling**: Processes vague, incomplete, or slang-based queries intelligently

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google ADK
- Google AI Studio API key

### 1. Setup
```bash
# Clone repository
git clone <repository>
cd liga_chatbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate.bat  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
1. **Get Google AI Studio API Key**:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create API key

2. **Configure Environment**:
```bash
# Copy environment template
cp env_example.txt .env

# Edit .env file
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. Run the Chatbot
```bash
# Web interface (recommended)
python3 main.py

# Access at http://localhost:8080
```

## 💬 Sample Conversations

The chatbot handles queries in multiple languages and styles:

### Filipino
```
User: "Ano ang role ng Liga ng mga Barangay sa SK elections?"
Bot: "Ayon sa mga dokumento ng Liga ng mga Barangay, ang Liga ay may mahalagang papel sa..."
```

### English
```
User: "Can you explain what the Barangay Federation does?"
Bot: "Based on the Liga ng mga Barangay documents, the Barangay Federation serves as..."
```

### Tag-lish
```
User: "May mga training programs ba sila this month?"
Bot: "According to the latest documents, may mga scheduled training programs nga ang Liga this month..."
```

## 🏗️ Architecture

### Core Components

1. **Agent** (`agent.py`)
   - Main ADK agent with Gemini-2.0-flash model
   - Multilingual instruction set
   - Tool orchestration and conversation management

2. **LigaChatbotService** (`tools/agent_tools.py`)
   - Core service class with document processing
   - Language detection with Filipino/English/Tag-lish support
   - Hybrid search implementation (keyword + semantic)
   - Q&A pair extraction and processing

3. **Document Updater** (`utils/document_updater.py`)
   - Google Drive integration for document fetching
   - File format conversion (PDF, DOCX, Google Docs)
   - Automatic markdown generation

4. **Local Documentation** (`utils/liga_documentation.md`)
   - Comprehensive Liga ng mga Barangay knowledge base
   - Structured sections and FAQ pairs
   - Regular updates from Google Drive sources

### Data Flow
```
User Query → Language Detection → Document Search (Keyword + Semantic) → Context Formation → LLM Response → Language-Matched Output
```

## 🔧 Current Functions

### Main Functions

#### `search_liga_documents(query: str) -> Dict[str, Any]`
Primary search function that:
- Detects query language (Filipino/English/Tag-lish)
- Performs keyword and semantic search
- Returns structured results with confidence scores
- Provides context and source information

#### Language Detection Functions

#### `detect_language(text: str) -> Dict`
Advanced language detection that:
- Identifies Filipino indicators and patterns
- Detects Tag-lish (code-switching) patterns
- Returns confidence scores and language metrics
- Handles mixed-language content

#### Search Functions

#### `_keyword_search(query: str, threshold: float = 0.1) -> List[Dict]`
Keyword-based search that:
- Matches query words with document content
- Prioritizes Q&A pairs with score boosting
- Returns top 5 results above threshold

#### `_semantic_search(query: str, threshold: float = 0.3) -> List[Dict]`
Semantic similarity search that:
- Uses multilingual sentence transformers
- Computes cosine similarity scores
- Returns top 3 semantically relevant results

#### Document Processing Functions

#### `_parse_sections() -> List[Dict]`
Document parser that:
- Extracts sections with hierarchical structure
- Maintains title and content relationships
- Supports markdown formatting

#### `_extract_qa_pairs() -> List[Dict]`
FAQ processor that:
- Identifies Q&A patterns in documentation
- Structures question-answer pairs
- Enables specialized FAQ search

### Utility Functions

#### `update_liga_docs(credentials_path=None)`
Documentation updater that:
- Connects to Google Drive API
- Downloads files from Liga folder
- Converts various file formats to markdown
- Updates local documentation file

#### `get_service() -> LigaChatbotService`
Singleton pattern implementation:
- Returns global service instance
- Prevents multiple initializations
- Optimizes memory usage

## 📊 Performance Metrics

- **Response Accuracy**: Document-first approach with fallback to general knowledge
- **Language Detection**: 90%+ accuracy for Filipino/English/Tag-lish with pattern matching
- **Search Performance**: Sub-second retrieval with hybrid search approach
- **Multilingual Consistency**: Maintains context across language switches

## 🔧 Troubleshooting

### Common Issues

1. **Google Drive Authentication**:
```bash
# Check service account credentials
python3 -c "from liga_chatbot.utils.document_updater import DocumentUpdater; DocumentUpdater('path/to/credentials.json').authenticate()"
```

2. **Missing Documentation**:
```bash
# Update documentation from Google Drive
python3 -c "from liga_chatbot.utils.document_updater import update_liga_docs; update_liga_docs()"
```

3. **Language Detection Issues**:
```bash
# Test language detection
python3 -c "from liga_chatbot.tools.agent_tools import get_service; print(get_service().detect_language('your text'))"
```

4. **Search Performance**:
```bash
# Test document search
python3 -c "from liga_chatbot.tools.agent_tools import search_liga_documents; print(search_liga_documents('your query'))"
```

## 📚 Development

### Project Structure
```
liga_chatbot/
├── __init__.py                    # Module initialization
├── agent.py                       # Main ADK agent
├── tools/
│   ├── agent_tools.py            # Core service and search functions
│   └── __init__.py
├── utils/
│   ├── document_updater.py       # Google Drive integration
│   └── liga_documentation.md     # Local knowledge base
├── google_adk/                   # ADK framework
main.py                           # FastAPI web application
requirements.txt                  # Dependencies
env_example.txt                   # Environment template
```

### Key Classes

- **LigaChatbotService**: Main service class handling all document operations
- **DocumentUpdater**: Google Drive integration and file processing
- **Agent**: ADK agent with multilingual conversation capabilities

### Dependencies
- `google-adk`: ADK framework
- `sentence-transformers`: Multilingual embeddings
- `scikit-learn`: Cosine similarity calculations
- `langdetect`: Base language detection
- `google-generativeai`: Gemini model integration

## 📖 Documentation Sources

- **Liga ng mga Barangay Documents**: [Google Drive Folder](https://drive.google.com/drive/folders/1JmMuoMr6CswsphQVD10DG5UsTpBHYp6m)
- **Local Knowledge Base**: `utils/liga_documentation.md`
- **Language Support**: Filipino, English, Tag-lish with pattern-based detection

## 🤝 Support

For Liga ng mga Barangay specific queries, the chatbot provides:
- Official document-based answers with confidence scoring
- Barangay governance information from constitution and by-laws
- SK (Sangguniang Kabataan) election guidance
- Local government procedure explanations
- FAQ-based quick answers

---

**Built with ❤️ for Liga ng mga Barangay using Google ADK**
