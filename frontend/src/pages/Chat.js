<<<<<<< HEAD
import React, { useEffect, useState, useRef } from 'react';
=======
import React, { useEffect, useState, useRef, useCallback } from 'react';
>>>>>>> 17c6933 (initial update)
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { authService } from '../services/auth';
import Navbar from '../components/Navbar';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card } from '../components/ui/card';
import { toast } from 'sonner';

export default function Chat() {
  const { groupId } = useParams();
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
<<<<<<< HEAD
  const [ws, setWs] = useState(null);
  const [connected, setConnected] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchMessages();
    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [groupId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchMessages = async () => {
    try {
      const response = await api.get(`/groups/${groupId}/messages`);
      setMessages(response.data);
    } catch (error) {
      toast.error('Failed to load messages');
    }
  };

  const connectWebSocket = () => {
=======
  const wsRef = useRef(null);
  const [connected, setConnected] = useState(false);
  const messagesEndRef = useRef(null);

  const fetchMessages = useCallback(async () => {
    try {
      const response = await api.get(`/groups/${groupId}/messages`);
      // Normalize incoming messages so each has `uid` and `sender_uid` fields (backend may use uid/sender_uid)
      const normalized = response.data.map((m) => ({
        ...m,
        id: m.id ?? m.uid,
        uid: m.uid ?? m.id,
        sender_uid: m.sender_uid ?? m.sender_id,
      }));
      setMessages(normalized);
    } catch (error) {
      toast.error('Failed to load messages');
    }
  }, [groupId]);

  const connectWebSocket = useCallback(() => {
>>>>>>> 17c6933 (initial update)
    const token = authService.getToken();
    const wsUrl = process.env.REACT_APP_BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://');
    const socket = new WebSocket(`${wsUrl}/api/ws/chat/${groupId}?token=${token}`);

    socket.onopen = () => {
<<<<<<< HEAD
=======
      wsRef.current = socket;
>>>>>>> 17c6933 (initial update)
      setConnected(true);
      console.log('WebSocket connected');
    };

    socket.onmessage = (event) => {
<<<<<<< HEAD
      const message = JSON.parse(event.data);
      setMessages((prev) => [...prev, message]);
=======
      const raw = JSON.parse(event.data);
      const message = {
        ...raw,
        id: raw.id ?? raw.uid,
        uid: raw.uid ?? raw.id,
        sender_uid: raw.sender_uid ?? raw.sender_id,
      };
      setMessages((prev) => {
        // If server-provided uid already exists, ignore
        if (message.uid && prev.some((m) => m.uid === message.uid)) return prev;

        // If this message came from the current user, try to reconcile with a pending local message
        if (message.sender_uid && user?.uid && message.sender_uid === user.uid) {
          const serverTime = new Date(message.created_at).getTime();
          const pendingIndex = prev.findIndex((m) => m.pending && m.sender_uid === user.uid && m.content === message.content && Math.abs(new Date(m.created_at).getTime() - serverTime) < 15000);
          if (pendingIndex !== -1) {
            const next = [...prev];
            next[pendingIndex] = message; // replace pending local with authoritative server message
            return next;
          }
        }

        // Generic duplicate check by uid or (sender+content+time) fallback
        if (prev.some((m) => (m.uid ?? m.id) === message.uid)) return prev;
        return [...prev, message];
      });
>>>>>>> 17c6933 (initial update)
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      toast.error('Chat connection error');
    };

    socket.onclose = () => {
      setConnected(false);
      console.log('WebSocket disconnected');
<<<<<<< HEAD
      
=======
      wsRef.current = null;
>>>>>>> 17c6933 (initial update)
      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        if (groupId) {
          connectWebSocket();
        }
      }, 3000);
    };

<<<<<<< HEAD
    setWs(socket);
  };
=======
  }, [groupId, user?.uid]);

  useEffect(() => {
    fetchMessages();
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [fetchMessages, connectWebSocket]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
>>>>>>> 17c6933 (initial update)

  const handleSendMessage = (e) => {
    e.preventDefault();
    
<<<<<<< HEAD
    if (!newMessage.trim() || !ws || !connected) return;

    ws.send(JSON.stringify({
      content: newMessage.trim()
=======
    if (!newMessage.trim() || !wsRef.current || !connected) return;
    const content = newMessage.trim();

    // Build optimistic local message so user's message appears immediately
    const localUid = `local-${Date.now()}`;
    const optimistic = {
      uid: localUid,
      id: localUid,
      sender_uid: user?.uid,
      sender_name: user?.name,
      content,
      created_at: new Date().toISOString(),
      pending: true,
    };

    setMessages((prev) => [...prev, optimistic]);

    // Send to server (server may echo back the authoritative message)
    wsRef.current.send(JSON.stringify({
      content,
>>>>>>> 17c6933 (initial update)
    }));

    setNewMessage('');
  };

  return (
    <div className="min-h-screen bg-stone-50 flex flex-col" data-testid="chat-page">
      <Navbar />
      
      <div className="flex-1 container mx-auto px-6 py-8 flex flex-col">
        <div className="flex justify-between items-center mb-6">
          <h1 className="font-chivo text-3xl font-bold text-emerald-950">Group Chat</h1>
          <div className="flex items-center space-x-4">
            {connected ? (
              <span className="text-sm text-green-600 flex items-center">
                <span className="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
                Connected
              </span>
            ) : (
              <span className="text-sm text-red-600 flex items-center">
                <span className="w-2 h-2 bg-red-600 rounded-full mr-2"></span>
                Disconnected
              </span>
            )}
            <Link to={`/groups/${groupId}`}>
              <Button variant="outline" className="rounded-full" data-testid="back-to-group-button">
                Back to Group
              </Button>
            </Link>
          </div>
        </div>

        {/* Messages Container */}
        <Card className="flex-1 bg-white rounded-2xl border border-stone-200 shadow-sm p-6 mb-6 overflow-hidden flex flex-col" data-testid="messages-container">
          <div className="flex-1 overflow-y-auto space-y-4 mb-4">
            {messages.length === 0 ? (
              <p className="text-slate-500 text-center py-12">No messages yet. Start the conversation!</p>
<<<<<<< HEAD
            ) : (
              messages.map((msg) => (
                <div 
                  key={msg.id} 
                  className={`flex ${msg.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}
                  data-testid={`message-${msg.id}`}
                >
                  <div className={`max-w-md ${
                    msg.sender_id === user?.id 
                      ? 'bg-emerald-900 text-white' 
                      : 'bg-stone-100 text-emerald-950'
                  } rounded-2xl px-4 py-3`}>
                    {msg.sender_id !== user?.id && (
=======
              ) : (
              messages.map((msg) => (
                <div 
                  key={msg.uid} 
                  className={`flex ${msg.sender_uid === user?.uid ? 'justify-start' : 'justify-end'}`}
                  data-testid={`message-${msg.uid}`}
                >
                  <div className={`max-w-md ${
                    msg.sender_uid === user?.uid 
                      ? 'bg-emerald-900 text-white' 
                      : 'bg-stone-100 text-emerald-950'
                  } rounded-2xl px-4 py-3`}>
                    {msg.sender_uid !== user?.uid && (
>>>>>>> 17c6933 (initial update)
                      <p className="text-xs font-semibold mb-1 opacity-70">{msg.sender_name}</p>
                    )}
                    <p className="text-sm">{msg.content}</p>
                    <p className={`text-xs mt-1 ${
<<<<<<< HEAD
                      msg.sender_id === user?.id ? 'text-emerald-200' : 'text-slate-500'
=======
                      msg.sender_uid === user?.uid ? 'text-emerald-200' : 'text-slate-500'
>>>>>>> 17c6933 (initial update)
                    }`}>
                      {new Date(msg.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
        </Card>

        {/* Message Input */}
        <form onSubmit={handleSendMessage} className="flex space-x-4" data-testid="message-form">
          <Input
            placeholder="Type your message..."
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            className="flex-1 h-12 rounded-full"
            disabled={!connected}
            data-testid="message-input"
          />
          <Button 
            type="submit" 
            className="bg-emerald-900 hover:bg-emerald-800 text-white rounded-full px-8"
            disabled={!connected || !newMessage.trim()}
            data-testid="send-message-button"
          >
            Send
          </Button>
        </form>
      </div>
    </div>
  );
}