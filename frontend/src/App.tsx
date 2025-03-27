import { useState, useRef, useEffect } from 'react';
import { Send, BookOpen, GraduationCap } from 'lucide-react';

interface Message {
  type: 'user' | 'ai';
  content: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Add initial welcome message
    setMessages([
      {
        type: 'ai',
        content: "Hello! I'm your AI tutor. Please type the name of the course you'd like to study. Available courses: Python, Excel, C++"
      }
    ]);
  }, []);

  useEffect(() => {
    // Auto scroll to bottom when new messages arrive
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await response.json();
      setMessages(prev => [...prev, { type: 'ai', content: data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { type: 'ai', content: '⚠️ Error communicating with the server' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = (message: Message, index: number) => {
    if (message.type === 'user') {
      return (
        <div key={index} className="flex justify-end mb-4">
          <div className="bg-blue-500 text-white rounded-2xl rounded-br-sm px-4 py-2 max-w-[70%]">
            {message.content}
          </div>
        </div>
      );
    }

    // Check for special AI messages
    if (message.content.startsWith('📘 Module') || message.content.startsWith('✅ Selected')) {
      return (
        <div key={index} className="bg-green-50 border-l-4 border-green-500 p-4 mb-4">
          <div className="flex items-center">
            <BookOpen className="w-5 h-5 mr-2 text-green-600" />
            <p className="text-green-700">{message.content}</p>
          </div>
        </div>
      );
    }

    if (message.content.includes('🎉 Course completed')) {
      return (
        <div key={index} className="bg-yellow-50 border-l-4 border-yellow-500 p-4 mb-4">
          <div className="flex items-center">
            <GraduationCap className="w-5 h-5 mr-2 text-yellow-600" />
            <p className="text-yellow-700">{message.content}</p>
          </div>
        </div>
      );
    }

    return (
      <div key={index} className="flex mb-4">
        <div className="bg-gray-100 rounded-2xl rounded-bl-sm px-4 py-2 max-w-[70%]">
          {message.content}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <GraduationCap className="w-8 h-8 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">AI Tutor</h1>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-8">
        <div 
          ref={chatContainerRef}
          className="bg-white rounded-lg shadow-md h-[600px] mb-4 p-4 overflow-y-auto"
        >
          {messages.map((message, index) => renderMessage(message, index))}
          {isLoading && (
            <div className="flex justify-center">
              <div className="animate-pulse text-gray-400">Thinking...</div>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message or course name..."
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="bg-blue-500 text-white rounded-lg px-6 py-2 hover:bg-blue-600 transition-colors disabled:bg-blue-300 flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            Send
          </button>
        </form>
      </main>
    </div>
  );
}

export default App;