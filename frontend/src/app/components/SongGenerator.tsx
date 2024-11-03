'use client'

import { useState } from 'react'
import { Loader2 } from 'lucide-react'

async function makeSong(query: string, version: number) {
  try {
    const response = await fetch('https://tunetutor.onrender.com/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, version }),
    })
    const result = await response.json()
    return result
  } catch (error) {
    console.error('Error generating song:', error)
    throw error
  }
}

export default function SongGenerator() {
  const [isGenerating, setIsGenerating] = useState(false)
  const [songUrls, setSongUrls] = useState<string[] | null>(null)
  const [query, setQuery] = useState('')
  const [version, setVersion] = useState(1)
  const [error, setError] = useState<string | null>(null)

  const handleGenerateSong = async () => {
    setIsGenerating(true)
    setError(null)
    try {
      const result = await makeSong(query, version)
      setSongUrls(result)
    } catch (err) {
      setError('Failed to generate song. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <section className="w-full bg-white py-16">
      <div className="container mx-auto px-4 text-center">
        <h2 className="text-3xl font-bold text-st-tropaz mb-8">
          Generate Your Learning Song
        </h2>
        <div className="mb-6">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your topic or question"
            className="w-full max-w-md px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-bright-green"
          />
        </div>
        <div className="mb-6">
          <label className="inline-flex items-center mr-4">
            <input
              type="radio"
              value="1"
              checked={version === 1}
              onChange={() => setVersion(1)}
              className="form-radio text-bright-green"
            />
            <span className="ml-2">Educate Me</span>
          </label>
          <label className="inline-flex items-center">
            <input
              type="radio"
              value="2"
              checked={version === 2}
              onChange={() => setVersion(2)}
              className="form-radio text-bright-green"
            />
            <span className="ml-2">Go Viral</span>
          </label>
        </div>
        {!songUrls && (
          <button
            onClick={handleGenerateSong}
            disabled={isGenerating || !query}
            className="bg-bright-green text-white px-6 py-3 rounded-md text-lg font-semibold hover:bg-opacity-90 transition-colors flex items-center justify-center mx-auto disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <>
                <Loader2 className="animate-spin mr-2" />
                Generating...
              </>
            ) : (
              'Generate My Song'
            )}
          </button>
        )}
        {isGenerating && (
          <div className="mt-8">
            <div className="w-full h-2 bg-gray-200 rounded-full">
              <div className="w-1/2 h-full bg-bright-green rounded-full animate-pulse"></div>
            </div>
            <p className="mt-2 text-st-tropaz">Creating your personalized learning song...</p>
          </div>
        )}
        {error && (
          <p className="mt-4 text-red-500">{error}</p>
        )}
        {songUrls && (
          <div className="mt-8">
            <p className="text-st-tropaz mb-4">Your song is ready!</p>
            <div className="space-y-2">
              {songUrls.map((url, index) => (
                <div key={index} className="break-all">
                  <a href={url} target="_blank" rel="noopener noreferrer" className="text-bright-green hover:underline">
                    Song URL {index + 1}
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  )
}