import { useState, useRef, useEffect } from 'react'
import { FaWhatsapp, FaPaperPlane, FaImage, FaCheck, FaCheckDouble } from 'react-icons/fa'
import { FiPaperclip, FiCamera, FiSmile } from 'react-icons/fi'
import { analyzeImage } from '../utils/api'

const WELCOME_MSG = {
  from: 'bot',
  type: 'text',
  text: `🌱 *नमस्ते! FasalDrishti में आपका स्वागत है!*

मैं आपकी फसल की बीमारी पहचानने में मदद करता हूं।

📸 *कैसे इस्तेमाल करें:*
1. अपनी फसल की प्रभावित पत्ती की फोटो लें
2. इस नंबर पर भेजें
3. 30 सेकंड में पाएं:
   ✅ बीमारी की पहचान
   💊 इलाज की सलाह

🌾 *समर्थित फसलें:* टमाटर, धान, गेहूं, कपास, आलू, मिर्च, प्याज

📸 अभी फोटो भेजें और शुरू करें!`,
  time: formatTime(),
}

function formatTime(date) {
  const d = date || new Date()
  return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true })
}

function formatBotText(text) {
  // Simple WhatsApp-style bold *text* → <strong>
  return text
    .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
    .replace(/_(.*?)_/g, '<em>$1</em>')
    .replace(/\n/g, '<br/>')
}

