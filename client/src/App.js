import { Routes, Route } from "react-router-dom"
import Navbar from "./components/Navbar"
import Research from "./pages/Research"
import Articles from "./pages/Articles" 

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route index path="/" element={<Research />} />
        <Route path="/articles" element={<Articles />} />
      </Routes>
    </>
  );
}

export default App;
