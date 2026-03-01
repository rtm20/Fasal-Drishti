import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area
} from 'recharts'
import { FaLeaf, FaBug, FaUsers, FaClock, FaCheckCircle, FaTimesCircle } from 'react-icons/fa'
import { MdSpeed, MdCloud } from 'react-icons/md'
import { getDashboardStats, getSupportedInfo } from '../utils/api'

const COLORS = ['#2E7D32', '#4CAF50', '#66BB6A', '#D4A017', '#F9A825', '#ef4444', '#795548', '#FF6F00']

const SEVERITY_COLORS = {
  none: '#2E7D32',
  mild: '#F9A825',
  moderate: '#FF6F00',
  severe: '#ef4444',
}

const AWS_SERVICE_ICONS = {
  bedrock: '🧠',
  rekognition: '👁️',
  translate: '🌐',
  s3: '📦',
  polly: '🔊',
  dynamodb: '🗄️',
  cloudwatch: '📊',
}

const AWS_SERVICE_NAMES = {
  bedrock: 'Amazon Bedrock (Claude 3.5 Sonnet v2)',
  rekognition: 'Amazon Rekognition',
  translate: 'Amazon Translate',
  s3: 'Amazon S3',
  polly: 'Amazon Polly',
  dynamodb: 'Amazon DynamoDB',
  cloudwatch: 'Amazon CloudWatch',
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [supported, setSupported] = useState(null)
  const [awsHealth, setAwsHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchData() {
      try {
        const API_BASE = import.meta.env.VITE_API_URL || ''
        const [statsRes, supRes, healthRes] = await Promise.all([
          getDashboardStats(),
          getSupportedInfo(),
          fetch(`${API_BASE}/api/health/detailed`).then(r => r.json()).catch(() => null),
        ])
        setStats(statsRes)
        setSupported(supRes)
        setAwsHealth(healthRes)
      } catch (err) {
        setError('Could not connect to backend. Is the server running?')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  // ——— Derived chart data from real DynamoDB stats ———

  const diseaseChartData = (stats?.top_diseases || []).map(d => ({
    name: d.name || d.disease_name || 'Unknown',
    count: d.count || 0,
  }))

  const cropChartData = Object.entries(stats?.crop_distribution || {}).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
  }))

  const severityChartData = Object.entries(stats?.severity_distribution || {})
    .filter(([, v]) => v > 0)
    .map(([name, value]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      value,
      color: SEVERITY_COLORS[name] || '#6b7280',
    }))

  // Group recent scans by date for trend chart
  const trendData = (() => {
    const scans = stats?.recent_scans || []
    const dateCounts = {}
    scans.forEach(s => {
      const d = s.date || (s.timestamp ? s.timestamp.split('T')[0] : 'unknown')
      dateCounts[d] = (dateCounts[d] || 0) + 1
    })
    return Object.entries(dateCounts)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([date, count]) => ({ day: date, scans: count }))
  })()

  // Recent scans for the table
  const recentScans = (stats?.recent_scans || []).slice(0, 10)

  // AWS services list from health endpoint
  const awsServices = (() => {
    if (!awsHealth?.services?.ai_pipeline) return []
    const pipeline = awsHealth.services.ai_pipeline
    const services = []
    const keys = ['bedrock', 'rekognition', 'translate', 's3', 'polly', 'dynamodb', 'cloudwatch']
    keys.forEach(key => {
      if (pipeline[key]) {
        services.push({
          key,
          name: AWS_SERVICE_NAMES[key] || key,
          icon: AWS_SERVICE_ICONS[key] || '☁️',
          available: pipeline[key].available || false,
          detail: key === 'bedrock' ? pipeline[key].model
            : key === 's3' ? `Bucket: ${pipeline[key].bucket}`
            : key === 'polly' ? pipeline[key].voice
            : key === 'dynamodb' ? `Tables: ${(pipeline[key].tables || []).join(', ')}`
            : key === 'cloudwatch' ? `Namespace: ${pipeline[key].namespace}`
            : '',
        })
      }
    })
    return services
  })()

  const operationalCount = awsHealth?.aws_services_operational || 0

  const statCards = [
    {
      icon: <FaUsers className="text-2xl" />,
      label: 'Total Scans',
      value: stats?.total_scans ?? 0,
      color: 'text-[#2E7D32]',
      subtitle: 'From DynamoDB',
    },
    {
      icon: <FaBug className="text-2xl" />,
      label: 'Diseases Detected',
      value: stats?.diseases_detected ?? 0,
      color: 'text-red-500',
      subtitle: 'Unique diseases',
    },
    {
      icon: <FaLeaf className="text-2xl" />,
      label: 'Crops Analyzed',
      value: stats?.crops_analyzed ?? 0,
      color: 'text-[#4CAF50]',
      subtitle: 'Crop types',
    },
    {
      icon: <MdSpeed className="text-2xl" />,
      label: 'Avg Confidence',
      value: stats?.average_confidence ? `${stats.average_confidence}%` : '—',
      color: 'text-[#D4A017]',
      subtitle: 'AI accuracy',
    },
  ]

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FFFDF7] text-[#1B3409] pt-24 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-[#2E7D32]/20 border-t-[#2E7D32] rounded-full animate-spin mx-auto mb-4" />
          <p className="text-[#7A8856]">Loading real-time data from AWS...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#FFFDF7] text-[#1B3409] pt-24 pb-20 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-3xl font-bold mb-2">
            <span className="text-[#2E7D32]">
              📊 Live Analytics Dashboard
            </span>
          </h1>
          <p className="text-[#7A8856]">
            Real-time insights powered by <span className="text-[#D4A017] font-medium">Amazon DynamoDB</span> &amp; <span className="text-[#D4A017] font-medium">CloudWatch</span> — all data from actual scans.
          </p>
          {error && (
            <div className="mt-3 p-3 rounded-xl bg-red-50 border border-red-200 text-red-600 text-sm">
              {error}
            </div>
          )}
        </div>

        {/* ================= AWS SERVICES HEALTH ================= */}
        <div className="mb-8 p-6 rounded-2xl bg-white border border-[#D4A017]/20 shadow-sm">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-3">
              <MdCloud className="text-2xl text-[#D4A017]" />
              <div>
                <h2 className="text-lg font-bold text-[#1B3409]">AWS Services Status</h2>
                <p className="text-xs text-[#7A8856]">Live connectivity check to all AWS services</p>
              </div>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-[#2E7D32]/10 border border-[#2E7D32]/20">
              <div className="w-2 h-2 rounded-full bg-[#2E7D32] animate-pulse" />
              <span className="text-[#2E7D32] text-sm font-semibold">{operationalCount}/7 Operational</span>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
            {awsServices.map(svc => (
              <div
                key={svc.key}
                className={`p-3 rounded-xl border text-center transition-all ${
                  svc.available
                    ? 'bg-[#2E7D32]/5 border-[#2E7D32]/20 hover:border-[#2E7D32]/40'
                    : 'bg-red-50 border-red-200'
                }`}
              >
                <div className="text-2xl mb-1">{svc.icon}</div>
                <div className="text-xs font-medium text-[#4A5726] mb-1">{svc.key.charAt(0).toUpperCase() + svc.key.slice(1)}</div>
                <div className="flex items-center justify-center gap-1">
                  {svc.available ? (
                    <FaCheckCircle className="text-[#2E7D32] text-xs" />
                  ) : (
                    <FaTimesCircle className="text-red-500 text-xs" />
                  )}
                  <span className={`text-xs ${svc.available ? 'text-[#2E7D32]' : 'text-red-500'}`}>
                    {svc.available ? 'Live' : 'Down'}
                  </span>
                </div>
                {svc.detail && (
                  <div className="text-[10px] text-[#7A8856] mt-1 truncate" title={svc.detail}>
                    {svc.detail}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* ================= STAT CARDS ================= */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {statCards.map(card => (
            <div key={card.label} className="p-5 rounded-2xl bg-white border border-[#d4c5a0]/40 hover:border-[#2E7D32]/30 transition-colors shadow-sm">
              <div className={`${card.color} mb-3`}>{card.icon}</div>
              <div className="text-2xl font-bold text-[#1B3409]">{card.value}</div>
              <div className="text-[#7A8856] text-sm mt-1">{card.label}</div>
              <div className="text-[#a0ad8a] text-xs mt-0.5">{card.subtitle}</div>
            </div>
          ))}
        </div>

        {/* ================= CHARTS ROW 1 ================= */}
        <div className="grid lg:grid-cols-2 gap-6 mb-6">
          {/* Disease Distribution — from DynamoDB */}
          <div className="p-6 rounded-2xl bg-white border border-[#d4c5a0]/40 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-[#1B3409]">Disease Distribution</h3>
              <span className="text-[10px] text-[#D4A017] bg-[#D4A017]/10 px-2 py-0.5 rounded-full">DynamoDB</span>
            </div>
            {diseaseChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={diseaseChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e8dcc8" />
                  <XAxis dataKey="name" tick={{ fill: '#5a6b3c', fontSize: 11 }} angle={-30} textAnchor="end" height={60} />
                  <YAxis tick={{ fill: '#5a6b3c', fontSize: 11 }} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #d4c5a0', borderRadius: '12px', color: '#1B3409' }}
                    labelStyle={{ color: '#2E7D32' }}
                  />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                    {diseaseChartData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[280px] flex items-center justify-center">
                <div className="text-center text-[#a0ad8a]">
                  <FaBug className="text-3xl mx-auto mb-2 opacity-30" />
                  <p className="text-sm">No disease data yet</p>
                  <p className="text-xs mt-1">Scan some diseased crops to populate this chart</p>
                </div>
              </div>
            )}
          </div>

          {/* Crop Distribution — from DynamoDB */}
          <div className="p-6 rounded-2xl bg-white border border-[#d4c5a0]/40 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-[#1B3409]">Crop Distribution</h3>
              <span className="text-[10px] text-[#D4A017] bg-[#D4A017]/10 px-2 py-0.5 rounded-full">DynamoDB</span>
            </div>
            {cropChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie data={cropChartData} cx="50%" cy="50%" outerRadius={100} innerRadius={50}
                    dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {cropChartData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #d4c5a0', borderRadius: '12px', color: '#1B3409' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[280px] flex items-center justify-center">
                <div className="text-center text-[#a0ad8a]">
                  <FaLeaf className="text-3xl mx-auto mb-2 opacity-30" />
                  <p className="text-sm">No crop data yet</p>
                  <p className="text-xs mt-1">Start scanning to see crop distribution</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ================= CHARTS ROW 2 ================= */}
        <div className="grid lg:grid-cols-2 gap-6 mb-6">
          {/* Scan Activity — from DynamoDB timestamps */}
          <div className="p-6 rounded-2xl bg-white border border-[#d4c5a0]/40 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-[#1B3409]">Scan Activity</h3>
              <span className="text-[10px] text-[#D4A017] bg-[#D4A017]/10 px-2 py-0.5 rounded-full">DynamoDB</span>
            </div>
            {trendData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={trendData}>
                  <defs>
                    <linearGradient id="scanGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#2E7D32" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="#2E7D32" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e8dcc8" />
                  <XAxis dataKey="day" tick={{ fill: '#5a6b3c', fontSize: 11 }} />
                  <YAxis tick={{ fill: '#5a6b3c', fontSize: 11 }} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #d4c5a0', borderRadius: '12px', color: '#1B3409' }}
                  />
                  <Area type="monotone" dataKey="scans" stroke="#2E7D32" fill="url(#scanGrad)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[250px] flex items-center justify-center">
                <div className="text-center text-[#a0ad8a]">
                  <FaClock className="text-3xl mx-auto mb-2 opacity-30" />
                  <p className="text-sm">No activity data yet</p>
                </div>
              </div>
            )}
          </div>

          {/* Severity Distribution — from DynamoDB */}
          <div className="p-6 rounded-2xl bg-white border border-[#d4c5a0]/40 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-[#1B3409]">Severity Distribution</h3>
              <span className="text-[10px] text-[#D4A017] bg-[#D4A017]/10 px-2 py-0.5 rounded-full">DynamoDB</span>
            </div>
            {severityChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie data={severityChartData} cx="50%" cy="50%" outerRadius={90} dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {severityChartData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #d4c5a0', borderRadius: '12px', color: '#1B3409' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[250px] flex items-center justify-center">
                <div className="text-center text-[#a0ad8a]">
                  <MdSpeed className="text-3xl mx-auto mb-2 opacity-30" />
                  <p className="text-sm">No severity data yet</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ================= ANALYSIS ENGINE BREAKDOWN ================= */}
        {stats?.engine_distribution && Object.keys(stats.engine_distribution).length > 0 && (
          <div className="p-6 rounded-2xl bg-white border border-[#d4c5a0]/40 mb-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-[#1B3409]">AI Engine Usage</h3>
              <span className="text-[10px] text-[#D4A017] bg-[#D4A017]/10 px-2 py-0.5 rounded-full">DynamoDB</span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(stats.engine_distribution).map(([engine, count]) => (
                <div key={engine} className="p-4 rounded-xl bg-[#2E7D32]/5 border border-[#2E7D32]/10 text-center">
                  <div className="text-2xl mb-1">
                    {engine === 'rekognition' ? '👁️' : engine === 'bedrock' ? '🧠' : engine === 'local_fallback' ? '🔧' : '⚙️'}
                  </div>
                  <div className="text-lg font-bold text-[#2E7D32]">{count}</div>
                  <div className="text-xs text-[#7A8856] mt-0.5">{engine.replace(/_/g, ' ')}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ================= SUPPORTED CAPABILITIES ================= */}
        {supported && (
          <div className="p-6 rounded-2xl bg-white border border-[#d4c5a0]/40 mb-6 shadow-sm">
            <h3 className="font-semibold text-[#1B3409] mb-4">Platform Capabilities</h3>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="p-4 rounded-xl bg-[#2E7D32]/5 border border-[#2E7D32]/10">
                <div className="text-3xl font-bold text-[#2E7D32]">{supported.total_diseases}</div>
                <div className="text-xs text-[#7A8856] mt-1">Diseases Detectable</div>
              </div>
              <div className="p-4 rounded-xl bg-[#4CAF50]/5 border border-[#4CAF50]/10">
                <div className="text-3xl font-bold text-[#4CAF50]">{supported.total_crops}</div>
                <div className="text-xs text-[#7A8856] mt-1">Crops Supported</div>
              </div>
              <div className="p-4 rounded-xl bg-[#D4A017]/5 border border-[#D4A017]/10">
                <div className="text-3xl font-bold text-[#D4A017]">{supported.total_languages}</div>
                <div className="text-xs text-[#7A8856] mt-1">Languages</div>
              </div>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {Object.entries(supported.languages || {}).map(([code, name]) => (
                <span key={code} className="px-3 py-1 rounded-full bg-[#D4A017]/5 border border-[#D4A017]/15 text-xs text-[#4A5726]">
                  {name}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* ================= RECENT SCANS TABLE — REAL DATA ================= */}
        <div className="p-6 rounded-2xl bg-white border border-[#d4c5a0]/40 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-[#1B3409]">Recent Detections</h3>
            <span className="text-[10px] text-[#D4A017] bg-[#D4A017]/10 px-2 py-0.5 rounded-full">Live from DynamoDB</span>
          </div>
          {recentScans.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-[#7A8856] border-b border-[#d4c5a0]/40">
                    <th className="text-left py-3 px-2 font-medium">Scan ID</th>
                    <th className="text-left py-3 px-2 font-medium">Crop</th>
                    <th className="text-left py-3 px-2 font-medium">Disease</th>
                    <th className="text-left py-3 px-2 font-medium">Severity</th>
                    <th className="text-left py-3 px-2 font-medium">Confidence</th>
                    <th className="text-left py-3 px-2 font-medium">Engine</th>
                    <th className="text-left py-3 px-2 font-medium">Source</th>
                    <th className="text-left py-3 px-2 font-medium">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {recentScans.map((scan, i) => {
                    const sevConfig = {
                      none: 'text-[#2E7D32] bg-[#2E7D32]/10',
                      mild: 'text-yellow-600 bg-yellow-500/10',
                      moderate: 'text-orange-600 bg-orange-500/10',
                      severe: 'text-red-600 bg-red-500/10',
                    }
                    const sourceConfig = {
                      whatsapp_twilio: { label: 'WhatsApp', class: 'text-[#2E7D32] bg-[#2E7D32]/10' },
                      web: { label: 'Web App', class: 'text-blue-600 bg-blue-500/10' },
                      api: { label: 'API', class: 'text-purple-600 bg-purple-500/10' },
                    }
                    const src = sourceConfig[scan.source] || { label: scan.source || 'Unknown', class: 'text-[#7A8856] bg-[#F7F0E3]' }
                    const timeStr = scan.timestamp
                      ? new Date(scan.timestamp).toLocaleString('en-IN', { hour: '2-digit', minute: '2-digit', day: 'numeric', month: 'short' })
                      : '—'
                    return (
                      <tr key={scan.scan_id || i} className="border-b border-[#d4c5a0]/20 hover:bg-[#F7F0E3]/50">
                        <td className="py-3 px-2 text-[#a0ad8a] font-mono text-xs">{scan.scan_id || '—'}</td>
                        <td className="py-3 px-2 text-[#4A5726] capitalize">{scan.crop || '—'}</td>
                        <td className="py-3 px-2 text-[#1B3409] font-medium">{scan.disease_name || scan.disease_key || '—'}</td>
                        <td className="py-3 px-2">
                          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${sevConfig[scan.severity] || sevConfig.moderate}`}>
                            {scan.severity || '—'}
                          </span>
                        </td>
                        <td className="py-3 px-2 text-[#2E7D32] font-medium">{scan.confidence ? `${scan.confidence}%` : '—'}</td>
                        <td className="py-3 px-2">
                          <span className="text-xs text-[#7A8856]">
                            {scan.analysis_engine === 'rekognition' ? '👁️ Rekognition'
                              : scan.analysis_engine === 'bedrock' ? '🧠 Bedrock'
                              : scan.analysis_engine || '—'}
                          </span>
                        </td>
                        <td className="py-3 px-2">
                          <span className={`px-2 py-0.5 rounded-full text-xs ${src.class}`}>{src.label}</span>
                        </td>
                        <td className="py-3 px-2 text-[#a0ad8a] text-xs">{timeStr}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 text-[#a0ad8a]">
              <FaUsers className="text-3xl mx-auto mb-2 opacity-40" />
              <p className="text-sm">No scans recorded yet</p>
              <p className="text-xs mt-1">Use the Analyze page or WhatsApp to scan a crop image</p>
            </div>
          )}
        </div>

        {/* Footer note */}
        <div className="mt-6 text-center text-xs text-[#a0ad8a]">
          All data is fetched in real-time from <span className="text-[#D4A017]">Amazon DynamoDB</span> • 
          Metrics published to <span className="text-[#D4A017]">Amazon CloudWatch</span> • 
          No dummy or hardcoded data
        </div>
      </div>
    </div>
  )
}