export default function WhatsAppDemo() {
  const [messages, setMessages] = useState([WELCOME_MSG])
  const [inputText, setInputText] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const chatEndRef = useRef(null)
  const fileInputRef = useRef(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  const addMessage = (msg) => {
    setMessages(prev => [...prev, { ...msg, time: formatTime() }])
  }

  const handleSendText = () => {
    const text = inputText.trim()
    if (!text) return
    setInputText('')
    addMessage({ from: 'user', type: 'text', text })

    // Simulate bot response
    setIsTyping(true)
    setTimeout(() => {
      setIsTyping(false)
      const lower = text.toLowerCase()
      if (['hi', 'hello', 'namaste', 'हेलो', 'नमस्ते'].some(w => lower.includes(w))) {
        addMessage({
          from: 'bot',
          type: 'text',
          text: WELCOME_MSG.text,
        })
      } else if (['help', 'मदद', 'सहायता'].some(w => lower.includes(w))) {
        addMessage({
          from: 'bot',
          type: 'text',
          text: `🆘 *सहायता*

📸 *फोटो भेजने के टिप्स:*
• प्रभावित पत्ती को करीब से फोटो लें
• अच्छी रोशनी में फोटो लें
• पत्ती का आगे और पीछे दोनों तरफ भेजें

🗣️ *भाषा बदलें:*
'english' - English
'hindi' - हिंदी
'tamil' - தமிழ்

❓ समस्या हो तो 'support' टाइप करें`,
        })
      } else {
        addMessage({
          from: 'bot',
          type: 'text',
          text: `🤖 मैं आपकी फसल की बीमारी पहचानने में मदद करता हूं।

📸 कृपया अपनी *फसल की फोटो* भेजें।
या 'help' टाइप करें मदद के लिए।`,
        })
      }
    }, 1200)
  }

  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    const preview = URL.createObjectURL(file)
    addMessage({ from: 'user', type: 'image', preview, text: 'फसल की फोटो' })

    setIsTyping(true)

    try {
      const result = await analyzeImage(file, 'hi')
      setIsTyping(false)

      // Build WhatsApp-style response
      const sEmoji = {
        none: '🟢', mild: '🟡', moderate: '🟠', severe: '🔴'
      }
      const severity = result.severity || 'moderate'
      const emoji = sEmoji[severity] || '⚪'
      const confidence = result.confidence ? Math.round(result.confidence * 100) : 85

      let msg = `🌱 *FasalDrishti विश्लेषण परिणाम*\n\n`
      msg += `🔍 *बीमारी:* ${result.disease_name || result.disease}\n`
      if (result.hindi_name) msg += `   _${result.hindi_name}_\n`
      msg += `\n${emoji} *गंभीरता:* ${severity.toUpperCase()}\n`
      msg += `📊 *विश्वास स्तर:* ${confidence}%\n`

      if (result.description) {
        msg += `\n📝 *विवरण:*\n${result.description}\n`
      }

      if (result.treatments?.length > 0) {
        msg += `\n💊 *अनुशंसित उपचार:*\n`
        result.treatments.slice(0, 2).forEach((t, i) => {
          const name = typeof t === 'string' ? t : t.name
          msg += `${i + 1}. *${name}*\n`
          if (t.dosage) msg += `   └ खुराक: ${t.dosage}\n`
          if (t.cost) msg += `   └ खर्च: ${t.cost}\n`
        })
      }

      if (result.organic_treatments?.length > 0) {
        msg += `\n🌿 *जैविक विकल्प:*\n`
        result.organic_treatments.slice(0, 2).forEach(t => {
          msg += `• ${typeof t === 'string' ? t : t.name}\n`
        })
      }

      if (result.prevention?.length > 0) {
        msg += `\n🛡️ *बचाव के उपाय:*\n`
        result.prevention.slice(0, 3).forEach(p => {
          msg += `• ${p}\n`
        })
      }

      msg += `\n---\n📸 एक और फोटो भेजें या 'help' टाइप करें`

      addMessage({ from: 'bot', type: 'text', text: msg })
    } catch {
      setIsTyping(false)
      addMessage({
        from: 'bot',
        type: 'text',
        text: '🙏 माफ कीजिए, फोटो प्राप्त नहीं हो सकी। कृपया फिर से भेजें।',
      })
    }
  }

  return (
    <div className="min-h-screen bg-[#FFFDF7] text-[#1B3409] pt-20 pb-8 px-4">
      <div className="max-w-lg mx-auto">
        {/* Header info */}
        <div className="text-center mb-4">
          <h1 className="text-2xl font-bold mb-1 text-[#2E7D32]">
            WhatsApp Integration Demo
          </h1>
          <p className="text-[#7A8856] text-sm">
            Simulates how farmers interact with FasalDrishti via WhatsApp
          </p>
        </div>

        {/* Phone Frame */}
        <div className="rounded-3xl border-2 border-[#d4c5a0]/60 overflow-hidden shadow-xl max-w-md mx-auto">
          {/* WhatsApp Header */}
          <div className="bg-[#1f2c34] px-4 py-3 flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-green-600 flex items-center justify-center">
              <FaWhatsapp className="text-white text-xl" />
            </div>
            <div className="flex-1">
              <div className="text-white font-semibold text-sm">FasalDrishti Bot</div>
              <div className="text-green-400 text-xs">
                {isTyping ? 'typing…' : 'online'}
              </div>
            </div>
            <div className="flex gap-4 text-gray-400">
              <FiCamera className="text-lg" />
              <span className="text-lg">⋮</span>
            </div>
          </div>

          {/* Chat Area */}
          <div
            className="h-[480px] overflow-y-auto px-3 py-4 space-y-2"
            style={{
              background: `#0b141a url("data:image/svg+xml,%3Csvg width='60' height='60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h60v60H0z' fill='none'/%3E%3Cpath d='M30 5a2 2 0 100 4 2 2 0 000-4zM10 25a2 2 0 100 4 2 2 0 000-4zM50 25a2 2 0 100 4 2 2 0 000-4zM30 45a2 2 0 100 4 2 2 0 000-4z' fill='%23ffffff06'/%3E%3C/svg%3E")`,
            }}
          >
            {/* Date pill */}
            <div className="flex justify-center mb-2">
              <span className="px-3 py-1 rounded-lg bg-[#182229] text-gray-400 text-xs">
                TODAY
              </span>
            </div>

            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.from === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[85%] rounded-xl px-3 py-2 text-sm relative ${
                    msg.from === 'user'
                      ? 'bg-[#005c4b] text-white rounded-tr-none'
                      : 'bg-[#202c33] text-gray-100 rounded-tl-none'
                  }`}
                >
                  {msg.type === 'image' && msg.preview && (
                    <div className="mb-1.5 -mx-1 -mt-0.5">
                      <img
                        src={msg.preview}
                        alt="Crop"
                        className="rounded-lg w-full max-h-48 object-cover"
                      />
                    </div>
                  )}
                  <div
                    className="whitespace-pre-wrap leading-relaxed break-words"
                    dangerouslySetInnerHTML={{ __html: formatBotText(msg.text || '') }}
                  />
                  <div className={`flex items-center gap-1 justify-end mt-1 ${
                    msg.from === 'user' ? 'text-green-300/50' : 'text-gray-500'
                  } text-[10px]`}>
                    <span>{msg.time}</span>
                    {msg.from === 'user' && <FaCheckDouble className="text-blue-400" />}
                  </div>
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-[#202c33] rounded-xl rounded-tl-none px-4 py-3">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Input Area */}
          <div className="bg-[#1f2c34] px-2 py-2 flex items-center gap-2">
            <button className="text-gray-400 p-2 hover:text-white transition-colors bg-transparent border-none">
              <FiSmile className="text-xl" />
            </button>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="text-gray-400 p-2 hover:text-green-400 transition-colors bg-transparent border-none"
              title="Send crop image"
            >
              <FiPaperclip className="text-xl" />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
            />
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendText()}
              placeholder="Type a message"
              className="flex-1 bg-[#2a3942] rounded-full px-4 py-2 text-sm text-white placeholder-gray-500 outline-none border-none"
            />
            <button
              onClick={handleSendText}
              className="w-10 h-10 rounded-full bg-green-600 flex items-center justify-center text-white hover:bg-green-500 transition-colors border-none"
            >
              <FaPaperPlane className="text-sm" />
            </button>
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-6 space-y-3 max-w-md mx-auto">
          <div className="p-4 rounded-xl bg-[#25D366]/5 border border-[#25D366]/20">
            <h3 className="text-[#25D366] font-semibold text-sm mb-2">📱 Try It Out</h3>
            <ul className="text-[#7A8856] text-xs space-y-1.5 leading-relaxed">
              <li>• Click the <strong className="text-[#4A5726]">📎 paperclip</strong> icon to upload a crop leaf image</li>
              <li>• Type <strong className="text-[#4A5726]">"namaste"</strong> or <strong className="text-[#4A5726]">"help"</strong> for guided responses</li>
              <li>• AI will analyze the image and respond in <strong className="text-[#4A5726]">Hindi</strong> with disease info + treatment</li>
            </ul>
          </div>

          <div className="p-4 rounded-xl bg-white border border-[#d4c5a0]/40 shadow-sm">
            <h3 className="text-[#1B3409] font-semibold text-sm mb-2">🔗 Real WhatsApp Connection</h3>
            <p className="text-[#7A8856] text-xs leading-relaxed">
              This demo uses <strong className="text-[#4A5726]">Twilio WhatsApp Sandbox</strong> or <strong className="text-[#4A5726]">Meta Cloud API</strong> for real WhatsApp integration.
              Farmers send crop photos to the WhatsApp number and receive AI diagnosis in Hindi — no app install needed.
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              <span className="px-2 py-1 rounded bg-[#2E7D32]/10 text-[#2E7D32] text-[10px]">Twilio Sandbox</span>
              <span className="px-2 py-1 rounded bg-[#2E7D32]/10 text-[#2E7D32] text-[10px]">Meta Cloud API</span>
              <span className="px-2 py-1 rounded bg-[#D4A017]/10 text-[#D4A017] text-[10px]">Amazon Bedrock AI</span>
              <span className="px-2 py-1 rounded bg-[#795548]/10 text-[#795548] text-[10px]">Hindi Response</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
