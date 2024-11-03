'use client';

import { useState } from 'react';
import axios from 'axios';
import { Type, ArrowRight } from 'lucide-react';

export default function TopicInput() {
  const [topic, setTopic] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [responseData, setResponseData] = useState<{
    lyrics: string;
    style: string;
    urls: string[];
  } | null>(null);

  const makeRequest = async () => {
    try {
        const response = await axios.post('/api/generate', {
            query: topic,
            version: 1,
          });
      setResponseData(response.data);
    } catch (error) {
      console.error('Error generating song, retrying in 1 second...', error);
      // Wait for 1 second before retrying
      await new Promise((resolve) => setTimeout(resolve, 1000));
      await makeRequest(); // Retry after delay
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setResponseData(null);

    try {
      await makeRequest();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section id="topic-input" className="w-full bg-white py-16">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-st-tropaz mb-8 text-center">
          What do you want to learn today?
        </h2>
        <div className="max-w-md mx-auto">
          <form onSubmit={handleSubmit}>
            <div className="flex justify-center space-x-4 mb-6">
              <button
                type="button"
                className="flex items-center px-4 py-2 rounded-full bg-st-tropaz text-white"
              >
                <Type className="mr-2 h-5 w-5" />
                Type a topic
              </button>
            </div>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Type a topic here..."
              className="w-full px-4 py-3 border-2 border-st-tropaz rounded-md focus:outline-none focus:ring-2 focus:ring-bright-green text-lg text-black"
            />
            <button
              type="submit"
              className="w-full mt-6 bg-bright-green text-white px-6 py-3 rounded-full text-lg font-semibold hover:bg-opacity-90 transition-colors transform hover:scale-105 flex items-center justify-center"
            >
              Next
              <ArrowRight className="ml-2 h-5 w-5" />
            </button>
          </form>

          {isLoading && <p className="mt-4 text-center text-st-tropaz">Generating...</p>}

          {responseData && (
            <div className="mt-8 p-6 bg-gray-100 rounded-lg shadow-md">
              <h3 className="text-xl font-bold text-st-tropaz mb-4">Generated Song Details:</h3>
              
              <h4 className="text-lg font-semibold text-st-tropaz mb-2">Lyrics:</h4>
              <p className="bg-white p-4 rounded-lg text-black whitespace-pre-line mb-4">
                {responseData.lyrics}
              </p>

              <h4 className="text-lg font-semibold text-st-tropaz mb-2">Style:</h4>
              <p className="bg-white p-4 rounded-lg text-black mb-4">
                {responseData.style}
              </p>

              <h4 className="text-lg font-semibold text-st-tropaz mb-2">URLs:</h4>
              <ul className="list-disc list-inside bg-white p-4 rounded-lg">
                {responseData.urls.map((url, index) => (
                  <li key={index}>
                    <a href={url} target="_blank" rel="noopener noreferrer" className="text-bright-green hover:underline">
                      {url}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}