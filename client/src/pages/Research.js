import ReactMarkdown from 'react-markdown'
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import Box from '@mui/material/Box';
import { useState } from "react";
import '@fontsource/roboto/700.css';
import "./../styles/Research.css"

function Research() {
  const [request, setRequest] = useState("");
  const [response, setResponse] = useState("");
  const [sent, setSent] = useState(false);
  const [graph, setGraph] = useState("5d");
  const [loading, setLoading] = useState(false);
  const [imageData, setImageData] = useState(null);

  const handleSend = async (e) => {
    if (e) e.preventDefault();
    if (!request.trim()) return; // Don't send empty requests

    setLoading(true);

    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL}/api/generate_response`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ "prompt": request })
      });

      if (!res.ok) {
        throw new Error(`Server responded with ${res.status}`);
      }

      const data = await res.json();
      setResponse(data.text);
      setImageData(data.image_data)
      setSent(true);
    } catch (error) {
      console.error("Failed to fetch data:", error);
      setResponse("### Error\nFailed to reach the backend. Please check your connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#0B1120', pt: 6, px: 2 }}>
      <Box className="Research" sx={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        
        {/* Search Bar Container */}
        <Box 
          component="form" 
          onSubmit={handleSend} 
          sx={{ 
            display: "flex", 
            alignItems: "center",
            p: "6px 12px",
            bgcolor: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '12px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            transition: 'border 0.3s ease',
            '&:focus-within': {
              border: '1px solid #3b82f6'
            }
          }}
        >
          <input 
            type="text"
            placeholder="Company Name or Ticker"
            value={request} 
            onChange={(e) => setRequest(e.target.value)}
            className="custom-input"
          />
          <Button 
            type="submit" 
            variant="contained" 
            disabled={loading}
            sx={{ 
              ml: 1, 
              bgcolor: '#3b82f6', 
              fontWeight: 'bold',
              textTransform: 'none',
              borderRadius: '8px',
              boxShadow: '0 0 15px rgba(59, 130, 246, 0.4)',
              '&:hover': {
                bgcolor: '#2563eb',
                boxShadow: '0 0 20px rgba(59, 130, 246, 0.6)',
              }
            }}
          >
            {loading ? "..." : "Analyze"}
          </Button>
        </Box>

        {/* AI Response Display */}
        {response && (
          <Box sx={{ 
            mt: 4, 
            width: '100%', 
            maxWidth: '700px', 
            color: '#e2e8f0', 
            bgcolor: 'rgba(30, 41, 59, 0.5)',
            p: 4,
            borderRadius: '20px',
            border: '1px solid rgba(255, 255, 255, 0.05)',
            lineHeight: 1.6
          }}>
            <ReactMarkdown>{response}</ReactMarkdown>
          </Box>
        )}

        {/* Graph Selection Buttons */}
        {sent && (
          <Box sx={{ mt: 4, mb: 1 }}>
            <ButtonGroup variant="outlined">
              {["5d", "1mo", "6mo"].map((range) => (
                <Button 
                  key={range}
                  onClick={() => setGraph(range)}
                  sx={{ 
                    borderColor: 'rgba(255, 255, 255, 0.1)', 
                    color: graph === range ? '#3b82f6' : '#94a3b8',
                    bgcolor: graph === range ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                    '&:hover': { borderColor: '#3b82f6' }
                  }}
                >
                  {range}
                </Button>
              ))}
            </ButtonGroup>
          </Box>
        )}

        {/* Dynamic Image Display */}
        <Box sx={{ mt: 2 }}>
          {sent && (
            <img 
              className="graph-image" 
              src={imageData} 
              alt={`Stock data for ${graph}`} 
            />
          )}
        </Box>

      </Box>
    </Box>
  );
}

export default Research;