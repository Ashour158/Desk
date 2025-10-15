import React, { createContext, useContext, useState, useEffect, useRef, useMemo, useCallback } from 'react';
import PropTypes from 'prop-types';
import io from 'socket.io-client';
import Logger from '../utils/logger';

/**
 * Optimized Socket context with memoization to prevent unnecessary re-renders
 */
const SocketContext = createContext();

/**
 * Custom hook to use socket context
 * @returns {Object} Socket context value
 */
export const useSocket = () => {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};

/**
 * Optimized Socket provider component with memoization
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 */
export const SocketProvider = ({ children }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const socketRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  /**
   * Initialize socket connection with memoization
   */
  const initializeSocket = useCallback(() => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        Logger.warn('No authentication token found, skipping socket connection');
        return;
      }

      const socketUrl = process.env.REACT_APP_SOCKET_URL || 'http://localhost:3000';
      
      socketRef.current = io(socketUrl, {
        auth: {
          token: token
        },
        transports: ['websocket', 'polling'],
        timeout: 20000,
        forceNew: true
      });

      setupSocketListeners();
      
      Logger.info('Socket connection initialized', {
        url: socketUrl,
        transports: ['websocket', 'polling']
      });
      
    } catch (error) {
      Logger.error('Failed to initialize socket connection:', error);
      setConnectionError('Failed to connect to real-time service');
    }
  }, []);

  /**
   * Setup socket event listeners
   */
  const setupSocketListeners = useCallback(() => {
    if (!socketRef.current) return;

    socketRef.current.on('connect', () => {
      Logger.info('Socket connected successfully');
      setIsConnected(true);
      setConnectionError(null);
      reconnectAttempts.current = 0;
    });

    socketRef.current.on('disconnect', (reason) => {
      Logger.warn('Socket disconnected:', reason);
      setIsConnected(false);
      
      // Attempt reconnection for certain disconnect reasons
      if (reason === 'io server disconnect' || reason === 'io client disconnect') {
        handleReconnection();
      }
    });

    socketRef.current.on('connect_error', (error) => {
      Logger.error('Socket connection error:', error);
      setConnectionError('Connection failed. Retrying...');
      handleReconnection();
    });

    socketRef.current.on('error', (error) => {
      Logger.error('Socket error:', error);
      setConnectionError('Real-time service error');
    });

    // Real-time event listeners
    socketRef.current.on('ticket-updated', (data) => {
      Logger.info('Ticket updated via socket:', data);
      // Emit custom event for components to listen to
      window.dispatchEvent(new CustomEvent('ticket-updated', { detail: data }));
    });

    socketRef.current.on('new-message', (data) => {
      Logger.info('New message via socket:', data);
      window.dispatchEvent(new CustomEvent('new-message', { detail: data }));
    });

    socketRef.current.on('notification', (data) => {
      Logger.info('Notification via socket:', data);
      window.dispatchEvent(new CustomEvent('notification', { detail: data }));
    });

    socketRef.current.on('user-online', (data) => {
      Logger.info('User online:', data);
      window.dispatchEvent(new CustomEvent('user-online', { detail: data }));
    });

    socketRef.current.on('user-offline', (data) => {
      Logger.info('User offline:', data);
      window.dispatchEvent(new CustomEvent('user-offline', { detail: data }));
    });
  }, []);

  /**
   * Handle reconnection logic
   */
  const handleReconnection = useCallback(() => {
    if (reconnectAttempts.current >= maxReconnectAttempts) {
      Logger.error('Max reconnection attempts reached');
      setConnectionError('Unable to connect to real-time service');
      return;
    }

    reconnectAttempts.current += 1;
    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
    
    Logger.info(`Attempting reconnection ${reconnectAttempts.current}/${maxReconnectAttempts} in ${delay}ms`);
    
    reconnectTimeoutRef.current = setTimeout(() => {
      if (socketRef.current) {
        socketRef.current.connect();
      }
    }, delay);
  }, [maxReconnectAttempts]);

  /**
   * Cleanup socket connection
   */
  const cleanupSocket = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
    }
    
    setIsConnected(false);
    setConnectionError(null);
    reconnectAttempts.current = 0;
    
    Logger.info('Socket connection cleaned up');
  }, []);

  /**
   * Join ticket room
   */
  const joinTicket = useCallback((ticketId) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('join-ticket', { ticketId });
      Logger.info('Joined ticket room:', ticketId);
    }
  }, [isConnected]);

  /**
   * Leave ticket room
   */
  const leaveTicket = useCallback((ticketId) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('leave-ticket', { ticketId });
      Logger.info('Left ticket room:', ticketId);
    }
  }, [isConnected]);

  /**
   * Join chat room
   */
  const joinChat = useCallback((chatId) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('join-chat', { chatId });
      Logger.info('Joined chat room:', chatId);
    }
  }, [isConnected]);

  /**
   * Send chat message
   */
  const sendMessage = useCallback((chatId, message) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('chat-message', {
        chatId,
        message
      });
      Logger.info('Message sent via socket:', { chatId, message });
    }
  }, [isConnected]);

  /**
   * Subscribe to notifications
   */
  const subscribeNotifications = useCallback(() => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('subscribe-notifications');
      Logger.info('Subscribed to notifications');
    }
  }, [isConnected]);

  /**
   * Unsubscribe from notifications
   */
  const unsubscribeNotifications = useCallback(() => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('unsubscribe-notifications');
      Logger.info('Unsubscribed from notifications');
    }
  }, [isConnected]);

  /**
   * Update ticket
   */
  const updateTicket = useCallback((ticketId, updates) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('ticket-update', {
        ticketId,
        updates
      });
      Logger.info('Ticket update sent via socket:', { ticketId, updates });
    }
  }, [isConnected]);

  /**
   * Send typing indicator
   */
  const sendTypingStart = useCallback((ticketId) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('typing-start', { ticketId });
    }
  }, [isConnected]);

  /**
   * Stop typing indicator
   */
  const sendTypingStop = useCallback((ticketId) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('typing-stop', { ticketId });
    }
  }, [isConnected]);

  // Initialize socket on mount
  useEffect(() => {
    initializeSocket();
    return cleanupSocket;
  }, [initializeSocket, cleanupSocket]);

  /**
   * Memoized context value to prevent unnecessary re-renders
   */
  const contextValue = useMemo(() => ({
    isConnected,
    connectionError,
    joinTicket,
    leaveTicket,
    joinChat,
    sendMessage,
    subscribeNotifications,
    unsubscribeNotifications,
    updateTicket,
    sendTypingStart,
    sendTypingStop,
    reconnect: initializeSocket
  }), [
    isConnected,
    connectionError,
    joinTicket,
    leaveTicket,
    joinChat,
    sendMessage,
    subscribeNotifications,
    unsubscribeNotifications,
    updateTicket,
    sendTypingStart,
    sendTypingStop,
    initializeSocket
  ]);

  return (
    <SocketContext.Provider value={contextValue}>
      {children}
    </SocketContext.Provider>
  );
};

SocketProvider.propTypes = {
  children: PropTypes.node.isRequired
};

export default SocketProvider;
