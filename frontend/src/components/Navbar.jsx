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
    <nav className="fixed top-0 w-full z-50 bg-[#0f0f1a]/90 backdrop-blur-md border-b border-green-900/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 no-underline">
            <FaSeedling className="text-2xl text-green-400" />
            <span className="text-xl font-bold bg-gradient-to-r from-green-400 to-emerald-300 bg-clip-text text-transparent">
              FasalDrishti
            </span>
          </Link>

          {/* Desktop links */}
          <div className="hidden md:flex items-center gap-8">
            {links.map(link => (
              <Link
                key={link.path}
                to={link.path}
                className={`text-sm font-medium transition-colors no-underline ${
                  location.pathname === link.path
                    ? 'text-green-400'
                    : 'text-gray-300 hover:text-green-400'
                }`}
              >
                {link.label}
              </Link>
            ))}
            <Link
              to="/analyze"
              className="px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-500 text-white rounded-full text-sm font-semibold hover:shadow-lg hover:shadow-green-500/30 transition-all no-underline"
            >
              🔬 Scan Crop
            </Link>
          </div>

          {/* Mobile burger */}
          <button
            onClick={() => setOpen(!open)}
            className="md:hidden text-gray-300 text-xl bg-transparent border-none"
          >
            {open ? <FiX /> : <FiMenu />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="md:hidden bg-[#0f0f1a] border-t border-green-900/30 px-4 pb-4">
          {links.map(link => (
            <Link
              key={link.path}
              to={link.path}
              onClick={() => setOpen(false)}
              className={`block py-3 text-sm font-medium no-underline ${
                location.pathname === link.path ? 'text-green-400' : 'text-gray-300'
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  )
}
