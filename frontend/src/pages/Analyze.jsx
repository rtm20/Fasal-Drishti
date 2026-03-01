import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { FiUploadCloud, FiCamera, FiChevronDown, FiChevronUp } from 'react-icons/fi'
import { FaLeaf, FaWhatsapp, FaLanguage } from 'react-icons/fa'
import { MdWarning } from 'react-icons/md'
import { analyzeImage } from '../utils/api'

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिंदी (Hindi)' },
  { code: 'ta', label: 'தமிழ் (Tamil)' },
  { code: 'te', label: 'తెలుగు (Telugu)' },
  { code: 'kn', label: 'ಕನ್ನಡ (Kannada)' },
  { code: 'bn', label: 'বাংলা (Bengali)' },
  { code: 'mr', label: 'मराठी (Marathi)' },
  { code: 'gu', label: 'ગુજરાતી (Gujarati)' },
  { code: 'pa', label: 'ਪੰਜਾਬੀ (Punjabi)' },
  { code: 'ml', label: 'മലയാളം (Malayalam)' },
  { code: 'or', label: 'ଓଡ଼ିଆ (Odia)' },
]

const SEVERITY_COLORS = {
  none: { bg: 'bg-[#2E7D32]/10', text: 'text-[#2E7D32]', border: 'border-[#2E7D32]/30' },
  mild: { bg: 'bg-yellow-500/10', text: 'text-yellow-600', border: 'border-yellow-500/30' },
  moderate: { bg: 'bg-orange-500/10', text: 'text-orange-600', border: 'border-orange-500/30' },
  severe: { bg: 'bg-red-500/10', text: 'text-red-600', border: 'border-red-500/30' },
}

