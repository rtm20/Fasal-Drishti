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
    icon: <MdCameraAlt className="text-3xl text-[#2E7D32]" />,
    title: 'Snap & Detect',
    desc: 'Simply photograph a crop leaf and get instant AI-powered disease diagnosis with confidence scores.',
  },
  {
    icon: <FaWhatsapp className="text-3xl text-[#25D366]" />,
    title: 'WhatsApp Integration',
    desc: 'Send crop images via WhatsApp — no app download needed. Works on any phone farmers already own.',
  },
  {
    icon: <FaLanguage className="text-3xl text-[#D4A017]" />,
    title: '11 Indian Languages',
    desc: 'Receive treatment advice in Hindi, Tamil, Telugu, Kannada, Bengali and more regional languages.',
  },
  {
    icon: <MdLocalPharmacy className="text-3xl text-[#2E7D32]" />,
    title: 'Treatment Plans',
    desc: 'Get actionable treatment recommendations with exact dosage, organic alternatives, and cost estimates.',
  },
  {
    icon: <FaBrain className="text-3xl text-[#795548]" />,
    title: 'Powered by AI',
    desc: 'Amazon Bedrock Claude 3.5 Sonnet v2 vision model delivers expert-grade analysis from just a photograph.',
  },
  {
    icon: <MdSpeed className="text-3xl text-[#D4A017]" />,
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
    <div className="min-h-screen bg-[#FFFDF7] text-[#1B3409]">
      {/* Hero */}
      <section className="relative pt-32 pb-20 px-4 overflow-hidden">
        {/* Warm glow bg */}
        <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-[#2E7D32]/5 blur-[120px] pointer-events-none" />
        <div className="absolute top-40 right-1/4 w-[300px] h-[300px] rounded-full bg-[#D4A017]/8 blur-[100px] pointer-events-none" />

        <div className={`max-w-5xl mx-auto text-center relative z-10 transition-all duration-1000 ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-[#D4A017]/30 bg-[#D4A017]/10 text-[#8B6914] text-sm mb-6 font-medium">
            <FaSeedling className="text-[#2E7D32]" /> AI for Bharat Hackathon — Track&nbsp;03
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold leading-tight mb-6">
            <span className="text-[#2E7D32]">
              Instant Crop Disease Detection
            </span>
            <br />
            <span className="text-[#4A5726] text-3xl sm:text-4xl">
              for Every Indian Farmer 🌾
            </span>
          </h1>

          <p className="text-[#5a6b3c] max-w-2xl mx-auto text-lg mb-10 leading-relaxed">
            <strong className="text-[#1B3409]">FasalDrishti</strong> uses AI-powered image analysis to identify crop diseases in seconds — 
            accessible through <span className="text-[#25D366] font-semibold">WhatsApp</span> in <span className="text-[#D4A017] font-semibold">11 Indian languages</span>. 
            Get treatment advice with dosage, cost, and organic alternatives.
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link
              to="/connect"
              className="px-8 py-3 bg-[#25D366] text-white rounded-full text-lg font-semibold hover:bg-[#20bd5a] hover:shadow-lg transition-all no-underline flex items-center justify-center gap-2 shadow-md"
            >
              <FaWhatsapp /> Connect via WhatsApp
            </Link>
            <Link
              to="/analyze"
              className="px-8 py-3 bg-[#2E7D32] text-white rounded-full text-lg font-semibold hover:bg-[#1B5E20] hover:shadow-lg transition-all no-underline flex items-center justify-center gap-2 shadow-md"
            >
              🌿 Try Disease Detection
            </Link>
            <Link
              to="/dashboard"
              className="px-8 py-3 border-2 border-[#2E7D32]/30 text-[#2E7D32] rounded-full text-lg font-semibold hover:bg-[#2E7D32]/5 transition-all no-underline flex items-center justify-center gap-2"
            >
              📊 View Dashboard
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 border-y border-[#d4c5a0]/40 bg-[#F7F0E3]/50">
        <div className="max-w-5xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {stats.map(s => (
            <div key={s.label}>
              <div className="text-3xl font-bold text-[#2E7D32]">{s.value}</div>
              <div className="text-[#7A8856] text-sm mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4 text-[#1B3409]">How It Works</h2>
          <p className="text-[#7A8856] text-center mb-12 max-w-lg mx-auto">Three simple steps — no app download, no registration needed.</p>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: '1', emoji: '📸', title: 'Capture', desc: 'Take a photo of the affected crop leaf using your phone camera or WhatsApp.' },
              { step: '2', emoji: '🤖', title: 'Analyze', desc: 'Our AI engine identifies the disease, severity level, and confidence score in under 3 seconds.' },
              { step: '3', emoji: '💊', title: 'Treat', desc: 'Receive treatment plan with exact dosage, organic options, and cost estimates in your language.' },
            ].map(item => (
              <div key={item.step} className="relative p-6 rounded-2xl bg-white border border-[#d4c5a0]/40 text-center shadow-sm hover:shadow-md transition-shadow">
                <div className="text-4xl mb-4">{item.emoji}</div>
                <div className="text-xs text-[#D4A017] font-bold tracking-widest mb-2">STEP {item.step}</div>
                <h3 className="text-xl font-semibold mb-2 text-[#1B3409]">{item.title}</h3>
                <p className="text-[#7A8856] text-sm leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4 bg-[#F7F0E3]/40">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4 text-[#1B3409]">Key Features</h2>
          <p className="text-[#7A8856] text-center mb-12 max-w-lg mx-auto">Built specifically for smallholder farmers across rural India.</p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map(f => (
              <div key={f.title} className="p-6 rounded-2xl border border-[#d4c5a0]/40 hover:border-[#2E7D32]/30 transition-all bg-white shadow-sm hover:shadow-md">
                <div className="mb-4 w-12 h-12 rounded-xl bg-[#2E7D32]/5 flex items-center justify-center">{f.icon}</div>
                <h3 className="text-lg font-semibold mb-2 text-[#1B3409]">{f.title}</h3>
                <p className="text-[#7A8856] text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Crops & Languages */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-12">
          <div>
            <h3 className="text-2xl font-bold mb-6 text-[#1B3409]">Supported Crops</h3>
            <div className="flex flex-wrap gap-3">
              {crops.map(c => (
                <span key={c} className="px-4 py-2 rounded-full bg-[#2E7D32]/5 border border-[#2E7D32]/20 text-sm text-[#2E7D32] font-medium">{c}</span>
              ))}
            </div>
          </div>
          <div>
            <h3 className="text-2xl font-bold mb-6 text-[#1B3409]">Supported Languages</h3>
            <div className="flex flex-wrap gap-3">
              {languages.map(l => (
                <span key={l} className="px-4 py-2 rounded-full bg-[#D4A017]/5 border border-[#D4A017]/20 text-sm text-[#8B6914] font-medium">{l}</span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Tech stack */}
      <section className="py-20 px-4 bg-[#F7F0E3]/40">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4 text-[#1B3409]">Powered by AWS ☁️</h2>
          <p className="text-[#7A8856] mb-10 max-w-lg mx-auto">Enterprise-grade cloud infrastructure for reliable, scalable AI at the edge.</p>
          <div className="flex flex-wrap justify-center gap-4">
            {['Amazon Bedrock', 'Claude 3.5 Sonnet v2', 'Amazon Rekognition', 'Amazon S3', 'DynamoDB', 'API Gateway', 'Lambda', 'Amazon Translate', 'Amazon Polly', 'CloudWatch'].map(t => (
              <span key={t} className="px-5 py-2.5 rounded-xl bg-white border border-[#d4c5a0]/40 text-[#4A5726] text-sm font-medium shadow-sm">
                {t}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-4 text-center">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold mb-4 text-[#1B3409]">Ready to Protect Your Crops? 🌱</h2>
          <p className="text-[#7A8856] mb-8">Connect on WhatsApp — send a crop photo, get AI diagnosis in Hindi. No app needed.</p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link
              to="/connect"
              className="inline-flex items-center gap-3 px-10 py-4 bg-[#25D366] text-white rounded-full text-lg font-bold hover:bg-[#20bd5a] transition-all no-underline shadow-lg"
            >
              <FaWhatsapp className="text-2xl" /> Connect on WhatsApp
            </Link>
            <Link
              to="/analyze"
              className="inline-flex items-center gap-2 px-10 py-4 bg-[#2E7D32] text-white rounded-full text-lg font-semibold hover:bg-[#1B5E20] transition-all no-underline shadow-lg"
            >
              🌿 Analyze a Crop Image
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#d4c5a0]/40 py-8 px-4 text-center text-[#7A8856] text-sm bg-[#F7F0E3]/30">
        <div className="flex items-center justify-center gap-2 mb-2">
          <FaSeedling className="text-[#2E7D32]" />
          <span className="font-semibold text-[#1B3409]">FasalDrishti</span>
        </div>
        <p>AI for Bharat Hackathon 2026 — Track 03: Rural Innovation & Sustainable Systems</p>
        <p className="mt-1">Built with ❤️ for Indian farmers using Amazon Web Services</p>
      </footer>
    </div>
  )
}
