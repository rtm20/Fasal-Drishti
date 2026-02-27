import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Analyze from './pages/Analyze'
import Dashboard from './pages/Dashboard'
import About from './pages/About'
import WhatsAppDemo from './pages/WhatsAppDemo'
import WhatsAppConnect from './pages/WhatsAppConnect'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-[#0f0f1a] text-white">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/analyze" element={<Analyze />} />
          <Route path="/connect" element={<WhatsAppConnect />} />
          <Route path="/whatsapp" element={<WhatsAppDemo />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
