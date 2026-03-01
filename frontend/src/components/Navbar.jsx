import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { FiMenu, FiX } from 'react-icons/fi'
import { FaSeedling } from 'react-icons/fa'

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const location = useLocation()

  const links = [
    { path: '/', label: 'Home' },
    { path: '/analyze', label: 'Analyze' },
    { path: '/connect', label: 'WhatsApp' },
    { path: '/whatsapp', label: 'Demo' },
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/about', label: 'About' },
  ]

  return (
    <nav className="fixed top-0 w-full z-50 bg-[#FFFDF7]/95 backdrop-blur-md border-b border-[#d4c5a0]/50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 no-underline">
            <div className="w-9 h-9 rounded-full bg-[#2E7D32] flex items-center justify-center shadow-sm">
              <FaSeedling className="text-white text-lg" />
            </div>
            <span className="text-xl font-bold text-[#2E7D32]">
              Fasal<span className="text-[#D4A017]">Drishti</span>
            </span>
          </Link>

          {/* Desktop links */}
          <div className="hidden md:flex items-center gap-1">
            {links.map(link => (
              <Link
                key={link.path}
                to={link.path}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors no-underline ${
                  location.pathname === link.path
                    ? 'bg-[#2E7D32]/10 text-[#2E7D32] font-semibold'
                    : 'text-[#4A5726] hover:bg-[#2E7D32]/5 hover:text-[#2E7D32]'
                }`}
              >
                {link.label}
              </Link>
            ))}
            <Link
              to="/analyze"
              className="ml-2 px-5 py-2 bg-[#2E7D32] text-white rounded-full text-sm font-semibold hover:bg-[#1B5E20] transition-all no-underline shadow-sm"
            >
              🌾 Scan Crop
            </Link>
          </div>

          {/* Mobile burger */}
          <button
            onClick={() => setOpen(!open)}
            className="md:hidden text-[#2E7D32] text-xl bg-transparent border-none"
          >
            {open ? <FiX /> : <FiMenu />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="md:hidden bg-[#FFFDF7] border-t border-[#d4c5a0]/30 px-4 pb-4">
          {links.map(link => (
            <Link
              key={link.path}
              to={link.path}
              onClick={() => setOpen(false)}
              className={`block py-3 px-3 rounded-lg text-sm font-medium no-underline ${
                location.pathname === link.path
                  ? 'bg-[#2E7D32]/10 text-[#2E7D32]'
                  : 'text-[#4A5726] hover:bg-[#2E7D32]/5'
              }`}
            >
              {link.label}
            </Link>
          ))}
          <Link
            to="/analyze"
            onClick={() => setOpen(false)}
            className="block text-center mt-2 px-5 py-2.5 bg-[#2E7D32] text-white rounded-full text-sm font-semibold no-underline"
          >
            🌾 Scan Crop
          </Link>
        </div>
      )}
    </nav>
  )
}
