import Header from './components/Header'
import HeroSection from './components/HeroSection'
import TopicInput from './components/TopicInput'
import Questionnaire from './components/Questionnaire'
import SongGenerator from './components/SongGenerator'
import SongPreview from './components/SongPreview'
import Footer from './components/Footer'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between">
      <Header />
      <HeroSection />
      <TopicInput />
      <Footer />
    </main>
  )
}