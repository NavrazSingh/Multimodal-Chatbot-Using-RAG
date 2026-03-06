import React, { useState, useRef, useEffect } from 'react';
import { Send, Image as ImageIcon, Mic, X, Loader2, Volume2 } from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from "react-markdown";


const API_BASE_URL = 'http://localhost:8000';

const App = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your Multimodal RAG Assistant. How can I help you today?' }
  ]);
  const [inputText, setInputText] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedAudio, setRecordedAudio] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const chatEndRef = useRef(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setRecordedAudio(audioBlob);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone:", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSendMessage = async () => {
    if (!inputText.trim() && !selectedImage && !recordedAudio) return;

    const userMessage = {
      role: 'user',
      content: inputText || (recordedAudio ? "🎤 Voice Message" : ""),
      image: imagePreview
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setSelectedImage(null);
    setImagePreview(null);
    setRecordedAudio(null);
    setIsLoading(true);

    const formData = new FormData();
    if (inputText) formData.append('text_query', inputText);
    if (selectedImage) formData.append('image', selectedImage);
    if (recordedAudio) formData.append('voice', recordedAudio, 'recording.wav');

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, formData);
      const botMessage = {
        role: 'assistant',
        content: response.data.answer,
        image_description: response.data.image_description,
        transcribed_text: response.data.transcribed_text
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4 bg-transparent text-white font-sans">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-purple-500 mb-2">
          Multimodal RAG AI
        </h1>
        <p className="text-gray-400 text-sm">Text • Image • Voice • Fast Retrieval</p>
      </header>

      <div className="flex-1 overflow-y-auto mb-6 space-y-4 px-2 custom-scrollbar">
        <AnimatePresence>
          {messages.map((msg, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 shadow-lg ${
                  msg.role === 'user'
                    ? 'bg-primary-600 text-white rounded-br-none'
                    : 'glass-dark text-gray-100 rounded-bl-none border border-gray-700'
                }`}
              >
                {msg.image && (
                  <img src={msg.image} alt="User upload" className="w-full h-auto rounded-lg mb-2 max-h-60 object-cover" />
                )}
                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                
                {msg.transcribed_text && (
                  <div className="mt-2 pt-2 border-t border-gray-600 border-opacity-30 text-xs italic text-blue-400 flex items-center">
                    <Volume2 className="w-3 h-3 mr-1" /> Transcribed: {msg.transcribed_text}
                  </div>
                )}
                {msg.image_description && (
                  <div className="mt-2 pt-2 border-t border-gray-600 border-opacity-30 text-xs italic text-gray-400">
                    Image: {msg.image_description}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
          {isLoading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
              <div className="glass-dark rounded-2xl px-4 py-2 flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin text-primary-400" />
                <span className="text-sm text-gray-400">Thinking...</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={chatEndRef} />
      </div>

      <div className="glass-dark rounded-3xl p-2 border border-gray-800 shadow-2xl relative">
        {imagePreview && (
          <div className="absolute -top-24 left-4 p-2 glass rounded-xl flex items-center group">
            <img src={imagePreview} className="w-16 h-16 rounded-md object-cover" alt="Preview" />
            <button
              onClick={() => { setSelectedImage(null); setImagePreview(null); }}
              className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        )}
        
        <div className="flex items-center space-x-2 p-1">
          <label className="p-2 cursor-pointer hover:bg-gray-800 rounded-full transition-colors">
            <ImageIcon className="w-6 h-6 text-gray-400 hover:text-primary-400" />
            <input type="file" className="hidden" accept="image/*" onChange={handleImageChange} />
          </label>
          
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`p-2 rounded-full transition-colors ${
              isRecording ? 'bg-red-500/20 text-red-500 animate-pulse' : 'hover:bg-gray-800 text-gray-400 hover:text-red-500'
            }`}
          >
            <Mic className="w-6 h-6" />
          </button>

          <input
            type="text"
            placeholder="Ask anything..."
            className="flex-1 bg-transparent border-none focus:ring-0 text-white px-2 py-2 placeholder-gray-500"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          />

          <button
            onClick={handleSendMessage}
            // disabled={(!inputText.trim() && !selectedImage) || isLoading}
            disabled={(!inputText.trim() && !selectedImage && !recordedAudio) || isLoading}
            className="p-3 bg-primary-600 hover:bg-primary-500 rounded-2xl text-white transition-all transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:grayscale disabled:scale-100 shadow-lg shadow-primary-900/40"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;

