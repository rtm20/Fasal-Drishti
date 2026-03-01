import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FaWhatsapp, FaQrcode, FaCheckCircle, FaSeedling, FaArrowRight } from 'react-icons/fa'
import { MdCameraAlt, MdTranslate, MdLocalPharmacy } from 'react-icons/md'

// Hardcoded fallback so the page works as a static site without backend
const FALLBACK_INFO = {
  wa_me_link: 'https://wa.me/14155238886?text=join%20sky-shadow',
  qr_code_url: 'https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=https://wa.me/14155238886?text=join%20sky-shadow',
  whatsapp_number_display: '+1 415 523 8886',
  is_sandbox: true,
}

export default function WhatsAppConnect() {
  const [connectInfo, setConnectInfo] = useState(FALLBACK_INFO)
  const [loading, setLoading] = useState(false)
  const [showQR, setShowQR] = useState(true)

  useEffect(() => {
    fetch('/api/whatsapp/connect')
      .then(r => r.json())
      .then(data => { setConnectInfo(data) })
      .catch(() => { /* use fallback */ })
  }, [])

  const info = connectInfo
  const waLink = info?.wa_me_link || FALLBACK_INFO.wa_me_link
  const qrUrl = info?.qr_code_url || FALLBACK_INFO.qr_code_url
  const phoneDisplay = info?.whatsapp_number_display || FALLBACK_INFO.whatsapp_number_display
  const isSandbox = info?.is_sandbox ?? true

  const steps = isSandbox
    ? [
        { num: '1', icon: '📱', title: 'Open WhatsApp', desc: 'Click the green button below or scan the QR code to open a chat with FasalDrishti.' },
        { num: '2', icon: '🔗', title: 'Join Sandbox', desc: 'If prompted, send the join code (e.g. "join <code>") shown in the chat. This is a one-time step for the demo.' },
        { num: '3', icon: '📸', title: 'Send Crop Photo', desc: 'Take a photo of an affected crop leaf and send it in the chat.' },
        { num: '4', icon: '🤖', title: 'Get AI Diagnosis', desc: 'In ~30 seconds, receive disease name, severity, treatment plan with dosage — all in Hindi!' },
      ]
    : [
        { num: '1', icon: '📱', title: 'Scan QR or Click Link', desc: 'Use the QR code or tap the button below to open WhatsApp chat with FasalDrishti.' },
        { num: '2', icon: '👋', title: 'Say Namaste', desc: 'Send "namaste" or "hi" to get a welcome message with instructions.' },
        { num: '3', icon: '📸', title: 'Send Crop Photo', desc: 'Photograph the affected leaf and send it. AI analysis starts instantly.' },
        { num: '4', icon: '💊', title: 'Receive Treatment', desc: 'Get disease identification + organic & chemical treatment options in your language.' },
      ]

  return (
    <div className="min-h-screen bg-[#FFFDF7] text-[#1B3409] pt-24 pb-16">
      {/* Hero */}
      <div className="max-w-4xl mx-auto px-4 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-[#25D366]/30 bg-[#25D366]/10 text-[#25D366] text-sm mb-6">
          <FaWhatsapp /> Connect via WhatsApp
        </div>

        <h1 className="text-3xl sm:text-5xl font-extrabold mb-4 text-[#2E7D32]">
          Start Using FasalDrishti
        </h1>
        <p className="text-[#7A8856] max-w-xl mx-auto text-lg mb-10">
          No app download. No registration. Just open WhatsApp, send a crop photo, and get instant AI diagnosis in Hindi.
        </p>
      </div>

      {/* Connection Card */}
      <div className="max-w-4xl mx-auto px-4">
        <div className="grid md:grid-cols-2 gap-8 mb-16">
          {/* QR Code Side */}
          <div className="bg-white rounded-3xl border border-[#d4c5a0]/50 p-8 text-center flex flex-col items-center justify-center shadow-md">
            <div className="flex items-center gap-2 text-[#2E7D32] font-semibold mb-6">
              <FaQrcode className="text-xl" />
              <span>Scan to Connect</span>
            </div>

            {qrUrl && (
              <div className="bg-[#F7F0E3] rounded-2xl p-4 inline-block mb-6 shadow-sm">
                <img
                  src={qrUrl}
                  alt="WhatsApp QR Code"
                  className="w-56 h-56"
                  onError={(e) => { e.target.style.display = 'none' }}
                />
              </div>
            )}

            <p className="text-[#a0ad8a] text-sm mb-2">or tap the button below on mobile</p>

            <a
              href={waLink}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-3 px-8 py-4 bg-[#25D366] text-white rounded-full text-lg font-bold hover:bg-[#20bd5a] transition-all no-underline shadow-lg"
            >
              <FaWhatsapp className="text-2xl" />
              Chat on WhatsApp
            </a>

            <p className="text-[#a0ad8a] text-xs mt-4">{phoneDisplay}</p>
          </div>

          {/* Steps Side */}
          <div className="flex flex-col gap-4">
            <h2 className="text-xl font-bold text-[#1B3409] mb-2">How to Connect</h2>
            {steps.map((step) => (
              <div
                key={step.num}
                className="flex gap-4 p-4 rounded-xl bg-white border border-[#d4c5a0]/40 hover:border-[#2E7D32]/30 transition-colors shadow-sm"
              >
                <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-[#2E7D32]/10 flex items-center justify-center text-xl">
                  {step.icon}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[#2E7D32] text-xs font-bold">STEP {step.num}</span>
                    <span className="text-[#1B3409] font-semibold text-sm">{step.title}</span>
                  </div>
                  <p className="text-[#7A8856] text-sm mt-1 leading-relaxed">{step.desc}</p>
                </div>
              </div>
            ))}

            {isSandbox && (
              <div className="p-4 rounded-xl bg-[#D4A017]/5 border border-[#D4A017]/20 mt-2">
                <p className="text-[#D4A017] text-xs font-semibold mb-1">⚡ Demo Mode (Twilio Sandbox)</p>
                <p className="text-[#7A8856] text-xs leading-relaxed">
                  The sandbox requires a one-time join code. In production, users simply message the number directly — no join step needed.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* What You Can Do */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-center text-[#1B3409] mb-8">What You Can Do</h2>
          <div className="grid sm:grid-cols-3 gap-6">
            {[
              {
                icon: <MdCameraAlt className="text-3xl text-[#2E7D32]" />,
                title: 'Send Crop Photo',
                desc: 'Photograph any affected leaf, fruit, or stem. AI identifies the disease with confidence score.',
                example: '📸 Send a photo of a tomato leaf →',
              },
              {
                icon: <MdTranslate className="text-3xl text-[#D4A017]" />,
                title: 'Get Hindi Response',
                desc: 'All diagnosis and treatment advice is delivered in Hindi with easy-to-understand language.',
                example: '"बीमारी: Leaf Rust (पत्ती का रतुआ)"',
              },
              {
                icon: <MdLocalPharmacy className="text-3xl text-[#795548]" />,
                title: 'Treatment + Cost',
                desc: 'Receive exact dosage, application method, cost per acre, and organic alternatives.',
                example: '"Mancozeb 75% WP — ₹350/एकड़"',
              },
            ].map((item) => (
              <div
                key={item.title}
                className="p-6 rounded-2xl bg-white border border-[#d4c5a0]/40 text-center shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex justify-center mb-4">{item.icon}</div>
                <h3 className="font-semibold text-lg text-[#1B3409] mb-2">{item.title}</h3>
                <p className="text-[#7A8856] text-sm leading-relaxed mb-3">{item.desc}</p>
                <div className="px-3 py-2 rounded-lg bg-[#2E7D32]/5 border border-[#2E7D32]/10 text-xs text-[#2E7D32] italic">
                  {item.example}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Supported Commands */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-center text-[#1B3409] mb-8">Supported Commands</h2>
          <div className="max-w-lg mx-auto space-y-3">
            {(info?.supported_commands || [
              { command: 'namaste / hi / hello', desc: 'Get welcome message & instructions' },
              { command: 'help / मदद', desc: 'Get usage tips & language options' },
              { command: '📸 Send photo', desc: 'Get AI disease diagnosis + treatment plan' },
            ]).map((cmd, i) => (
              <div
                key={i}
                className="flex items-center gap-4 p-4 rounded-xl bg-white border border-[#d4c5a0]/40 shadow-sm"
              >
                <div className="px-3 py-1.5 rounded-lg bg-[#2E7D32]/10 text-[#2E7D32] text-sm font-mono font-bold whitespace-nowrap">
                  {cmd.command}
                </div>
                <FaArrowRight className="text-[#D4A017] text-xs flex-shrink-0" />
                <span className="text-[#4A5726] text-sm">{cmd.desc}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Demo video / screenshot placeholder */}
        <div className="mb-16 text-center">
          <h2 className="text-2xl font-bold text-[#1B3409] mb-6">See It In Action</h2>
          <div className="inline-block bg-white rounded-3xl border border-[#d4c5a0]/50 p-8 shadow-md">
            <div className="flex flex-col sm:flex-row items-center gap-6">
              <div className="text-left max-w-xs">
                <p className="text-[#1B3409] font-semibold mb-2">Live WhatsApp Demo</p>
                <p className="text-[#7A8856] text-sm leading-relaxed mb-4">
                  Try the interactive simulator to see exactly how the conversation flows — or connect via real WhatsApp above.
                </p>
                <Link
                  to="/whatsapp"
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-[#25D366]/15 text-[#25D366] border border-[#25D366]/30 text-sm font-semibold hover:bg-[#25D366]/25 transition-all no-underline"
                >
                  <FaWhatsapp /> Try Simulator
                </Link>
              </div>
              <div className="w-48 h-80 rounded-2xl bg-[#F7F0E3] border border-[#d4c5a0]/40 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-4xl mb-2">📱</div>
                  <p className="text-[#2E7D32] text-xs font-medium">WhatsApp Chat</p>
                  <p className="text-[#a0ad8a] text-[10px]">Simulator →</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Production Vision */}
        <div className="max-w-2xl mx-auto text-center mb-16">
          <h2 className="text-2xl font-bold text-[#1B3409] mb-4">Production Vision</h2>
          <p className="text-[#7A8856] text-sm leading-relaxed mb-8">
            In production, FasalDrishti will have a <strong className="text-[#1B3409]">dedicated WhatsApp Business number</strong>. 
            Farmers discover the service through:
          </p>
          <div className="grid sm:grid-cols-2 gap-4 text-left">
            {[
              { icon: '🏪', title: 'Local Agri Shops', desc: 'QR code posters at fertilizer/seed shops across villages' },
              { icon: '📻', title: 'Community Radio', desc: 'WhatsApp number announced on local FM radio' },
              { icon: '👨‍🌾', title: 'Gram Panchayat', desc: 'Village leaders share the number during farmer meetings' },
              { icon: '📱', title: 'wa.me Link', desc: 'One-click link shared via SMS, Facebook groups, YouTube' },
            ].map((ch) => (
              <div key={ch.title} className="flex gap-3 p-4 rounded-xl bg-white border border-[#d4c5a0]/40 shadow-sm">
                <span className="text-2xl">{ch.icon}</span>
                <div>
                  <h4 className="font-semibold text-sm text-[#1B3409]">{ch.title}</h4>
                  <p className="text-[#7A8856] text-xs mt-1">{ch.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="text-center">
          <a
            href={waLink}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-3 px-10 py-4 bg-[#25D366] text-white rounded-full text-lg font-bold hover:bg-[#20bd5a] transition-all no-underline shadow-lg"
          >
            <FaWhatsapp className="text-2xl" />
            Start Chatting with FasalDrishti
          </a>
          <p className="text-[#a0ad8a] text-xs mt-3">Free • No download • Works on any phone</p>
        </div>
      </div>
    </div>
  )
}
