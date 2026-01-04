import ReactMarkdown from 'react-markdown'
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import { useState } from "react";
import '@fontsource/roboto/700.css';

function App() {
  const [request, setRequest] = useState("");
  const [response, setResponse] = useState("");
  const [sent, setSent] = useState(false)
  const [graph, setGraph] = useState("1D")
  
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
    
    setSent(true)
  };

  return (
    <div className="App">
      <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", mt: 2 }}>
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <TextField 
            label="stock" 
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
        <Box sx={{ mt: 1, mb: 1 }}>
          {sent && <ButtonGroup variant="contained" aria-label="Basic button group">
            <Button onClick={() => setGraph("1D")}>1D</Button>
            <Button onClick={() => setGraph("1W")}>1W</Button>
            <Button onClick={() => setGraph("1M")}>1M</Button>
          </ButtonGroup>}
        </Box>
        <Box>
          {sent && graph==="1D" && <img src="/1D-Graph.jpg" alt="Graph of stock data for the past day" />}
          {sent && graph==="5D" && <img src="/5D-Graph.jpg" alt="Graph of stock data for the past 5 days" />}
          {sent && graph==="1M" && <img src="/1M-Graph.jpg" alt="Graph of stock data for the past month" />}
        </Box>
      </Box>
    </div>
  );
}

export default App;
