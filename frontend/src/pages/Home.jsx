import { Link } from 'react-router-dom'
import { FaSeedling, FaWhatsapp, FaLanguage, FaBrain } from 'react-icons/fa'
import { MdCameraAlt, MdSpeed, MdLocalPharmacy } from 'react-icons/md'
import { useEffect, useState } from 'react'

const stats = [
  { value: '12+', label: 'Diseases Detected' },
  { value: '7', label: 'Crops Supported' },
  { value: '11', label: 'Indian Languages' },
  { value: '<3s', label: 'Detection Time' },
]

const features = [
  {
    icon: <MdCameraAlt className="text-3xl text-green-400" />,
    title: 'Snap & Detect',
    desc: 'Simply photograph a crop leaf and get instant AI-powered disease diagnosis with confidence scores.',
  },
  {
    icon: <FaWhatsapp className="text-3xl text-green-400" />,
    title: 'WhatsApp Integration',
    desc: 'Send crop images via WhatsApp — no app download needed. Works on any phone farmers already own.',
  },
  {
    icon: <FaLanguage className="text-3xl text-green-400" />,
    title: '11 Indian Languages',
    desc: 'Receive treatment advice in Hindi, Tamil, Telugu, Kannada, Bengali and more regional languages.',
  },
  {
    icon: <MdLocalPharmacy className="text-3xl text-green-400" />,
    title: 'Treatment Plans',
    desc: 'Get actionable treatment recommendations with exact dosage, organic alternatives, and cost estimates.',
  },
  {
    icon: <FaBrain className="text-3xl text-green-400" />,
    title: 'Powered by AI',
    desc: 'Amazon Bedrock Claude 3.5 Sonnet v2 vision model delivers expert-grade analysis from just a photograph.',
  },
  {
    icon: <MdSpeed className="text-3xl text-green-400" />,
    title: 'Works Offline-First',
    desc: 'Lightweight design optimized for low-bandwidth rural networks with minimal data usage.',
  },
]

const crops = ['🍅 Tomato', '🌾 Rice', '🌾 Wheat', '🧶 Cotton', '🥔 Potato', '🌶️ Chili', '🧅 Onion']

const languages = ['Hindi', 'Tamil', 'Telugu', 'Kannada', 'Bengali', 'Marathi', 'Gujarati', 'Punjabi', 'Malayalam', 'Odia', 'Assamese']

