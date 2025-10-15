import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import io from 'socket.io-client';
import Logger from '../utils/logger';

/**
 * Socket context for managing real-time connections
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
 * Socket provider component
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

  useEffect(() => {
    initializeSocket();
    return () => {
      cleanupSocket();
    };
  }, []);

  /**
   * Initialize socket connection
   */
  const initializeSocket = () => {
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
  };

  /**
   * Setup socket event listeners
   */
  const setupSocketListeners = () => {
    const socket = socketRef.current;
    if (!socket) return;

    // Connection events
    socket.on('connect', () => {
      setIsConnected(true);
      setConnectionError(null);
      reconnectAttempts.current = 0;
      
      Logger.info('Socket connected successfully', {
        socketId: socket.id
      });
    });

    socket.on('disconnect', (reason) => {
      setIsConnected(false);
      
      Logger.warn('Socket disconnected', {
        reason: reason
      });
      
      // Attempt to reconnect if not manually disconnected
      if (reason !== 'io client disconnect') {
        scheduleReconnect();
      }
    });

    socket.on('connect_error', (error) => {
      setConnectionError('Connection failed');
      setIsConnected(false);
      
      Logger.error('Socket connection error:', error);
      
      scheduleReconnect();
    });

    // Authentication events
    socket.on('authenticated', (data) => {
      Logger.info('Socket authenticated successfully', {
        userId: data.user?.id,
        organizationId: data.organization?.id
      });
    });

    socket.on('authentication_error', (error) => {
      Logger.error('Socket authentication failed:', error);
      setConnectionError('Authentication failed');
      setIsConnected(false);
    });

    // Real-time events
    socket.on('ticket-updated', (data) => {
      Logger.info('Ticket update received', {
        ticketId: data.ticketId,
        updates: data.updates
      });
      
      // Emit custom event for components to listen to
      window.dispatchEvent(new CustomEvent('ticket-updated', { detail: data }));
    });

    socket.on('new-message', (data) => {
      Logger.info('New message received', {
        messageId: data.id,
        chatId: data.chatId
      });
      
      // Emit custom event for components to listen to
      window.dispatchEvent(new CustomEvent('new-message', { detail: data }));
    });

    socket.on('notification', (data) => {
      Logger.info('Notification received', {
        type: data.type,
        message: data.message
      });
      
      // Emit custom event for components to listen to
      window.dispatchEvent(new CustomEvent('notification', { detail: data }));
    });

    socket.on('user-typing', (data) => {
      Logger.debug('User typing indicator received', {
        userId: data.userId,
        ticketId: data.ticketId
      });
      
      // Emit custom event for components to listen to
      window.dispatchEvent(new CustomEvent('user-typing', { detail: data }));
    });

    socket.on('user-stopped-typing', (data) => {
      Logger.debug('User stopped typing indicator received', {
        userId: data.userId,
        ticketId: data.ticketId
      });
      
      // Emit custom event for components to listen to
      window.dispatchEvent(new CustomEvent('user-stopped-typing', { detail: data }));
    });

    socket.on('error', (error) => {
      Logger.error('Socket error received:', error);
      setConnectionError(error.message || 'Socket error occurred');
    });
  };

  /**
   * Schedule reconnection attempt
   */
  const scheduleReconnect = () => {
    if (reconnectAttempts.current >= maxReconnectAttempts) {
      Logger.error('Max reconnection attempts reached');
      setConnectionError('Unable to reconnect to real-time service');
      return;
    }

    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
    reconnectAttempts.current += 1;
    
    Logger.info('Scheduling reconnection attempt', {
      attempt: reconnectAttempts.current,
      delay: delay
    });
    
    reconnectTimeoutRef.current = setTimeout(() => {
      if (socketRef.current && !socketRef.current.connected) {
        initializeSocket();
      }
    }, delay);
  };

  /**
   * Cleanup socket connection
   */
  const cleanupSocket = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
    }
    
    Logger.info('Socket connection cleaned up');
  };

  /**
   * Join a room
   * @param {string} room - Room name
   */
  const joinRoom = (room) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('join-room', { room });
      Logger.info('Joined room', { room });
    }
  };

  /**
   * Leave a room
   * @param {string} room - Room name
   */
  const leaveRoom = (room) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('leave-room', { room });
      Logger.info('Left room', { room });
    }
  };

  /**
   * Send a message
   * @param {string} event - Event name
   * @param {Object} data - Message data
   */
  const emit = (event, data) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit(event, data);
      Logger.debug('Emitted event', { event, data });
    } else {
      Logger.warn('Cannot emit event, socket not connected', { event, data });
    }
  };

  /**
   * Subscribe to an event
   * @param {string} event - Event name
   * @param {Function} callback - Event callback
   */
  const subscribe = (event, callback) => {
    if (socketRef.current) {
      socketRef.current.on(event, callback);
      Logger.debug('Subscribed to event', { event });
    }
  };

  /**
   * Unsubscribe from an event
   * @param {string} event - Event name
   * @param {Function} callback - Event callback
   */
  const unsubscribe = (event, callback) => {
    if (socketRef.current) {
      socketRef.current.off(event, callback);
      Logger.debug('Unsubscribed from event', { event });
    }
  };

  /**
   * Manually reconnect
   */
  const reconnect = () => {
    cleanupSocket();
    reconnectAttempts.current = 0;
    setConnectionError(null);
    initializeSocket();
  };

  const value = {
    isConnected,
    connectionError,
    socket: socketRef.current,
    joinRoom,
    leaveRoom,
    emit,
    subscribe,
    unsubscribe,
    reconnect
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
};

SocketProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export default SocketContext;
