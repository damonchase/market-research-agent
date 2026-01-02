# Market Research Agent

This project is a web-based application that provides stock research using live web access. It consists of a FastAPI backend and a React frontend. The backend integrates with the Google GenAI API to generate stock recommendations based on user input.

## Features

- **Stock Research**: Users can input a stock name, and the application will fetch relevant information and provide a recommendation on whether it's a good time to buy the stock.
- **Live Web Access**: The backend uses a `web_search` tool to fetch up-to-date information about the stock.
- **Interactive UI**: A simple and intuitive React-based frontend for user interaction.

---

## Project Structure

### Backend (`server`)

- **Framework**: FastAPI
- **Key Dependencies**:
    - `fastapi`
    - `pydantic`
    - `google-genai`
    - `python-dotenv`
- **Endpoint**:
    - `POST /api/generate_response`: Accepts a stock name as input and returns a recommendation.
- **Environment Variables**:
    - `GEMINI_API_KEY`: API key for Google GenAI.

### Frontend (`client`)

- **Framework**: React
- **Key Dependencies**:
    - `react-markdown`
    - `@mui/material`
- **Features**:
    - Input field for stock name.
    - Markdown-rendered response display.

---

## Installation

### Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the `server` directory:
     ```bash
     cd server
     ```
2. Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
3. Create a `.env` file and add your `GEMINI_API_KEY`:
     ```env
     GEMINI_API_KEY=your_api_key_here
     ```
4. Run the FastAPI server:
     ```bash
     uvicorn app.main:app --reload
     ```

### Frontend Setup

1. Navigate to the `client` directory:
     ```bash
     cd client
     ```
2. Install dependencies:
     ```bash
     npm install
     ```
3. Start the React development server:
     ```bash
     npm start
     ```

---

## Usage

1. Start both the backend and frontend servers.
2. Open the frontend in your browser (default: `http://localhost:3000`).
3. Enter a stock name in the input field and click "Send".
4. View the generated response and recommendation.

---

## Example

### Input:
```
AAPL
```

### Output:
```
Apple Inc. (AAPL) is currently trading at $X.XX. Based on recent market trends and analysis, it is recommended to [buy/hold/sell] this stock.
```

---

## License

This project is licensed under the MIT License.

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Google GenAI](https://cloud.google.com/genai)
- [Material-UI](https://mui.com/)
- [dotenv](https://pypi.org/project/python-dotenv/)
- [React Markdown](https://github.com/remarkjs/react-markdown)