import { useState } from 'react'

function App() {
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Use production API in production, localhost in dev
  const API_URL = import.meta.env.PROD 
    ? 'https://YOUR_RAILWAY_URL_HERE.up.railway.app'
    : 'http://localhost:8000'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${API_URL}/api/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          name: name,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setSubmitted(true)
        setEmail('')
        setName('')
        
        setTimeout(() => {
          setSubmitted(false)
        }, 5000)
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-pink-900">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20">
        <div className="max-w-4xl mx-auto text-center">
          
          {/* Hero Section - Responsive */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-4 sm:mb-6">
            🏋️ FitMentor AI
          </h1>
          
          <p className="text-2xl sm:text-3xl text-gray-200 mb-3 sm:mb-4">
            Your AI Fitness Coach That Teaches <span className="text-yellow-400">Why</span>
          </p>
          
          <p className="text-lg sm:text-xl text-gray-300 mb-8 sm:mb-12 px-4">
            Real-time form checking • Biomechanics education • Personalized feedback
          </p>
          
          {/* Problem Section - Responsive Grid */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 sm:p-8 mb-8 sm:mb-12">
            <h2 className="text-xl sm:text-2xl font-bold text-white mb-4">
              The Problem with Fitness Apps
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 text-left">
              <div className="flex flex-col items-center sm:items-start text-center sm:text-left">
                <div className="text-3xl sm:text-4xl mb-2">❌</div>
                <p className="text-gray-200 text-sm sm:text-base">Just track reps - don't teach</p>
              </div>
              <div className="flex flex-col items-center sm:items-start text-center sm:text-left">
                <div className="text-3xl sm:text-4xl mb-2">❌</div>
                <p className="text-gray-200 text-sm sm:text-base">No form feedback - risk injury</p>
              </div>
              <div className="flex flex-col items-center sm:items-start text-center sm:text-left">
                <div className="text-3xl sm:text-4xl mb-2">❌</div>
                <p className="text-gray-200 text-sm sm:text-base">Generic plans - no education</p>
              </div>
            </div>
          </div>
          
          {/* Features Section - Responsive Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 sm:gap-8 mb-8 sm:mb-12">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
              <div className="text-4xl sm:text-5xl mb-4">📹</div>
              <h3 className="text-lg sm:text-xl font-bold text-white mb-2">
                Real-Time Form Checking
              </h3>
              <p className="text-gray-300 text-sm sm:text-base">
                AI analyzes your form instantly
              </p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
              <div className="text-4xl sm:text-5xl mb-4">🧠</div>
              <h3 className="text-lg sm:text-xl font-bold text-white mb-2">
                Learn the "Why"
              </h3>
              <p className="text-gray-300 text-sm sm:text-base">
                Understand biomechanics
              </p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
              <div className="text-4xl sm:text-5xl mb-4">🎯</div>
              <h3 className="text-lg sm:text-xl font-bold text-white mb-2">
                Personalized Coach
              </h3>
              <p className="text-gray-300 text-sm sm:text-base">
                Adapts to YOUR goals
              </p>
            </div>
          </div>
          
          {/* Waitlist Form - Responsive */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 sm:p-8">
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3 sm:mb-4">
              Join the Alpha Waitlist
            </h2>
            <p className="text-gray-300 mb-4 sm:mb-6 text-sm sm:text-base">
              Get early access + lifetime Pro for free 🎁
            </p>
            
            {!submitted ? (
              <form onSubmit={handleSubmit} className="max-w-md mx-auto px-4">
                <div className="space-y-3 sm:space-y-4">
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Your name"
                    required
                    className="w-full px-4 sm:px-6 py-3 sm:py-4 rounded-lg text-gray-900 text-base sm:text-lg"
                  />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your.email@example.com"
                    required
                    className="w-full px-4 sm:px-6 py-3 sm:py-4 rounded-lg text-gray-900 text-base sm:text-lg"
                  />
                  
                  {error && (
                    <div className="text-red-400 font-semibold bg-red-900/30 p-3 rounded text-sm sm:text-base">
                      {error}
                    </div>
                  )}
                  
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full px-6 sm:px-8 py-3 sm:py-4 bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-bold rounded-lg text-base sm:text-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Joining...' : 'Join Waitlist 🚀'}
                  </button>
                </div>
              </form>
            ) : (
              <div className="text-center p-4 sm:p-6">
                <div className="text-4xl sm:text-5xl mb-3 sm:mb-4">🎉</div>
                <div className="text-2xl sm:text-3xl text-green-400 font-bold mb-2">
                  You're on the list!
                </div>
                <p className="text-gray-300 text-sm sm:text-base">
                  Check your email for confirmation
                </p>
              </div>
            )}
          </div>
          
          {/* GitHub Link - Responsive */}
          <div className="mt-8 sm:mt-12">
            <a 
              href="https://github.com/Vamsikrishnv/fitmentor-form-checker"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 underline text-base sm:text-lg inline-block"
            >
              ⭐ Star on GitHub
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
