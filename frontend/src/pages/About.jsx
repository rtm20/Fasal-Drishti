import { FaSeedling, FaGithub, FaAws, FaWhatsapp } from 'react-icons/fa'
import { MdEmail } from 'react-icons/md'

const techStack = [
  {
    category: 'Frontend',
    items: ['React 19', 'Tailwind CSS v4', 'Recharts', 'Vite 8'],
  },
  {
    category: 'Backend',
    items: ['Python 3.13', 'FastAPI', 'Pydantic v2', 'Uvicorn'],
  },
  {
    category: 'AWS Services',
    items: ['Bedrock (Claude 3.5 Sonnet v2)', 'Rekognition', 'S3', 'DynamoDB', 'Lambda', 'API Gateway', 'Translate', 'Polly', 'CloudWatch'],
  },
  {
    category: 'Integration',
    items: ['WhatsApp Business API', 'Meta Cloud API', 'REST APIs'],
  },
]

const team = [
  { name: 'Team FasalDrishti', role: 'AI for Bharat Hackathon 2026', emoji: '🌱' },
]

export default function About() {
  return (
    <div className="min-h-screen bg-[#FFFDF7] text-[#1B3409] pt-24 pb-20 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 mb-4">
            <FaSeedling className="text-3xl text-[#2E7D32]" />
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold mb-4 text-[#2E7D32]">
            About FasalDrishti
          </h1>
          <p className="text-[#7A8856] max-w-2xl mx-auto leading-relaxed">
            An AI-powered crop disease detection platform built to empower 
            smallholder farmers across rural India with accessible, affordable, and 
            actionable agricultural intelligence.
          </p>
        </div>

        {/* Problem & Solution */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          <div className="p-6 rounded-2xl bg-red-50 border border-red-200/60 shadow-sm">
            <h3 className="text-lg font-bold text-red-600 mb-3">🔴 The Problem</h3>
            <ul className="space-y-2 text-[#4A5726] text-sm leading-relaxed">
              <li>• Indian farmers lose <strong className="text-[#1B3409]">₹50,000 crore+</strong> annually to crop diseases</li>
              <li>• 1 agricultural expert per <strong className="text-[#1B3409]">1,000+ farmers</strong> — severe shortage</li>
              <li>• 65% farmers have <strong className="text-[#1B3409]">no smartphone apps</strong> — only basic feature phones</li>
              <li>• Disease misidentification leads to <strong className="text-[#1B3409]">wrong pesticide usage</strong></li>
              <li>• Language barriers prevent access to <strong className="text-[#1B3409]">expert knowledge</strong></li>
            </ul>
          </div>
          <div className="p-6 rounded-2xl bg-[#2E7D32]/5 border border-[#2E7D32]/20 shadow-sm">
            <h3 className="text-lg font-bold text-[#2E7D32] mb-3">🟢 Our Solution</h3>
            <ul className="space-y-2 text-[#4A5726] text-sm leading-relaxed">
              <li>• <strong className="text-[#1B3409]">AI vision analysis</strong> via Amazon Bedrock Claude 3.5 Sonnet v2</li>
              <li>• Accessible through <strong className="text-[#1B3409]">WhatsApp</strong> — works on any phone</li>
              <li>• Support for <strong className="text-[#1B3409]">11 Indian languages</strong> via Amazon Translate</li>
              <li>• Actionable treatments with <strong className="text-[#1B3409]">dosage, cost & organic options</strong></li>
              <li>• Under <strong className="text-[#1B3409]">3-second</strong> response time even on low bandwidth</li>
            </ul>
          </div>
        </div>

        {/* Impact */}
        <div className="p-6 rounded-2xl bg-white border border-[#d4c5a0]/40 mb-12 shadow-sm">
          <h3 className="text-lg font-bold text-center text-[#1B3409] mb-6">Projected Impact</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            {[
              { val: '10M+', desc: 'Farmers can be reached via WhatsApp' },
              { val: '30-40%', desc: 'Reduction in crop losses' },
              { val: '₹15K-20K', desc: 'Savings per farmer per season' },
              { val: '11', desc: 'Indian languages supported' },
            ].map(item => (
              <div key={item.desc}>
                <div className="text-2xl font-bold text-[#2E7D32]">{item.val}</div>
                <div className="text-[#7A8856] text-xs mt-1">{item.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div className="mb-12">
          <h3 className="text-2xl font-bold text-center text-[#1B3409] mb-8">Technology Stack</h3>
          <div className="grid md:grid-cols-2 gap-6">
            {techStack.map(cat => (
              <div key={cat.category} className="p-5 rounded-2xl bg-white border border-[#d4c5a0]/40 shadow-sm">
                <h4 className="text-sm font-bold text-[#D4A017] uppercase tracking-wider mb-3">{cat.category}</h4>
                <div className="flex flex-wrap gap-2">
                  {cat.items.map(item => (
                    <span key={item} className="px-3 py-1.5 rounded-lg bg-[#F7F0E3] text-[#4A5726] text-xs border border-[#d4c5a0]/30">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Architecture */}
        <div className="p-6 rounded-2xl bg-white border border-[#d4c5a0]/40 mb-12 shadow-sm">
          <h3 className="text-lg font-bold mb-4 text-center text-[#1B3409]">System Architecture</h3>
          <div className="text-center text-sm text-[#4A5726] space-y-3">
            <div className="flex flex-wrap justify-center gap-3">
              <span className="px-4 py-2 rounded-xl bg-[#25D366]/10 border border-[#25D366]/20">📱 WhatsApp / Web UI</span>
              <span className="text-[#D4A017] font-bold">→</span>
              <span className="px-4 py-2 rounded-xl bg-blue-50 border border-blue-200/50">🌐 API Gateway</span>
              <span className="text-[#D4A017] font-bold">→</span>
              <span className="px-4 py-2 rounded-xl bg-purple-50 border border-purple-200/50">⚡ Lambda / FastAPI</span>
            </div>
            <div className="text-[#D4A017] font-bold">↓</div>
            <div className="flex flex-wrap justify-center gap-3">
              <span className="px-4 py-2 rounded-xl bg-orange-50 border border-orange-200/50">🧠 Bedrock AI</span>
              <span className="px-4 py-2 rounded-xl bg-red-50 border border-red-200/50">👁️ Rekognition</span>
              <span className="px-4 py-2 rounded-xl bg-[#D4A017]/5 border border-[#D4A017]/15">🔄 Translate</span>
              <span className="px-4 py-2 rounded-xl bg-teal-50 border border-teal-200/50">🔊 Polly</span>
              <span className="px-4 py-2 rounded-xl bg-cyan-50 border border-cyan-200/50">🗄️ DynamoDB</span>
              <span className="px-4 py-2 rounded-xl bg-pink-50 border border-pink-200/50">📦 S3</span>
              <span className="px-4 py-2 rounded-xl bg-indigo-50 border border-indigo-200/50">📊 CloudWatch</span>
            </div>
          </div>
        </div>

        {/* SDG Goals */}
        <div className="p-6 rounded-2xl bg-white border border-[#d4c5a0]/40 mb-12 shadow-sm">
          <h3 className="text-lg font-bold mb-4 text-center text-[#1B3409]">UN Sustainable Development Goals</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            {[
              { num: 1, title: 'No Poverty', desc: 'Higher yields = better income' },
              { num: 2, title: 'Zero Hunger', desc: 'Reduced crop losses' },
              { num: 12, title: 'Responsible Consumption', desc: 'Optimized pesticide use' },
              { num: 15, title: 'Life on Land', desc: 'Sustainable farming practices' },
            ].map(g => (
              <div key={g.num} className="p-3 rounded-xl bg-[#2E7D32]/5 border border-[#2E7D32]/10">
                <div className="text-2xl font-bold text-[#2E7D32]">SDG {g.num}</div>
                <div className="text-xs font-semibold text-[#1B3409] mt-1">{g.title}</div>
                <div className="text-xs text-[#7A8856] mt-0.5">{g.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Hackathon */}
        <div className="text-center p-6 rounded-2xl border border-[#D4A017]/30 bg-[#D4A017]/5 shadow-sm">
          <FaAws className="text-4xl text-[#FF6F00] mx-auto mb-3" />
          <h3 className="text-lg font-bold text-[#1B3409] mb-2">AI for Bharat Hackathon 2026</h3>
          <p className="text-[#7A8856] text-sm mb-4">Track 03: AI for Rural Innovation & Sustainable Systems</p>
          <p className="text-[#a0ad8a] text-xs">
            Built with Amazon Bedrock, Claude 3.5 Sonnet v2, Rekognition, S3, DynamoDB, Lambda, Translate, Polly, and CloudWatch.
          </p>
        </div>
      </div>
    </div>
  )
}
