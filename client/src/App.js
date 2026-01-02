import ReactMarkdown from 'react-markdown'
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import { useState } from "react";

function App() {
  const [request, setRequest] = useState("");
  const [response, setResponse] = useState("");

  const handleSend = async () => {
    const res = await fetch("http://localhost:8000/api/generate_response", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({"prompt": request})
    })
    const data = await res.json()
        setResponse(data.text)
  };

  return (
    <div className="App">
      <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", mt: 2 }}>
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <TextField 
            label="search" 
            variant="outlined" 
            value={request} 
            onChange={(e) => setRequest(e.target.value)}
          />
          <Button onClick={handleSend} variant="contained" sx={{ ml: 1 }}>
            Send
          </Button>
        </Box>

        <Box sx={{ mt: 2, width: '100%', maxWidth: '600px' }}>
          <ReactMarkdown>{response}</ReactMarkdown>
        </Box>
      </Box>
    </div>
  );
}

export default App;
