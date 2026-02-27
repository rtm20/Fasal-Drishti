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
    items: ['Bedrock (Claude 3.5 Sonnet v2)', 'S3', 'DynamoDB', 'Lambda', 'API Gateway', 'Translate', 'Polly', 'CloudWatch'],
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
    <div className="min-h-screen bg-[#0a0a14] text-white pt-24 pb-20 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 mb-4">
            <FaSeedling className="text-3xl text-green-400" />
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold mb-4">
            <span className="bg-gradient-to-r from-green-400 to-emerald-300 bg-clip-text text-transparent">
              About FasalDrishti
            </span>
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto leading-relaxed">
            An AI-powered crop disease detection platform built to empower 
            smallholder farmers across rural India with accessible, affordable, and 
            actionable agricultural intelligence.
          </p>
        </div>

        {/* Problem & Solution */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          <div className="p-6 rounded-2xl bg-red-900/10 border border-red-900/20">
            <h3 className="text-lg font-bold text-red-400 mb-3">🔴 The Problem</h3>
            <ul className="space-y-2 text-gray-300 text-sm leading-relaxed">
              <li>• Indian farmers lose <strong>₹50,000 crore+</strong> annually to crop diseases</li>
              <li>• 1 agricultural expert per <strong>1,000+ farmers</strong> — severe shortage</li>
              <li>• 65% farmers have <strong>no smartphone apps</strong> — only basic feature phones</li>
              <li>• Disease misidentification leads to <strong>wrong pesticide usage</strong></li>
              <li>• Language barriers prevent access to <strong>expert knowledge</strong></li>
            </ul>
          </div>
          <div className="p-6 rounded-2xl bg-green-900/10 border border-green-900/20">
            <h3 className="text-lg font-bold text-green-400 mb-3">🟢 Our Solution</h3>
            <ul className="space-y-2 text-gray-300 text-sm leading-relaxed">
              <li>• <strong>AI vision analysis</strong> via Amazon Bedrock Claude 3.5 Sonnet v2</li>
              <li>• Accessible through <strong>WhatsApp</strong> — works on any phone</li>
              <li>• Support for <strong>11 Indian languages</strong> via Amazon Translate</li>
              <li>• Actionable treatments with <strong>dosage, cost & organic options</strong></li>
              <li>• Under <strong>3-second</strong> response time even on low bandwidth</li>
            </ul>
          </div>
        </div>

        {/* Impact */}
        <div className="p-6 rounded-2xl bg-[#0f0f1a] border border-green-900/20 mb-12">
          <h3 className="text-lg font-bold text-center mb-6">Projected Impact</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            {[
              { val: '10M+', desc: 'Farmers can be reached via WhatsApp' },
              { val: '30-40%', desc: 'Reduction in crop losses' },
              { val: '₹15K-20K', desc: 'Savings per farmer per season' },
              { val: '11', desc: 'Indian languages supported' },
            ].map(item => (
              <div key={item.desc}>
                <div className="text-2xl font-bold text-green-400">{item.val}</div>
                <div className="text-gray-400 text-xs mt-1">{item.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div className="mb-12">
          <h3 className="text-2xl font-bold text-center mb-8">Technology Stack</h3>
          <div className="grid md:grid-cols-2 gap-6">
            {techStack.map(cat => (
              <div key={cat.category} className="p-5 rounded-2xl bg-[#0f0f1a] border border-green-900/20">
                <h4 className="text-sm font-bold text-green-400 uppercase tracking-wider mb-3">{cat.category}</h4>
                <div className="flex flex-wrap gap-2">
                  {cat.items.map(item => (
                    <span key={item} className="px-3 py-1.5 rounded-lg bg-green-900/20 text-gray-300 text-xs border border-green-900/20">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Architecture */}
        <div className="p-6 rounded-2xl bg-[#0f0f1a] border border-green-900/20 mb-12">
          <h3 className="text-lg font-bold mb-4 text-center">System Architecture</h3>
          <div className="text-center text-sm text-gray-300 space-y-3">
            <div className="flex flex-wrap justify-center gap-3">
              <span className="px-4 py-2 rounded-xl bg-green-900/20 border border-green-700/30">📱 WhatsApp / Web UI</span>
              <span className="text-green-500">→</span>
              <span className="px-4 py-2 rounded-xl bg-blue-900/20 border border-blue-700/30">🌐 API Gateway</span>
              <span className="text-green-500">→</span>
              <span className="px-4 py-2 rounded-xl bg-purple-900/20 border border-purple-700/30">⚡ Lambda / FastAPI</span>
            </div>
            <div className="text-green-500">↓</div>
            <div className="flex flex-wrap justify-center gap-3">
              <span className="px-4 py-2 rounded-xl bg-orange-900/20 border border-orange-700/30">🧠 Bedrock AI</span>
              <span className="px-4 py-2 rounded-xl bg-yellow-900/20 border border-yellow-700/30">🔄 Translate</span>
              <span className="px-4 py-2 rounded-xl bg-cyan-900/20 border border-cyan-700/30">🗄️ DynamoDB</span>
              <span className="px-4 py-2 rounded-xl bg-pink-900/20 border border-pink-700/30">📦 S3</span>
            </div>
          </div>
        </div>

        {/* SDG Goals */}
        <div className="p-6 rounded-2xl bg-[#0f0f1a] border border-green-900/20 mb-12">
          <h3 className="text-lg font-bold mb-4 text-center">UN Sustainable Development Goals</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            {[
              { num: 1, title: 'No Poverty', desc: 'Higher yields = better income' },
              { num: 2, title: 'Zero Hunger', desc: 'Reduced crop losses' },
              { num: 12, title: 'Responsible Consumption', desc: 'Optimized pesticide use' },
              { num: 15, title: 'Life on Land', desc: 'Sustainable farming practices' },
            ].map(g => (
              <div key={g.num} className="p-3 rounded-xl bg-green-900/10 border border-green-900/20">
                <div className="text-2xl font-bold text-green-400">SDG {g.num}</div>
                <div className="text-xs font-semibold text-gray-300 mt-1">{g.title}</div>
                <div className="text-xs text-gray-500 mt-0.5">{g.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Hackathon */}
        <div className="text-center p-6 rounded-2xl border border-green-900/20">
          <FaAws className="text-4xl text-orange-400 mx-auto mb-3" />
          <h3 className="text-lg font-bold mb-2">AI for Bharat Hackathon 2026</h3>
          <p className="text-gray-400 text-sm mb-4">Track 03: AI for Rural Innovation & Sustainable Systems</p>
          <p className="text-gray-500 text-xs">
            Built with Amazon Bedrock, Claude 3.5 Sonnet v2, S3, DynamoDB, Lambda, Translate, and Polly.
          </p>
        </div>
      </div>
    </div>
  )
}