export default function Home() {
  const [visible, setVisible] = useState(false)
  useEffect(() => { setVisible(true) }, [])

  return (
    <div className="min-h-screen bg-[#0a0a14] text-white">
      {/* Hero */}
      <section className="relative pt-32 pb-20 px-4 overflow-hidden">
        {/* Glow bg */}
        <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-green-500/10 blur-[120px] pointer-events-none" />

        <div className={`max-w-5xl mx-auto text-center relative z-10 transition-all duration-1000 ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-green-500/30 bg-green-500/10 text-green-400 text-sm mb-6">
            <FaSeedling /> AI for Bharat Hackathon — Track&nbsp;03
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold leading-tight mb-6">
            <span className="bg-gradient-to-r from-green-400 via-emerald-300 to-teal-400 bg-clip-text text-transparent">
              Instant Crop Disease Detection
            </span>
            <br />
            <span className="text-gray-200 text-3xl sm:text-4xl">
              for Every Indian Farmer
            </span>
          </h1>

          <p className="text-gray-400 max-w-2xl mx-auto text-lg mb-10 leading-relaxed">
            <strong className="text-white">FasalDrishti</strong> uses AI-powered image analysis to identify crop diseases in seconds — 
            accessible through <span className="text-green-400">WhatsApp</span> in <span className="text-green-400">11 Indian languages</span>. 
            Get treatment advice with dosage, cost, and organic alternatives.
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link
              to="/connect"
              className="px-8 py-3 bg-[#25D366] text-white rounded-full text-lg font-semibold hover:shadow-xl hover:shadow-green-500/30 transition-all no-underline flex items-center justify-center gap-2"
            >
              <FaWhatsapp /> Connect via WhatsApp
            </Link>
            <Link
              to="/analyze"
              className="px-8 py-3 bg-gradient-to-r from-green-600 to-emerald-500 text-white rounded-full text-lg font-semibold hover:shadow-xl hover:shadow-green-500/30 transition-all no-underline flex items-center justify-center gap-2"
            >
              🔬 Try Disease Detection
            </Link>
            <Link
              to="/dashboard"
              className="px-8 py-3 border border-green-500/30 text-green-400 rounded-full text-lg font-semibold hover:bg-green-500/10 transition-all no-underline flex items-center justify-center gap-2"
            >
              📊 View Dashboard
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 border-y border-green-900/20">
        <div className="max-w-5xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {stats.map(s => (
            <div key={s.label}>
              <div className="text-3xl font-bold text-green-400">{s.value}</div>
              <div className="text-gray-400 text-sm mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">How It Works</h2>
          <p className="text-gray-400 text-center mb-12 max-w-lg mx-auto">Three simple steps — no app download, no registration needed.</p>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: '1', emoji: '📸', title: 'Capture', desc: 'Take a photo of the affected crop leaf using your phone camera or WhatsApp.' },
              { step: '2', emoji: '🤖', title: 'Analyze', desc: 'Our AI engine identifies the disease, severity level, and confidence score in under 3 seconds.' },
              { step: '3', emoji: '💊', title: 'Treat', desc: 'Receive treatment plan with exact dosage, organic options, and cost estimates in your language.' },
            ].map(item => (
              <div key={item.step} className="relative p-6 rounded-2xl bg-gradient-to-b from-green-900/20 to-transparent border border-green-900/30 text-center">
                <div className="text-4xl mb-4">{item.emoji}</div>
                <div className="text-xs text-green-500 font-bold tracking-widest mb-2">STEP {item.step}</div>
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4 bg-[#0d0d1a]">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">Key Features</h2>
          <p className="text-gray-400 text-center mb-12 max-w-lg mx-auto">Built specifically for smallholder farmers across rural India.</p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map(f => (
              <div key={f.title} className="p-6 rounded-2xl border border-green-900/20 hover:border-green-500/30 transition-colors bg-[#0f0f1a]">
                <div className="mb-4">{f.icon}</div>
                <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Crops & Languages */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-12">
          <div>
            <h3 className="text-2xl font-bold mb-6">Supported Crops</h3>
            <div className="flex flex-wrap gap-3">
              {crops.map(c => (
                <span key={c} className="px-4 py-2 rounded-full bg-green-900/30 border border-green-700/30 text-sm">{c}</span>
              ))}
            </div>
          </div>
          <div>
            <h3 className="text-2xl font-bold mb-6">Supported Languages</h3>
            <div className="flex flex-wrap gap-3">
              {languages.map(l => (
                <span key={l} className="px-4 py-2 rounded-full bg-emerald-900/30 border border-emerald-700/30 text-sm">{l}</span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Tech stack */}
      <section className="py-20 px-4 bg-[#0d0d1a]">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Powered by AWS</h2>
          <p className="text-gray-400 mb-10 max-w-lg mx-auto">Enterprise-grade cloud infrastructure for reliable, scalable AI at the edge.</p>
          <div className="flex flex-wrap justify-center gap-4">
            {['Amazon Bedrock', 'Claude 3.5 Sonnet v2', 'Amazon S3', 'DynamoDB', 'API Gateway', 'Lambda', 'Amazon Translate', 'Amazon Polly', 'CloudWatch'].map(t => (
              <span key={t} className="px-5 py-2.5 rounded-xl bg-[#0f0f1a] border border-gray-700/50 text-gray-300 text-sm font-medium">
                {t}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-4 text-center">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold mb-4">Ready to Protect Your Crops?</h2>
          <p className="text-gray-400 mb-8">Connect on WhatsApp — send a crop photo, get AI diagnosis in Hindi. No app needed.</p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link
              to="/connect"
              className="inline-flex items-center gap-3 px-10 py-4 bg-[#25D366] text-white rounded-full text-lg font-bold hover:bg-[#20bd5a] transition-all no-underline shadow-lg shadow-green-500/20"
            >
              <FaWhatsapp className="text-2xl" /> Connect on WhatsApp
            </Link>
            <Link
              to="/analyze"
              className="inline-flex items-center gap-2 px-10 py-4 bg-gradient-to-r from-green-600 to-emerald-500 text-white rounded-full text-lg font-semibold hover:shadow-xl hover:shadow-green-500/30 transition-all no-underline"
            >
              🔬 Analyze a Crop Image
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-green-900/20 py-8 px-4 text-center text-gray-500 text-sm">
        <div className="flex items-center justify-center gap-2 mb-2">
          <FaSeedling className="text-green-500" />
          <span className="font-semibold text-gray-300">FasalDrishti</span>
        </div>
        <p>AI for Bharat Hackathon 2026 — Track 03: Rural Innovation & Sustainable Systems</p>
        <p className="mt-1">Built with ❤️ for Indian farmers using Amazon Web Services</p>
      </footer>
    </div>
  )
}
