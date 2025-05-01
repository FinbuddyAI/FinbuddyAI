# FinBuddyAI

FinBuddyAI is a AI-empowered personal finance management application with AI-powered insights and goal tracking/adjusting capabilities.

## Features

### Interactive Goal Setting
- MultiAgent-powered chat interface to help find and set personalized saving and spending goals
- Natural conversation flow for understanding your financial objectives
- Intelligent goal recommendations based on your spending patterns

### Smart Transaction Tracking
- Real-time transaction monitoring and categorization
- Automatic spending goal adjustments based on your transaction history
- Dynamic goal refinement to keep your financial targets realistic

### Proactive Financial Advice
- Personalized spending recommendations based on your habits
- Real-time notifications for important financial updates
- Slack integration for timely financial insights and alerts
- AI-driven suggestions for improving spending habits

The application combines these features to provide a comprehensive financial management experience, helping you stay on track with your financial goals while providing actionable insights for better financial decisions.

## Project Structure

```
finbuddy-ai/
├── backend/                 # FastAPI backend
│   ├── chat/               # Chat functionality
│   ├── goal_refine/        # Goal adjustment logic
│   ├── slack_bot/          # Slack integration
│   ├── utils/              # Utility functions
│   ├── main.py            # Main FastAPI application
│   ├── database.py        # Database configuration
│   └── requirements.txt   # Python dependencies
│
├── onboarding/             # User onboarding system
└── src/                    # React frontend
    ├── components/         # Reusable UI components
    ├── pages/             # Page components
    ├── services/          # API services
    └── App.js             # Main React application

```

## Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL
- OpenAI/Azure AI API key

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/FinbuddyAI.git
cd FinbuddyAI
```

2. Backend setup:
```bash
cd finbuddy-ai/backend
python -m venv env
source env/bin/activate  # On Windows: .\env\Scripts\activate
pip install -r requirements.txt
```

3. Frontend setup:
```bash
cd ../src
npm install
```

4. Environment setup:
- Create a `.env` file in the backend directory with:
```
DATABASE_URL=postgresql://username:password@localhost:5432/finbuddy
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_jwt_secret_key
```

## Running the Application

1. Start the backend:
```bash
cd finbuddy-ai/backend
uvicorn main:app --reload
```

2. Start the frontend (in a new terminal):
```bash
cd finbuddy-ai/src
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
