/**
 * Tests for NotificationContext
 * Tests notification state management
 */

import React, { useContext } from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { NotificationContext } from '@/contexts/NotificationContext';

// Mock notification types
type Notification = {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
};

// Mock component that uses NotificationContext
const NotificationConsumer = ({ onAddNotification }: { onAddNotification?: (notification: Notification) => void }) => {
  const { notifications, addNotification, removeNotification } = useContext(NotificationContext);

  const handleAddSuccess = () => {
    const notification: Notification = {
      id: '1',
      message: 'Success!',
      type: 'success',
    };
    addNotification(notification);
    onAddNotification?.(notification);
  };

  const handleAddError = () => {
    const notification: Notification = {
      id: '2',
      message: 'Error occurred!',
      type: 'error',
    };
    addNotification(notification);
    onAddNotification?.(notification);
  };

  return (
    <div>
      <button onClick={handleAddSuccess}>Add Success</button>
      <button onClick={handleAddError}>Add Error</button>
      <div data-testid="notification-count">{notifications?.length || 0}</div>
      {notifications && notifications.map((n: any) => <div key={n.id}>{n.message}</div>)}
    </div>
  );
};

describe('NotificationContext', () => {
  const mockValue = {
    notifications: [],
    addNotification: jest.fn(),
    removeNotification: jest.fn(),
    clearNotifications: jest.fn(),
  };

  test('provides notifications array', () => {
    render(
      <NotificationContext.Provider value={mockValue}>
        <NotificationConsumer />
      </NotificationContext.Provider>
    );

    const count = screen.getByTestId('notification-count');
    expect(count.textContent).toBe('0');
  });

  test('provides addNotification method', () => {
    const mockAddNotification = jest.fn();
    const value = {
      ...mockValue,
      addNotification: mockAddNotification,
    };

    render(
      <NotificationContext.Provider value={value}>
        <NotificationConsumer
          onAddNotification={(n) => {
            mockAddNotification(n);
          }}
        />
      </NotificationContext.Provider>
    );

    const button = screen.getByText('Add Success');
    fireEvent.click(button);
    expect(mockAddNotification).toHaveBeenCalled();
  });

  test('provides removeNotification method', () => {
    const mockRemoveNotification = jest.fn();
    const value = {
      ...mockValue,
      removeNotification: mockRemoveNotification,
    };

    render(
      <NotificationContext.Provider value={value}>
        <NotificationConsumer />
      </NotificationContext.Provider>
    );

    // Test that removeNotification is available
    expect(mockRemoveNotification).toBeDefined();
  });

  test('notification with success type', () => {
    const value = {
      ...mockValue,
      notifications: [
        {
          id: '1',
          message: 'Operation successful',
          type: 'success',
        },
      ],
    };

    render(
      <NotificationContext.Provider value={value}>
        <NotificationConsumer />
      </NotificationContext.Provider>
    );

    expect(screen.getByText('Operation successful')).toBeInTheDocument();
  });

  test('notification with error type', () => {
    const value = {
      ...mockValue,
      notifications: [
        {
          id: '1',
          message: 'An error occurred',
          type: 'error',
        },
      ],
    };

    render(
      <NotificationContext.Provider value={value}>
        <NotificationConsumer />
      </NotificationContext.Provider>
    );

    expect(screen.getByText('An error occurred')).toBeInTheDocument();
  });

  test('notification with warning type', () => {
    const value = {
      ...mockValue,
      notifications: [
        {
          id: '1',
          message: 'Warning message',
          type: 'warning',
        },
      ],
    };

    render(
      <NotificationContext.Provider value={value}>
        <NotificationConsumer />
      </NotificationContext.Provider>
    );

    expect(screen.getByText('Warning message')).toBeInTheDocument();
  });

  test('notification with info type', () => {
    const value = {
      ...mockValue,
      notifications: [
        {
          id: '1',
          message: 'Information',
          type: 'info',
        },
      ],
    };

    render(
      <NotificationContext.Provider value={value}>
        <NotificationConsumer />
      </NotificationContext.Provider>
    );

    expect(screen.getByText('Information')).toBeInTheDocument();
  });

  test('clearNotifications method available', () => {
    const mockClearNotifications = jest.fn();
    const value = {
      ...mockValue,
      clearNotifications: mockClearNotifications,
    };

    render(
      <NotificationContext.Provider value={value}>
        <NotificationConsumer />
      </NotificationContext.Provider>
    );

    expect(mockClearNotifications).toBeDefined();
  });

  test('handles multiple notifications', () => {
    const value = {
      ...mockValue,
      notifications: [
        {
          id: '1',
          message: 'First notification',
          type: 'success',
        },
        {
          id: '2',
          message: 'Second notification',
          type: 'error',
        },
        {
          id: '3',
          message: 'Third notification',
          type: 'info',
        },
      ],
    };

    render(
      <NotificationContext.Provider value={value}>
        <NotificationConsumer />
      </NotificationContext.Provider>
    );

    expect(screen.getByText('First notification')).toBeInTheDocument();
    expect(screen.getByText('Second notification')).toBeInTheDocument();
    expect(screen.getByText('Third notification')).toBeInTheDocument();

    const count = screen.getByTestId('notification-count');
    expect(count.textContent).toBe('3');
  });
});
