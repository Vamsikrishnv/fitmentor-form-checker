import { useState } from 'react'

function App() {
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [exercise, setExercise] = useState('squat')
  const [analyzing, setAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<any>(null)

  // Use Render URL in prod, localhost in dev
  const API_URL = import.meta.env.PROD
    ? 'https://fitmentor-form-checker.onrender.com'
    : 'http://localhost:8000'

  // Join waitlist submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${API_URL}/api/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name }),
      })

      const data = await response.json()

      if (response.ok) {
        setSubmitted(true)
        setEmail('')
        setName('')
        setTimeout(() => setSubmitted(false), 5000)
      } else {
        setError(data.detail || data.message || 'Something went wrong.')
      }
    } catch (err) {
      console.error('Signup error:', err)
      setError('Failed to join waitlist. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // Analyze uploaded video
  const handleAnalyze = async () => {
    if (!selectedFile) return

    setAnalyzing(true)
    setError('')
    setAnalysisResult(null)

    try {
      const formData = new FormData()
      formData.append('video', selectedFile)
      formData.append('exercise', exercise)

      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        let message = 'Analysis failed'
        try {
          const errJson = await response.json()
          message = errJson.detail || errJson.message || message
        } catch {}
        throw new Error(message)
      }

      const result = await response.json()
      setAnalysisResult(result)
    } catch (err) {
      console.error('Analyze error:', err)
      setError(err instanceof Error ? err.message : 'Failed to analyze video')
    } finally {
      setAnalyzing(false)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) setSelectedFile(file)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      {/* Nav */}
      <nav className="container mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex justify-between items-center">
          <div className="text-white font-bold text-2xl flex items-center gap-2">
            <span className="text-3xl" aria-hidden={true}>🏋️</span>
            <span>FitMentor AI</span>
          </div>

          <div className="hidden md:flex gap-8 text-gray-300">
            <a href="#features" className="hover:text-white transition">Features</a>
            <a href="#demo" className="hover:text-white transition">Demo</a>
            <a href="#waitlist" className="hover:text-white transition">Join Beta</a>
          </div>

          <a
            href="https://github.com/Vamsikrishnv/fitmentor-form-checker"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition"
          >
            ⭐ GitHub
          </a>
        </div>
      </nav>

      {/* Hero */}
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-block mb-4 px-4 py-2 bg-yellow-400/20 rounded-full text-yellow-400 text-sm font-semibold">
              🚀 Now in Alpha Testing
            </div>

            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight">
              Your AI Fitness Coach<br />
              That Teaches <span className="text-yellow-400">Why</span>
            </h1>

            <p className="text-xl sm:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
              Stop following blindly. Get real-time form analysis, understand biomechanics,
              and train smarter with AI-powered coaching.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <a
                href="#waitlist"
                className="px-8 py-4 bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-bold rounded-lg text-lg transition shadow-lg hover:shadow-xl"
              >
                Join Waitlist 🚀
              </a>
              <a
                href="#demo"
                className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-lg text-lg transition backdrop-blur"
              >
                Try Demo 📹
              </a>
            </div>

            <div className="mt-8 flex items-center justify-center gap-6 text-gray-400">
              <div className="flex items-center gap-2">
                <span className="text-green-400">✓</span>
                <span>10+ Exercises</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-400">✓</span>
                <span>Real-time Analysis</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-400">✓</span>
                <span>100% Free Alpha</span>
              </div>
            </div>
          </div>

          {/* Demo card */}
          <div id="demo" className="bg-white/5 backdrop-blur-xl rounded-3xl p-8 sm:p-12 mb-16 border border-white/10">
            <div className="text-center mb-8">
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">Try It Now - Live Demo</h2>
              <p className="text-gray-300 text-lg">Upload your workout video and get instant AI form analysis</p>
            </div>

            <div className="max-w-2xl mx-auto">
              <label htmlFor="video-upload">
                <div className="border-2 border-dashed border-white/30 rounded-2xl p-12 text-center hover:border-yellow-400 hover:bg-white/5 transition cursor-pointer">
                  {!selectedFile ? (
                    <>
                      <div className="text-7xl mb-4" aria-hidden={true}>📹</div>
                      <p className="text-white text-xl mb-2 font-semibold">Drop your workout video here</p>
                      <p className="text-gray-400">or click to browse (MP4, AVI, MOV)</p>
                      <div className="mt-6 inline-block px-6 py-3 bg-yellow-400 text-gray-900 font-bold rounded-lg hover:bg-yellow-500 transition">
                        Choose Video
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="text-7xl mb-4" aria-hidden={true}>✅</div>
                      <p className="text-white text-xl mb-2 font-semibold">{selectedFile.name}</p>
                      <p className="text-gray-400 mb-4">Ready to analyze!</p>

                      {/* Analyze controls */}
                      <div className="mt-6 space-y-4">
                        <div>
                          <label className="text-white font-semibold mb-2 block">Select Exercise:</label>
                          <select
                            value={exercise}
                            onChange={(e) => setExercise(e.target.value)}
                            className="w-full px-4 py-3 rounded-lg bg-white/10 text-white border border-white/20 focus:border-yellow-400 outline-none"
                          >
                            <option value="squat">🏋️ Squat</option>
                            <option value="pushup">💪 Push-up</option>
                            <option value="plank">🤸 Plank</option>
                            <option value="lunge">🦵 Lunge</option>
                            <option value="deadlift">🏃 Deadlift</option>
                          </select>
                        </div>

                        <button
                          type="button"
                          onClick={handleAnalyze}
                          disabled={analyzing || !selectedFile}
                          className="w-full px-6 py-4 bg-green-500 text-white font-bold rounded-lg hover:bg-green-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {analyzing ? '🔄 Analyzing...' : 'Analyze Form →'}
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </label>

              {/* hidden file input must be OUTSIDE the label */}
              <input
                id="video-upload"
                type="file"
                accept="video/*"
                className="hidden"
                onChange={handleFileChange}
              />

              {/* Supported exercises */}
              <div className="mt-8">
                <p className="text-gray-400 text-sm text-center mb-4">Supported exercises:</p>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                  {['🏋️ Squat', '💪 Push-up', '🤸 Plank', '🦵 Lunge', '🏃 Deadlift'].map((labelTxt) => (
                    <div
                      key={labelTxt}
                      className="bg-white/5 hover:bg-white/10 rounded-lg p-3 text-center transition cursor-pointer border border-white/10"
                    >
                      <p className="text-white text-sm font-medium">{labelTxt}</p>
                    </div>
                  ))}
                </div>
                <p className="text-center text-gray-400 text-sm mt-4">+ 5 more exercises</p>
              </div>

              {/* Results Display */}
              {analysisResult && (
                <div className="mt-8 bg-white/5 backdrop-blur-xl rounded-2xl p-8 border border-white/10">
                  <div className="text-center mb-6">
                    <h3 className="text-3xl font-bold text-white mb-2">Analysis Results</h3>
                    <p className="text-gray-300">Here's how you did! 💪</p>
                  </div>

                  {/* Score Circle */}
                  <div className="flex justify-center mb-8">
                    <div
                      className={`w-40 h-40 rounded-full border-8 flex items-center justify-center ${
                        (analysisResult.form_score ?? 0) >= 80
                          ? 'border-green-400 bg-green-400/10'
                          : (analysisResult.form_score ?? 0) >= 60
                          ? 'border-yellow-400 bg-yellow-400/10'
                          : 'border-red-400 bg-red-400/10'
                      }`}
                    >
                      <div className="text-center">
                        <div className="text-5xl font-bold text-white">
                          {analysisResult.form_score ?? '--'}
                        </div>
                        <div className="text-sm text-gray-300">Form Score</div>
                      </div>
                    </div>
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-white/5 rounded-xl p-4 text-center">
                      <div className="text-3xl font-bold text-yellow-400">{analysisResult.rep_count ?? '--'}</div>
                      <div className="text-gray-300 text-sm">Reps Counted</div>
                    </div>
                    <div className="bg-white/5 rounded-xl p-4 text-center">
                      <div className="text-3xl font-bold text-blue-400">{analysisResult.frames_analyzed ?? '--'}</div>
                      <div className="text-gray-300 text-sm">Frames Analyzed</div>
                    </div>
                  </div>

                  {/* Feedback */}
                  <div className="bg-white/5 rounded-xl p-6">
                    <h4 className="text-xl font-bold text-white mb-4">💡 Feedback</h4>
                    {Array.isArray(analysisResult.feedback) && analysisResult.feedback.length > 0 ? (
                      <ul className="space-y-2">
                        {analysisResult.feedback.map((item: string, index: number) => (
                          <li key={index} className="text-gray-300 flex items-start gap-2">
                            <span className="text-yellow-400">•</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-gray-300">Great form! Keep it up! 🎉</p>
                    )}
                  </div>

                  {/* Try Again */}
                  <button
                    onClick={() => {
                      setAnalysisResult(null)
                      setSelectedFile(null)
                    }}
                    className="w-full mt-6 px-6 py-3 bg-yellow-400 text-gray-900 font-bold rounded-lg hover:bg-yellow-500 transition"
                  >
                    Analyze Another Video →
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Features */}
          <div id="features" className="grid md:grid-cols-3 gap-8 mb-16">
            <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-8 border border-white/10 hover:border-yellow-400/50 transition">
              <div className="text-5xl mb-4" aria-hidden={true}>📹</div>
              <h3 className="text-2xl font-bold text-white mb-3">Real-Time Analysis</h3>
              <p className="text-gray-300 leading-relaxed">
                AI analyzes your form instantly using computer vision. Get immediate feedback on posture, angles, and technique.
              </p>
            </div>

            <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-8 border border-white/10 hover:border-yellow-400/50 transition">
              <div className="text-5xl mb-4" aria-hidden={true}>🧠</div>
              <h3 className="text-2xl font-bold text-white mb-3">Learn the "Why"</h3>
              <p className="text-gray-300 leading-relaxed">
                Don't just follow instructions. Understand biomechanics, muscle engagement, and injury prevention principles.
              </p>
            </div>

            <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-8 border border-white/10 hover:border-yellow-400/50 transition">
              <div className="text-5xl mb-4" aria-hidden={true}>🎯</div>
              <h3 className="text-2xl font-bold text-white mb-3">Personalized Coaching</h3>
              <p className="text-gray-300 leading-relaxed">
                Adaptive plans that evolve with your progress. Form scoring, rep counting, and intelligent progressions.
              </p>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16 text-center">
            <div>
              <div className="text-4xl font-bold text-yellow-400 mb-2">10+</div>
              <div className="text-gray-400">Exercises Supported</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-yellow-400 mb-2">95%</div>
              <div className="text-gray-400">Form Accuracy</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-yellow-400 mb-2">&lt;1s</div>
              <div className="text-gray-400">Analysis Time</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-yellow-400 mb-2">100%</div>
              <div className="text-gray-400">Free Alpha</div>
            </div>
          </div>

          {/* Waitlist */}
          <div id="waitlist" className="bg-gradient-to-r from-yellow-400/20 to-orange-400/20 backdrop-blur-xl rounded-3xl p-8 sm:p-12 border border-yellow-400/30">
            <div className="max-w-2xl mx-auto text-center">
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">Join the Alpha Waitlist</h2>
              <p className="text-gray-300 mb-8 text-lg">Get early access + lifetime Pro membership for free 🎁</p>

              {!submitted ? (
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid sm:grid-cols-2 gap-4">
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Your name"
                      required
                      className="px-6 py-4 rounded-xl text-gray-900 text-lg bg-white focus:ring-4 focus:ring-yellow-400 outline-none"
                    />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="your@email.com"
                      required
                      className="px-6 py-4 rounded-xl text-gray-900 text-lg bg-white focus:ring-4 focus:ring-yellow-400 outline-none"
                    />
                  </div>

                  {error && (
                    <div className="text-red-400 font-semibold bg-red-900/30 p-4 rounded-xl">
                      {error}
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full px-8 py-4 bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-bold rounded-xl text-lg transition disabled:opacity-50 shadow-lg hover:shadow-xl"
                  >
                    {loading ? 'Joining...' : 'Join Waitlist 🚀'}
                  </button>

                  <p className="text-gray-400 text-sm">
                    ✓ No credit card required • ✓ Cancel anytime • ✓ Alpha testers get lifetime Pro
                  </p>
                </form>
              ) : (
                <div className="p-8 bg-green-500/20 rounded-2xl border border-green-400/30">
                  <div className="text-6xl mb-4" aria-hidden={true}>🎉</div>
                  <div className="text-3xl text-green-400 font-bold mb-2">You're on the list!</div>
                  <p className="text-gray-300 text-lg">Check your email for confirmation and next steps</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 border-t border-white/10">
        <div className="max-w-6xl mx-auto text-center">
          <div className="flex justify-center items-center gap-6 mb-6">
            <a
              href="https://github.com/Vamsikrishnv/fitmentor-form-checker"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white transition"
            >
              GitHub
            </a>
            <span className="text-gray-600">•</span>
            <a href="#features" className="text-gray-400 hover:text-white transition">Features</a>
            <span className="text-gray-600">•</span>
            <a href="#demo" className="text-gray-400 hover:text-white transition">Demo</a>
          </div>
          <p className="text-gray-500 text-sm">© 2025 FitMentor AI. Built in public by Krishna.</p>
        </div>
      </footer>
    </div>
  )
}

export default App
