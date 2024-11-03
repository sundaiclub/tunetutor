'use client'

import { useState } from 'react'

const questions = [
  { id: 1, text: "What's your preferred learning voice?", options: ["Male", "Female", "Surprise me!"] },
  { id: 2, text: "Want to learn or just make something to go viral?", options: ["Educate me", "Idc, make me go viral!"] },
  { id: 3, text: "What's your favorite music genre?", options: ["Pop", "Rock", "Hip Hop", "Classical", "Electronic"] },
]

export default function Questionnaire() {
  const [answers, setAnswers] = useState<Record<number, string>>({})

  const handleAnswer = (questionId: number, answer: string) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }))
  }

  return (
    <section className="w-full bg-st-tropaz text-white py-16">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold mb-8 text-center">
          To make your learning experience personal, answer a few questions!
        </h2>
        <div className="max-w-md mx-auto space-y-6">
          {questions.map(question => (
            <div key={question.id} className="bg-white text-st-tropaz p-4 rounded-md">
              <p className="font-semibold mb-2">{question.text}</p>
              <select
                value={answers[question.id] || ''}
                onChange={(e) => handleAnswer(question.id, e.target.value)}
                className="w-full p-2 border border-bright-green rounded-md focus:outline-none focus:ring-2 focus:ring-bright-green"
              >
                <option value="">Select an option</option>
                {question.options.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>
          ))}
          <button className="w-full bg-bright-green text-white px-4 py-2 rounded-md hover:bg-opacity-90 transition-colors">
            Generate My Song
          </button>
        </div>
      </div>
    </section>
  )
}