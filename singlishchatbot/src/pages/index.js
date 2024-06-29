import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ChatComponent = () => {
  const [inputValue, setInputValue] = useState('');
  const [chatLog, setChatLog] = useState([]);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws/1');
    setWs(socket);

    socket.onopen = () => {
      console.log('WebSocket connection opened');
    };

    socket.onmessage = (event) => {
      console.log('Raw WebSocket message data:', event.data);

      try {
        const message = JSON.parse(event.data);
        setChatLog((prevChatLog) => [...prevChatLog, { type: 'bot', message: message.message }]);
      } catch (error) {
        console.error('Failed to parse WebSocket message as JSON:', error);
        setChatLog((prevChatLog) => [...prevChatLog, { type: 'bot', message: event.data }]);
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    socket.onclose = () => {
      console.log('WebSocket connection closed');
    };

    return () => {
      socket.close();
    };
  }, []);

  const handleSubmit = (event) => {
    event.preventDefault();
    setChatLog((prevChatLog) => [...prevChatLog, { type: 'user', message: inputValue }]);
    sendMessage(inputValue);
    setInputValue('');
  };

  const sendMessage = async (message) => {
    try {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(message);
      } else {
        console.error('WebSocket is not open');
      }

      const response = await axios.post('http://localhost:8000/chatbot/', { message });
      const botResponse = response.data.response;
      setChatLog((prevChatLog) => [...prevChatLog, { type: 'bot', message: botResponse }]);
    } catch (error) {
      console.error('Error:', error.response ? error.response.data : error.message);
    }
  };

  return (
    <div className="container mx-auto max-w-[700px]">
      <div className="flex flex-col h-screen bg-gray-900">
        <h1 className="bg-gradient-to-r from-blue-500 to-purple-500 text-transparent bg-clip-text text-center py-3 font-bold text-6xl">Combank-ChatGPT</h1>
        <div className="flex-grow p-6">
          <div className="flex flex-col space-y-4">
            {chatLog.map((message, index) => (
              <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`${message.type === 'user' ? 'bg-purple-500' : 'bg-gray-800'} rounded-lg p-4 text-white max-w-sm`}>
                  {message.message}
                </div>
              </div>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="flex rounded-lg border border-gray-700 bg-gray-800">
            <input
              type="text"
              className="flex-grow px-4 py-2 bg-transparent text-white outline-none placeholder-gray-500"
              placeholder="Type your message..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
            />
            <button className="bg-purple-500 rounded-lg px-4 py-2 font-semibold outline-none hover:bg-purple-600 transition-colors duration-300" type="submit">
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatComponent;
