import { useState } from 'react'

function App() {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('Email:', email)
    setSubmitted(true)
    setTimeout(() => {
      setSubmitted(false)
      setEmail('')
    }, 3000)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-pink-900">
      <div className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center">
          
          <h1 className="text-6xl font-bold text-white mb-6">
            🏋️ FitMentor AI
          </h1>
          
          <p className="text-3xl text-gray-200 mb-4">
            Your AI Fitness Coach That Teaches <span className="text-yellow-400">Why</span>
          </p>
          
          <p className="text-xl text-gray-300 mb-12">
            Real-time form checking • Biomechanics education • Personalized feedback
          </p>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 mb-12">
            <h2 className="text-2xl font-bold text-white mb-4">
              The Problem with Fitness Apps
            </h2>
            <div className="grid md:grid-cols-3 gap-6 text-left">
              <div>
                <div className="text-4xl mb-2">❌</div>
                <p className="text-gray-200">Just track reps - don't teach</p>
              </div>
              <div>
                <div className="text-4xl mb-2">❌</div>
                <p className="text-gray-200">No form feedback - risk injury</p>
              </div>
              <div>
                <div className="text-4xl mb-2">❌</div>
                <p className="text-gray-200">Generic plans - no education</p>
              </div>
            </div>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
              <div className="text-5xl mb-4">📹</div>
              <h3 className="text-xl font-bold text-white mb-2">
                Real-Time Form Checking
              </h3>
              <p className="text-gray-300">
                AI analyzes your form instantly
              </p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
              <div className="text-5xl mb-4">🧠</div>
              <h3 className="text-xl font-bold text-white mb-2">
                Learn the "Why"
              </h3>
              <p className="text-gray-300">
                Understand biomechanics
              </p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
              <div className="text-5xl mb-4">🎯</div>
              <h3 className="text-xl font-bold text-white mb-2">
                Personalized Coach
              </h3>
              <p className="text-gray-300">
                Adapts to YOUR goals
              </p>
            </div>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8">
            <h2 className="text-3xl font-bold text-white mb-4">
              Join the Alpha Waitlist
            </h2>
            <p className="text-gray-300 mb-6">
              Get early access + lifetime Pro for free 🎁
            </p>
            
            {!submitted ? (
              <form onSubmit={handleSubmit} className="max-w-md mx-auto">
                <div className="flex flex-col sm:flex-row gap-4">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your.email@example.com"
                    required
                    className="flex-1 px-6 py-4 rounded-lg text-gray-900 text-lg"
                  />
                  <button
                    type="submit"
                    className="px-8 py-4 bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-bold rounded-lg text-lg transition"
                  >
                    Join Waitlist
                  </button>
                </div>
              </form>
            ) : (
              <div className="text-2xl text-green-400 font-bold">
                ✅ You're on the list!
              </div>
            )}
          </div>
          
          <div className="mt-12">
            <a 
              href="https://github.com/Vamsikrishnv/fitmentor-form-checker"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 underline text-lg"
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