import ReactMarkdown from 'react-markdown'
import { useEffect, useState } from "react";

function App() {
  const [msg, setMsg] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/api/generate_response", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({"prompt": "Why is the sky blue"})
    })
      .then(res => res.json())
      .then(data => setMsg(data.text));
  }, []);

  return <ReactMarkdown>{msg}</ReactMarkdown>;
}

export default App;
