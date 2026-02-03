/**
 * WebSocket hook for real-time updates
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { WebSocketManager, TokenManager } from '@/lib/api-client';

interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

interface UseWebSocketOptions {
  userId: number;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

export function useWebSocket(options: UseWebSocketOptions) {
  const { userId, onMessage, onConnect, onDisconnect, onError } = options;
  const wsRef = useRef<WebSocketManager | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  useEffect(() => {
    const token = TokenManager.getAccessToken();
    
    if (!token || !userId) {
      return;
    }

    // Create WebSocket manager
    const ws = new WebSocketManager();
    wsRef.current = ws;

    // Connect
    ws.connect(userId, token, (message: WebSocketMessage) => {
      setLastMessage(message);
      
      if (onMessage) {
        onMessage(message);
      }
    });

    // Handle connection
    setConnected(true);
    if (onConnect) {
      onConnect();
    }

    // Cleanup
    return () => {
      if (wsRef.current) {
        wsRef.current.disconnect();
        wsRef.current = null;
      }
      setConnected(false);
      if (onDisconnect) {
        onDisconnect();
      }
    };
  }, [userId, onMessage, onConnect, onDisconnect]);

  const sendMessage = useCallback((data: any) => {
    if (wsRef.current) {
      wsRef.current.send(data);
    }
  }, []);

  const ping = useCallback(() => {
    sendMessage({ type: 'ping' });
  }, [sendMessage]);

  const subscribe = useCallback((events: string[]) => {
    sendMessage({
      type: 'subscribe',
      data: { events },
    });
  }, [sendMessage]);

  return {
    connected,
    lastMessage,
    sendMessage,
    ping,
    subscribe,
  };
}
