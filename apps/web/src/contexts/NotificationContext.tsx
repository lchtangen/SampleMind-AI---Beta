'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { CheckCircle, AlertCircle, Info, X } from 'lucide-react';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
}

interface NotificationContextType {
  notifications: Notification[];
  addNotification: (type: Notification['type'], message: string) => void;
  removeNotification: (id: string) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = (type: Notification['type'], message: string) => {
    const id = Math.random().toString(36).substring(7);
    setNotifications(prev => [...prev, { id, type, message }]);
    setTimeout(() => removeNotification(id), 5000);
  };

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  return (
    <NotificationContext.Provider value={{ notifications, addNotification, removeNotification }}>
      {children}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {notifications.map(notification => (
          <NotificationItem key={notification.id} notification={notification} onClose={() => removeNotification(notification.id)} />
        ))}
      </div>
    </NotificationContext.Provider>
  );
}

function NotificationItem({ notification, onClose }: { notification: Notification; onClose: () => void }) {
  const icons = {
    success: <CheckCircle className="h-5 w-5 text-[hsl(180,95%,55%)]" />,
    error: <AlertCircle className="h-5 w-5 text-red-400" />,
    info: <Info className="h-5 w-5 text-[hsl(220,90%,60%)]" />,
  };

  const colors = {
    success: 'border-[hsl(180,95%,55%)]/30 bg-[hsl(180,95%,55%)]/10',
    error: 'border-red-500/30 bg-red-500/10',
    info: 'border-[hsl(220,90%,60%)]/30 bg-[hsl(220,90%,60%)]/10',
  };

  return (
    <div className={`relative backdrop-blur-md bg-white/5 border ${colors[notification.type]} rounded-lg p-4 min-w-[300px] animate-slide-in`}>
      <div className="flex items-start space-x-3">
        {icons[notification.type]}
        <p className="text-[hsl(0,0%,98%)] flex-1 text-sm">{notification.message}</p>
        <button onClick={onClose} className="text-[hsl(220,10%,65%)] hover:text-[hsl(0,0%,98%)] transition">
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

export function useNotification() {
  const context = useContext(NotificationContext);
  if (!context) throw new Error('useNotification must be used within NotificationProvider');
  return context;
}