export default function Analyze() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [language, setLanguage] = useState('en')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [showTreatments, setShowTreatments] = useState(true)
  const [showOrganic, setShowOrganic] = useState(false)
  const [showPrevention, setShowPrevention] = useState(false)

  const onDrop = useCallback((acceptedFiles) => {
    const f = acceptedFiles[0]
    if (f) {
      setFile(f)
      setPreview(URL.createObjectURL(f))
      setResult(null)
      setError(null)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.webp'] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  })

  const handleAnalyze = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await analyzeImage(file, language)
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setFile(null)
    setPreview(null)
    setResult(null)
    setError(null)
  }

  const severity = result?.severity || 'moderate'
  const sColor = SEVERITY_COLORS[severity] || SEVERITY_COLORS.moderate

  return (
    <div className="min-h-screen bg-[#FFFDF7] text-[#1B3409] pt-24 pb-20 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-3xl sm:text-4xl font-bold mb-3">
            <span className="text-[#2E7D32]">
              🌿 Crop Disease Analysis
            </span>
          </h1>
          <p className="text-[#7A8856] max-w-lg mx-auto">
            Upload a photo of your crop leaf to get instant AI-powered disease detection
            with treatment recommendations.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left panel — Upload */}
          <div className="space-y-6">
            {/* Language selector */}
            <div className="flex items-center gap-3">
              <FaLanguage className="text-[#D4A017] text-xl" />
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="flex-1 bg-white border border-[#d4c5a0]/50 rounded-xl px-4 py-2.5 text-sm text-[#1B3409] focus:outline-none focus:border-[#2E7D32]/50 shadow-sm"
              >
                {LANGUAGES.map(l => (
                  <option key={l.code} value={l.code}>{l.label}</option>
                ))}
              </select>
            </div>

            {/* Dropzone */}
            <div
              {...getRootProps()}
              className={`relative rounded-2xl border-2 border-dashed transition-all cursor-pointer
                ${isDragActive
                  ? 'border-[#2E7D32] bg-[#2E7D32]/5'
                  : preview
                    ? 'border-[#2E7D32]/30 bg-white'
                    : 'border-[#d4c5a0] bg-white hover:border-[#2E7D32]/40'
                }
                min-h-[320px] flex items-center justify-center overflow-hidden shadow-sm`}
            >
              <input {...getInputProps()} />
              {preview ? (
                <img
                  src={preview}
                  alt="Crop preview"
                  className="w-full h-full object-contain max-h-[400px] rounded-2xl"
                />
              ) : (
                <div className="text-center p-8">
                  <FiUploadCloud className="text-5xl text-[#2E7D32]/40 mx-auto mb-4" />
                  <p className="text-[#4A5726] font-medium mb-1">
                    {isDragActive ? 'Drop the image here…' : 'Drag & drop crop image here'}
                  </p>
                  <p className="text-[#7A8856] text-sm">or click to browse — JPG, PNG, WebP up to 10&nbsp;MB</p>
                  <div className="mt-4 flex items-center justify-center gap-2 text-[#2E7D32]/50 text-xs">
                    <FiCamera /> Take a clear photo of the affected leaf
                  </div>
                </div>
              )}
            </div>

            {/* Action buttons */}
            <div className="flex gap-3">
              <button
                onClick={handleAnalyze}
                disabled={!file || loading}
                className={`flex-1 py-3 rounded-xl font-semibold text-sm transition-all flex items-center justify-center gap-2
                  ${!file || loading
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : 'bg-[#2E7D32] text-white hover:bg-[#1B5E20] shadow-md hover:shadow-lg'
                  }`}
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Analyzing…
                  </>
                ) : (
                  <>🌿 Analyze Image</>
                )}
              </button>
              {file && (
                <button
                  onClick={handleReset}
                  className="px-4 py-3 rounded-xl bg-[#F7F0E3] text-[#4A5726] text-sm hover:bg-[#efe4ce] transition-colors"
                >
                  Reset
                </button>
              )}
            </div>

            {/* WhatsApp tip */}
            <div className="p-4 rounded-xl bg-[#25D366]/5 border border-[#25D366]/20 flex items-start gap-3">
              <FaWhatsapp className="text-[#25D366] text-xl mt-0.5 flex-shrink-0" />
              <div className="text-sm">
                <p className="text-[#1B5E20] font-medium mb-1">WhatsApp Integration</p>
                <p className="text-[#7A8856] leading-relaxed">
                  Farmers can also send crop images via WhatsApp to get diagnosis in their local language — no app needed.
                </p>
              </div>
            </div>
          </div>

          {/* Right panel — Results */}
          <div className="space-y-6">
            {!result && !loading && !error && (
              <div className="h-full flex items-center justify-center rounded-2xl border border-[#d4c5a0]/40 bg-white min-h-[400px] shadow-sm">
                <div className="text-center text-[#7A8856]">
                  <FaLeaf className="text-4xl mx-auto mb-4 opacity-30" />
                  <p className="font-medium">Upload & analyze an image</p>
                  <p className="text-sm mt-1">Results will appear here</p>
                </div>
              </div>
            )}

            {loading && (
              <div className="h-full flex items-center justify-center rounded-2xl border border-[#d4c5a0]/40 bg-white min-h-[400px] shadow-sm">
                <div className="text-center">
                  <div className="w-16 h-16 border-4 border-[#2E7D32]/20 border-t-[#2E7D32] rounded-full animate-spin mx-auto mb-4" />
                  <p className="text-[#2E7D32] font-medium">Analyzing crop image…</p>
                  <p className="text-[#7A8856] text-sm mt-1">AI is identifying disease patterns</p>
                </div>
              </div>
            )}

            {error && (
              <div className="p-6 rounded-2xl border border-red-300 bg-red-50">
                <div className="flex items-center gap-2 text-red-600 mb-2">
                  <MdWarning className="text-xl" />
                  <span className="font-semibold">Analysis Error</span>
                </div>
                <p className="text-red-500 text-sm">{error}</p>
              </div>
            )}

            {result && (
              <div className="space-y-4">
                {/* Disease Card */}
                <div className="p-6 rounded-2xl border border-[#d4c5a0]/40 bg-white shadow-sm">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h2 className="text-xl font-bold text-[#1B3409]">
                        {result.disease_name || result.disease}
                      </h2>
                      {result.hindi_name && (
                        <p className="text-[#2E7D32] text-sm mt-0.5">{result.hindi_name}</p>
                      )}
                      {result.scientific_name && (
                        <p className="text-[#7A8856] text-xs italic mt-0.5">{result.scientific_name}</p>
                      )}
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${sColor.bg} ${sColor.text} ${sColor.border} border`}>
                      {severity.toUpperCase()}
                    </span>
                  </div>

                  {/* Stats row */}
                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div className="text-center p-3 rounded-xl bg-[#2E7D32]/5 border border-[#2E7D32]/10">
                      <div className="text-2xl font-bold text-[#2E7D32]">
                        {result.confidence ? `${Math.round(result.confidence * 100)}%` : 'N/A'}
                      </div>
                      <div className="text-xs text-[#7A8856] mt-1">Confidence</div>
                    </div>
                    <div className="text-center p-3 rounded-xl bg-[#D4A017]/5 border border-[#D4A017]/10">
                      <div className="text-2xl font-bold text-[#8B6914]">{result.crop || '—'}</div>
                      <div className="text-xs text-[#7A8856] mt-1">Crop</div>
                    </div>
                    <div className="text-center p-3 rounded-xl bg-[#F7F0E3]">
                      <div className={`text-2xl font-bold ${sColor.text}`}>
                        {severity}
                      </div>
                      <div className="text-xs text-[#7A8856] mt-1">Severity</div>
                    </div>
                  </div>

                  {/* Symptoms */}
                  {result.symptoms && result.symptoms.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-semibold text-[#4A5726] mb-2">Symptoms</h4>
                      <ul className="space-y-1">
                        {result.symptoms.map((s, i) => (
                          <li key={i} className="text-[#5a6b3c] text-sm flex items-start gap-2">
                            <span className="text-[#2E7D32] mt-1">•</span> {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* AI Description */}
                  {result.description && (
                    <div className="p-3 rounded-xl bg-[#2E7D32]/5 border border-[#2E7D32]/10">
                      <p className="text-sm text-[#4A5726] leading-relaxed">{result.description}</p>
                    </div>
                  )}
                </div>

                {/* Treatments */}
                {result.treatments && result.treatments.length > 0 && (
                  <div className="rounded-2xl border border-[#d4c5a0]/40 bg-white overflow-hidden shadow-sm">
                    <button
                      onClick={() => setShowTreatments(!showTreatments)}
                      className="w-full px-6 py-4 flex items-center justify-between text-left bg-transparent border-none text-[#1B3409]"
                    >
                      <h3 className="font-semibold flex items-center gap-2">
                        💊 Chemical Treatments
                      </h3>
                      {showTreatments ? <FiChevronUp className="text-[#7A8856]" /> : <FiChevronDown className="text-[#7A8856]" />}
                    </button>
                    {showTreatments && (
                      <div className="px-6 pb-4 space-y-3">
                        {result.treatments.map((t, i) => (
                          <div key={i} className="p-3 rounded-xl bg-[#F7F0E3]/50 border border-[#d4c5a0]/30">
                            <div className="flex items-start justify-between">
                              <span className="text-sm font-medium text-[#1B3409]">{t.name || t}</span>
                              {t.cost && (
                                <span className="text-xs text-[#2E7D32] bg-[#2E7D32]/10 px-2 py-0.5 rounded-full">{t.cost}</span>
                              )}
                            </div>
                            {t.dosage && <p className="text-xs text-[#7A8856] mt-1">Dosage: {t.dosage}</p>}
                            {t.application && <p className="text-xs text-[#7A8856] mt-0.5">{t.application}</p>}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Organic Treatments */}
                {result.organic_treatments && result.organic_treatments.length > 0 && (
                  <div className="rounded-2xl border border-[#2E7D32]/20 bg-white overflow-hidden shadow-sm">
                    <button
                      onClick={() => setShowOrganic(!showOrganic)}
                      className="w-full px-6 py-4 flex items-center justify-between text-left bg-transparent border-none text-[#1B3409]"
                    >
                      <h3 className="font-semibold flex items-center gap-2">
                        🌿 Organic Treatments
                      </h3>
                      {showOrganic ? <FiChevronUp className="text-[#7A8856]" /> : <FiChevronDown className="text-[#7A8856]" />}
                    </button>
                    {showOrganic && (
                      <div className="px-6 pb-4 space-y-2">
                        {result.organic_treatments.map((t, i) => (
                          <div key={i} className="p-3 rounded-xl bg-[#2E7D32]/5 border border-[#2E7D32]/10 text-sm text-[#4A5726]">
                            {typeof t === 'string' ? t : t.name}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Prevention */}
                {result.prevention && result.prevention.length > 0 && (
                  <div className="rounded-2xl border border-[#D4A017]/20 bg-white overflow-hidden shadow-sm">
                    <button
                      onClick={() => setShowPrevention(!showPrevention)}
                      className="w-full px-6 py-4 flex items-center justify-between text-left bg-transparent border-none text-[#1B3409]"
                    >
                      <h3 className="font-semibold flex items-center gap-2">
                        🛡️ Prevention Tips
                      </h3>
                      {showPrevention ? <FiChevronUp className="text-[#7A8856]" /> : <FiChevronDown className="text-[#7A8856]" />}
                    </button>
                    {showPrevention && (
                      <div className="px-6 pb-4 space-y-2">
                        {result.prevention.map((p, i) => (
                          <div key={i} className="flex items-start gap-2 text-sm text-[#4A5726]">
                            <span className="text-[#D4A017] mt-1">✓</span>
                            <span>{p}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Favorable conditions */}
                {result.favorable_conditions && (
                  <div className="p-4 rounded-2xl border border-[#D4A017]/30 bg-[#D4A017]/5">
                    <h4 className="text-sm font-semibold text-[#8B6914] mb-2">⚠️ Favorable Conditions</h4>
                    <p className="text-sm text-[#4A5726]">{result.favorable_conditions}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
