import Link from 'next/link'
import { ArrowRight, BookOpen, Music, Headphones } from 'lucide-react'

export default function HowItWorks() {
  return (
    <div className="container mx-auto px-4 py-12">
      <h1 className="text-4xl font-bold text-st-tropaz mb-8 text-center">How Tunetutor Works</h1>
      <div className="grid md:grid-cols-3 gap-8">
        <StepCard
          icon={<BookOpen className="h-12 w-12 text-st-tropaz" />}
          title="1. Choose Your Topic"
          description="Select a subject you want to learn or upload study materials."
        />
        <StepCard
          icon={<Music className="h-12 w-12 text-st-tropaz" />}
          title="2. Generate Your Song"
          description="Our AI creates a unique, catchy tune based on your topic."
        />
        <StepCard
          icon={<Headphones className="h-12 w-12 text-st-tropaz" />}
          title="3. Learn and Enjoy"
          description="Listen to your personalized educational song and start learning!"
        />
      </div>
      <div className="mt-12 text-center">
        <Link
          href="/"
          className="inline-flex items-center bg-bright-green text-white px-6 py-3 rounded-full font-semibold hover:bg-opacity-90 transition-colors"
        >
          Get Started
          <ArrowRight className="ml-2 h-5 w-5" />
        </Link>
      </div>
    </div>
  )
}

function StepCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-center mb-4">{icon}</div>
      <h2 className="text-xl font-semibold text-st-tropaz mb-2">{title}</h2>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}