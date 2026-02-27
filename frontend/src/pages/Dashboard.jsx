import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area
} from 'recharts'
import { FaLeaf, FaBug, FaUsers, FaClock } from 'react-icons/fa'
import { getDashboardStats, getSupportedInfo } from '../utils/api'

const COLORS = ['#22c55e', '#10b981', '#14b8a6', '#06b6d4', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

// Fallback demo data
const DEMO_DISEASE_DATA = [
  { name: 'Early Blight', count: 342 },
  { name: 'Late Blight', count: 289 },
  { name: 'Leaf Curl', count: 256 },
  { name: 'Rice Blast', count: 198 },
  { name: 'Brown Spot', count: 167 },
  { name: 'Leaf Rust', count: 145 },
  { name: 'Healthy', count: 412 },
]

const DEMO_CROP_DATA = [
  { name: 'Tomato', value: 35 },
  { name: 'Rice', value: 25 },
  { name: 'Wheat', value: 18 },
  { name: 'Cotton', value: 10 },
  { name: 'Potato', value: 7 },
  { name: 'Chili', value: 3 },
  { name: 'Onion', value: 2 },
]

const DEMO_TREND_DATA = [
  { day: 'Mon', scans: 45 },
  { day: 'Tue', scans: 62 },
  { day: 'Wed', scans: 78 },
  { day: 'Thu', scans: 55 },
  { day: 'Fri', scans: 91 },
  { day: 'Sat', scans: 120 },
  { day: 'Sun', scans: 85 },
]

const DEMO_SEVERITY_DATA = [
  { name: 'Low', value: 30, color: '#facc15' },
  { name: 'Moderate', value: 40, color: '#f97316' },
  { name: 'High', value: 22, color: '#ef4444' },
  { name: 'Critical', value: 8, color: '#dc2626' },
]

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [supported, setSupported] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const [s, sup] = await Promise.all([getDashboardStats(), getSupportedInfo()])
        setStats(s)
        setSupported(sup)
      } catch {
        // Use demo data if backend not running
        setStats({
          total_scans: 1809,
          diseases_detected: 12,
          crops_supported: 7,
          avg_response_time: '2.3s',
        })
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const statCards = [
    { icon: <FaUsers className="text-2xl" />, label: 'Total Scans', value: stats?.total_scans || 1809, color: 'text-green-400' },
    { icon: <FaBug className="text-2xl" />, label: 'Diseases Detected', value: stats?.diseases_detected || 12, color: 'text-red-400' },
    { icon: <FaLeaf className="text-2xl" />, label: 'Crops Covered', value: stats?.crops_supported || 7, color: 'text-emerald-400' },
    { icon: <FaClock className="text-2xl" />, label: 'Avg Response Time', value: stats?.avg_response_time || '2.3s', color: 'text-cyan-400' },
  ]

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a14] text-white pt-24 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-green-500/30 border-t-green-500 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading dashboard…</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0a0a14] text-white pt-24 pb-20 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-3xl font-bold mb-2">
            <span className="bg-gradient-to-r from-green-400 to-emerald-300 bg-clip-text text-transparent">
              Analytics Dashboard
            </span>
          </h1>
          <p className="text-gray-400">Real-time insights from crop disease detection across India.</p>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {statCards.map(card => (
            <div key={card.label} className="p-5 rounded-2xl bg-[#0f0f1a] border border-green-900/20 hover:border-green-500/30 transition-colors">
              <div className={`${card.color} mb-3`}>{card.icon}</div>
              <div className="text-2xl font-bold text-white">{card.value}</div>
              <div className="text-gray-500 text-sm mt-1">{card.label}</div>
            </div>
          ))}
        </div>

        {/* Charts Row 1 */}
        <div className="grid lg:grid-cols-2 gap-6 mb-6">
          {/* Disease Distribution */}
          <div className="p-6 rounded-2xl bg-[#0f0f1a] border border-green-900/20">
            <h3 className="font-semibold text-gray-200 mb-4">Disease Distribution</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={DEMO_DISEASE_DATA}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e30" />
                <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} angle={-30} textAnchor="end" height={60} />
                <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #22c55e30', borderRadius: '12px' }}
                  labelStyle={{ color: '#22c55e' }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {DEMO_DISEASE_DATA.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Crop Distribution */}
          <div className="p-6 rounded-2xl bg-[#0f0f1a] border border-green-900/20">
            <h3 className="font-semibold text-gray-200 mb-4">Crop Distribution</h3>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={DEMO_CROP_DATA} cx="50%" cy="50%" outerRadius={100} innerRadius={50}
                  dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {DEMO_CROP_DATA.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #22c55e30', borderRadius: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Charts Row 2 */}
        <div className="grid lg:grid-cols-2 gap-6 mb-6">
          {/* Scan Trends */}
          <div className="p-6 rounded-2xl bg-[#0f0f1a] border border-green-900/20">
            <h3 className="font-semibold text-gray-200 mb-4">Weekly Scan Trends</h3>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={DEMO_TREND_DATA}>
                <defs>
                  <linearGradient id="scanGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#22c55e" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#22c55e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e30" />
                <XAxis dataKey="day" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #22c55e30', borderRadius: '12px' }}
                />
                <Area type="monotone" dataKey="scans" stroke="#22c55e" fill="url(#scanGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Severity Distribution */}
          <div className="p-6 rounded-2xl bg-[#0f0f1a] border border-green-900/20">
            <h3 className="font-semibold text-gray-200 mb-4">Severity Distribution</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={DEMO_SEVERITY_DATA} cx="50%" cy="50%" outerRadius={90} dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {DEMO_SEVERITY_DATA.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #22c55e30', borderRadius: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Regional Map placeholder */}
        <div className="p-6 rounded-2xl bg-[#0f0f1a] border border-green-900/20 mb-6">
          <h3 className="font-semibold text-gray-200 mb-4">Regional Coverage</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
            {[
              { state: 'Maharashtra', scans: 342, emoji: '🍅' },
              { state: 'Punjab', scans: 289, emoji: '🌾' },
              { state: 'Tamil Nadu', scans: 256, emoji: '🌾' },
              { state: 'Karnataka', scans: 198, emoji: '🧅' },
              { state: 'Uttar Pradesh', scans: 167, emoji: '🥔' },
              { state: 'West Bengal', scans: 145, emoji: '🌾' },
              { state: 'Gujarat', scans: 132, emoji: '🧶' },
              { state: 'Andhra Pradesh', scans: 121, emoji: '🌶️' },
              { state: 'Madhya Pradesh', scans: 98, emoji: '🌾' },
              { state: 'Rajasthan', scans: 87, emoji: '🌾' },
              { state: 'Bihar', scans: 76, emoji: '🌾' },
              { state: 'Telangana', scans: 65, emoji: '🧶' },
            ].map(r => (
              <div key={r.state} className="p-3 rounded-xl bg-green-900/10 border border-green-900/20 text-center">
                <div className="text-2xl mb-1">{r.emoji}</div>
                <div className="text-xs text-gray-300 font-medium">{r.state}</div>
                <div className="text-xs text-green-400 mt-0.5">{r.scans} scans</div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Scans */}
        <div className="p-6 rounded-2xl bg-[#0f0f1a] border border-green-900/20">
          <h3 className="font-semibold text-gray-200 mb-4">Recent Detections</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-gray-500 border-b border-green-900/20">
                  <th className="text-left py-3 px-2 font-medium">Crop</th>
                  <th className="text-left py-3 px-2 font-medium">Disease</th>
                  <th className="text-left py-3 px-2 font-medium">Severity</th>
                  <th className="text-left py-3 px-2 font-medium">Confidence</th>
                  <th className="text-left py-3 px-2 font-medium">Language</th>
                  <th className="text-left py-3 px-2 font-medium">Time</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { crop: 'Tomato', disease: 'Early Blight', severity: 'moderate', confidence: 92, lang: 'Hindi', time: '2 min ago' },
                  { crop: 'Rice', disease: 'Blast', severity: 'high', confidence: 88, lang: 'Tamil', time: '5 min ago' },
                  { crop: 'Wheat', disease: 'Leaf Rust', severity: 'low', confidence: 95, lang: 'Punjabi', time: '8 min ago' },
                  { crop: 'Cotton', disease: 'Bacterial Blight', severity: 'critical', confidence: 91, lang: 'Gujarati', time: '12 min ago' },
                  { crop: 'Potato', disease: 'Late Blight', severity: 'high', confidence: 87, lang: 'Bengali', time: '15 min ago' },
                ].map((row, i) => {
                  const sevConfig = {
                    low: 'text-yellow-400 bg-yellow-500/10',
                    moderate: 'text-orange-400 bg-orange-500/10',
                    high: 'text-red-400 bg-red-500/10',
                    critical: 'text-red-500 bg-red-700/10',
                  }
                  return (
                    <tr key={i} className="border-b border-green-900/10 hover:bg-green-900/5">
                      <td className="py-3 px-2 text-gray-300">{row.crop}</td>
                      <td className="py-3 px-2 text-white font-medium">{row.disease}</td>
                      <td className="py-3 px-2">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${sevConfig[row.severity]}`}>
                          {row.severity}
                        </span>
                      </td>
                      <td className="py-3 px-2 text-green-400">{row.confidence}%</td>
                      <td className="py-3 px-2 text-gray-400">{row.lang}</td>
                      <td className="py-3 px-2 text-gray-500">{row.time}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
