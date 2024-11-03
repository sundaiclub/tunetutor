'use client'

import Link from 'next/link'
import { BookOpen, Music, Settings } from 'lucide-react'

export default function Header() {
  return (
    <header className="w-full bg-gradient-to-r from-st-tropaz to-bright-green text-white shadow-md">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link href="/" className="flex items-center space-x-2 text-2xl font-bold hover:text-white/80 transition-colors">
          <Music className="h-8 w-8" />
          <span>Tunetutor</span>
        </Link>
        <nav>
          <ul className="flex space-x-6">
            <li>
              <Link href="/how-it-works" className="flex items-center space-x-1 hover:text-white/80 transition-colors">
                <BookOpen className="h-5 w-5" />
                <span>How it Works</span>
              </Link>
            </li>
            <li>
              <Link href="/contact" className="flex items-center space-x-1 hover:text-white/80 transition-colors">
                <Settings className="h-5 w-5" />
                <span>Contact</span>
              </Link>
            </li>
          </ul>
        </nav>
        <button className="bg-white text-st-tropaz px-4 py-2 rounded-full font-semibold hover:bg-opacity-90 transition-colors transform hover:scale-105">
          Login
        </button>
      </div>
    </header>
  )
}