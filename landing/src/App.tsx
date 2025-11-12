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

  const isProd = (import.meta as any).env?.PROD ?? false
  const API_URL = isProd ? 'https://fitmentor-form-checker.onrender.com' : 'http://localhost:8000'

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
        setError(data.detail || 'Something went wrong.')
      }
    } catch (err) {
      setError('Failed to join waitlist.')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    if (!selectedFile) return
    setAnalyzing(true)
    setError('')
    setAnalysisResult(null)
    try {
      const formData = new FormData()
      formData.append('video', selectedFile)
      formData.append('exercise', exercise)
      const response = await fetch(`${API_URL}/api/analyze`, { method: 'POST', body: formData })
      if (!response.ok) throw new Error('Analysis failed')
      const result = await response.json()
      setAnalysisResult(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed')
    } finally {
      setAnalyzing(false)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      if (file.size / 1024 / 1024 > 25) {
        alert('File too large! Max 25MB.')
        e.target.value = ''
        return
      }
      setSelectedFile(file)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <nav className="container mx-auto px-4 py-6">
        <div className="flex justify-between items-center">
          <div className="text-white font-bold text-2xl">FitMentor AI</div>
          <div className="hidden md:flex gap-8 text-gray-300">
            <a href="#features" className="hover:text-white transition">Features</a>
            <a href="#demo" className="hover:text-white transition">Demo</a>
            <a href="#waitlist" className="hover:text-white transition">Join Beta</a>
          </div>
          <a href="https://github.com/Vamsikrishnv/fitmentor-form-checker" target="_blank" rel="noopener noreferrer" className="text-sm px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition">GitHub</a>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-block mb-4 px-4 py-2 bg-yellow-400/20 rounded-full text-yellow-400 text-sm font-semibold">Now in Alpha Testing</div>
            <h1 className="text-5xl sm:text-6xl font-bold text-white mb-6 leading-tight">Your AI Fitness Coach<br />That Teaches <span className="text-yellow-400">Why</span></h1>
            <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">Stop following blindly. Get real-time form analysis, understand biomechanics, and train smarter with AI-powered coaching.</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a href="#waitlist" className="px-8 py-4 bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-bold rounded-lg text-lg transition">Join Waitlist</a>
              <a href="#demo" className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-lg text-lg transition">Try Demo</a>
            </div>
          </div>

          <div id="demo" className="bg-white/5 rounded-3xl p-8 mb-16 border border-white/10">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-white mb-4">Try It Now - Live Demo</h2>
              <p className="text-gray-300">Upload your workout video and get instant AI form analysis</p>
            </div>
            <div className="max-w-2xl mx-auto">
              <label htmlFor="video-upload">
                <div className="border-2 border-dashed border-white/30 rounded-2xl p-12 text-center hover:border-yellow-400 cursor-pointer">
                  {!selectedFile ? (
                    <>
                      <p className="text-white text-xl mb-2 font-semibold">Drop your workout video here</p>
                      <p className="text-gray-400">or click to browse (MP4, AVI, MOV)</p>
                      <div className="mt-6 inline-block px-6 py-3 bg-yellow-400 text-gray-900 font-bold rounded-lg">Choose Video</div>
                    </>
                  ) : (
                    <>
                      <p className="text-white text-xl mb-2 font-semibold">{selectedFile.name}</p>
                      <p className="text-gray-400 mb-4">Ready to analyze</p>
                      <div className="mt-6 space-y-4">
                        <select value={exercise} onChange={(e) => setExercise(e.target.value)} className="w-full px-4 py-3 rounded-lg bg-white/10 text-white border border-white/20 outline-none">
                          <option value="squat">Squat</option>
                          <option value="pushup">Push-up</option>
                          <option value="plank">Plank</option>
                          <option value="lunge">Lunge</option>
                          <option value="deadlift">Deadlift</option>
                        </select>
                        <button onClick={handleAnalyze} disabled={analyzing} className="w-full px-6 py-4 bg-green-500 text-white font-bold rounded-lg hover:bg-green-600 disabled:opacity-50">{analyzing ? 'Analyzing...' : 'Analyze Form'}</button>
                      </div>
                    </>
                  )}
                </div>
              </label>
              <input id="video-upload" type="file" accept="video/*" className="hidden" onChange={handleFileChange} />
              {error && <div className="mt-4 p-4 bg-red-500/20 border border-red-500 rounded-xl"><p className="text-red-400 text-center">{error}</p></div>}
              {analysisResult && (
                <div className="mt-8 bg-white/5 rounded-2xl p-8 border border-white/10">
                  <h3 className="text-3xl font-bold text-white mb-6 text-center">Analysis Results</h3>
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-white/5 rounded-xl p-4 text-center">
                      <div className="text-3xl font-bold text-yellow-400">{analysisResult.form_score ?? '--'}</div>
                      <div className="text-gray-300 text-sm">Form Score</div>
                    </div>
                    <div className="bg-white/5 rounded-xl p-4 text-center">
                      <div className="text-3xl font-bold text-blue-400">{analysisResult.rep_count ?? '--'}</div>
                      <div className="text-gray-300 text-sm">Reps</div>
                    </div>
                  </div>
                  <button onClick={() => { setAnalysisResult(null); setSelectedFile(null); }} className="w-full px-6 py-3 bg-yellow-400 text-gray-900 font-bold rounded-lg">Analyze Another Video</button>
                </div>
              )}
            </div>
          </div>

          <div id="features" className="grid md:grid-cols-3 gap-8 mb-16">
            <div className="bg-white/5 rounded-2xl p-8 border border-white/10">
              <h3 className="text-2xl font-bold text-white mb-3">Real-Time Analysis</h3>
              <p className="text-gray-300">AI analyzes your form instantly using MediaPipe computer vision.</p>
            </div>
            <div className="bg-white/5 rounded-2xl p-8 border border-white/10">
              <h3 className="text-2xl font-bold text-white mb-3">Learn the Why</h3>
              <p className="text-gray-300">Understand biomechanics and injury prevention principles.</p>
            </div>
            <div className="bg-white/5 rounded-2xl p-8 border border-white/10">
              <h3 className="text-2xl font-bold text-white mb-3">Personalized Coaching</h3>
              <p className="text-gray-300">Adaptive workout plans based on your goals and equipment.</p>
            </div>
          </div>

          <div id="waitlist" className="bg-gradient-to-r from-yellow-400/20 to-orange-400/20 rounded-3xl p-8 border border-yellow-400/30">
            <div className="max-w-2xl mx-auto text-center">
              <h2 className="text-3xl font-bold text-white mb-4">Join the Alpha Waitlist</h2>
              <p className="text-gray-300 mb-8">Get early access + lifetime Pro membership</p>
              {!submitted ? (
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid sm:grid-cols-2 gap-4">
                    <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" required className="px-6 py-4 rounded-xl text-gray-900 bg-white outline-none" />
                    <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="your@email.com" required className="px-6 py-4 rounded-xl text-gray-900 bg-white outline-none" />
                  </div>
                  {error && <div className="text-red-400 font-semibold bg-red-900/30 p-4 rounded-xl">{error}</div>}
                  <button type="submit" disabled={loading} className="w-full px-8 py-4 bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-bold rounded-xl disabled:opacity-50">{loading ? 'Joining...' : 'Join Waitlist'}</button>
                </form>
              ) : (
                <div className="p-8 bg-green-500/20 rounded-2xl border border-green-400/30">
                  <div className="text-3xl text-green-400 font-bold mb-2">You're on the list!</div>
                  <p className="text-gray-300">Check your email for next steps</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <footer className="container mx-auto px-4 py-12 border-t border-white/10">
        <div className="text-center">
          <p className="text-gray-500 text-sm">© 2025 FitMentor AI • Built in public</p>
        </div>
      </footer>
    </div>
  )
}

export default App