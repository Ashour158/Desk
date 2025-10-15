/**
 * Comprehensive Logger Utility Tests
 * Tests critical logging functionality including log levels, formatting, and error handling.
 */

import Logger from '../../utils/logger-complete';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock console methods
const mockConsole = {
  log: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
  info: jest.fn(),
  debug: jest.fn()
};

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};

// Mock sessionStorage
const mockSessionStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};

// Mock fetch
const mockFetch = jest.fn();

// Mock performance API
const mockPerformance = {
  now: jest.fn(() => Date.now())
};

// Setup mocks
beforeAll(() => {
  global.console = mockConsole;
  Object.defineProperty(global, 'localStorage', {
    value: mockLocalStorage,
    writable: true
  });
  Object.defineProperty(global, 'sessionStorage', {
    value: mockSessionStorage,
    writable: true
  });
  global.fetch = mockFetch;
  global.performance = mockPerformance;
});

beforeEach(() => {
  jest.clearAllMocks();
  mockLocalStorage.getItem.mockReturnValue(null);
  mockSessionStorage.getItem.mockReturnValue(null);
});

describe('Logger Utility', () => {
  describe('Basic Logging Functionality', () => {
    it('should log info messages correctly', () => {
      const message = 'Test info message';
      const data = { userId: 123, action: 'login' };
      
      Logger.info(message, data);
      
      expect(mockConsole.info).toHaveBeenCalledWith(
        expect.stringContaining(message),
        expect.objectContaining(data)
      );
    });

    it('should log warning messages correctly', () => {
      const message = 'Test warning message';
      const data = { userId: 123, action: 'invalid_request' };
      
      Logger.warn(message, data);
      
      expect(mockConsole.warn).toHaveBeenCalledWith(
        expect.stringContaining(message),
        expect.objectContaining(data)
      );
    });

    it('should log error messages correctly', () => {
      const message = 'Test error message';
      const data = { userId: 123, action: 'database_error', error: 'Connection failed' };
      
      Logger.error(message, data);
      
      expect(mockConsole.error).toHaveBeenCalledWith(
        expect.stringContaining(message),
        expect.objectContaining(data)
      );
    });

    it('should log debug messages correctly', () => {
      const message = 'Test debug message';
      const data = { userId: 123, action: 'debug_info' };
      
      Logger.debug(message, data);
      
      expect(mockConsole.debug).toHaveBeenCalledWith(
        expect.stringContaining(message),
        expect.objectContaining(data)
      );
    });

    it('should log success messages correctly', () => {
      const message = 'Test success message';
      const data = { userId: 123, action: 'user_created' };
      
      Logger.success(message, data);
      
      expect(mockConsole.log).toHaveBeenCalledWith(
        expect.stringContaining(message),
        expect.objectContaining(data)
      );
    });
  });

  describe('Log Level Filtering', () => {
    it('should respect log level filtering', () => {
      // Set log level to warn
      Logger.setLogLevel('warn');
      
      Logger.info('This should not be logged');
      Logger.warn('This should be logged');
      Logger.error('This should be logged');
      
      expect(mockConsole.info).not.toHaveBeenCalled();
      expect(mockConsole.warn).toHaveBeenCalled();
      expect(mockConsole.error).toHaveBeenCalled();
    });

    it('should log all levels when log level is debug', () => {
      Logger.setLogLevel('debug');
      
      Logger.debug('Debug message');
      Logger.info('Info message');
      Logger.warn('Warning message');
      Logger.error('Error message');
      
      expect(mockConsole.debug).toHaveBeenCalled();
      expect(mockConsole.info).toHaveBeenCalled();
      expect(mockConsole.warn).toHaveBeenCalled();
      expect(mockConsole.error).toHaveBeenCalled();
    });

    it('should not log debug messages when log level is info', () => {
      Logger.setLogLevel('info');
      
      Logger.debug('This should not be logged');
      Logger.info('This should be logged');
      
      expect(mockConsole.debug).not.toHaveBeenCalled();
      expect(mockConsole.info).toHaveBeenCalled();
    });
  });

  describe('Log Formatting', () => {
    it('should format logs with timestamp', () => {
      const message = 'Test message';
      const data = { userId: 123 };
      
      Logger.info(message, data);
      
      const logCall = mockConsole.info.mock.calls[0][0];
      expect(logCall).toMatch(/\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/);
      expect(logCall).toContain(message);
    });

    it('should format logs with log level', () => {
      const message = 'Test message';
      const data = { userId: 123 };
      
      Logger.info(message, data);
      
      const logCall = mockConsole.info.mock.calls[0][0];
      expect(logCall).toContain('[INFO]');
    });

    it('should format logs with component name', () => {
      const message = 'Test message';
      const data = { userId: 123 };
      
      Logger.info(message, data, 'UserService');
      
      const logCall = mockConsole.info.mock.calls[0][0];
      expect(logCall).toContain('[UserService]');
    });

    it('should format logs with request ID', () => {
      const message = 'Test message';
      const data = { userId: 123 };
      
      Logger.info(message, data, 'UserService', 'req-123');
      
      const logCall = mockConsole.info.mock.calls[0][0];
      expect(logCall).toContain('[req-123]');
    });
  });

  describe('Error Handling', () => {
    it('should handle logging errors gracefully', () => {
      // Mock console.info to throw an error
      mockConsole.info.mockImplementation(() => {
        throw new Error('Console logging failed');
      });
      
      // Should not throw an error
      expect(() => {
        Logger.info('Test message');
      }).not.toThrow();
    });

    it('should handle invalid log levels gracefully', () => {
      // Should not throw an error
      expect(() => {
        Logger.setLogLevel('invalid_level');
      }).not.toThrow();
    });

    it('should handle null or undefined messages', () => {
      expect(() => {
        Logger.info(null);
        Logger.info(undefined);
        Logger.info('');
      }).not.toThrow();
    });

    it('should handle circular references in data', () => {
      const circularData = { name: 'test' };
      circularData.self = circularData;
      
      expect(() => {
        Logger.info('Test message', circularData);
      }).not.toThrow();
    });
  });

  describe('Performance Logging', () => {
    it('should log performance metrics', () => {
      const startTime = 1000;
      const endTime = 1500;
      
      mockPerformance.now
        .mockReturnValueOnce(startTime)
        .mockReturnValueOnce(endTime);
      
      Logger.performance('Test operation', { operation: 'database_query' });
      
      expect(mockConsole.log).toHaveBeenCalledWith(
        expect.stringContaining('Test operation'),
        expect.objectContaining({
          operation: 'database_query',
          duration: 500
        })
      );
    });

    it('should handle performance logging errors', () => {
      mockPerformance.now.mockImplementation(() => {
        throw new Error('Performance API failed');
      });
      
      expect(() => {
        Logger.performance('Test operation');
      }).not.toThrow();
    });
  });

  describe('Network Logging', () => {
    it('should log network requests', () => {
      const requestData = {
        url: '/api/users',
        method: 'GET',
        status: 200,
        responseTime: 150
      };
      
      Logger.network('API Request', requestData);
      
      expect(mockConsole.log).toHaveBeenCalledWith(
        expect.stringContaining('API Request'),
        expect.objectContaining(requestData)
      );
    });

    it('should log network errors', () => {
      const errorData = {
        url: '/api/users',
        method: 'GET',
        status: 500,
        error: 'Internal Server Error'
      };
      
      Logger.network('API Error', errorData);
      
      expect(mockConsole.error).toHaveBeenCalledWith(
        expect.stringContaining('API Error'),
        expect.objectContaining(errorData)
      );
    });
  });

  describe('User Action Logging', () => {
    it('should log user actions', () => {
      const actionData = {
        userId: 123,
        action: 'login',
        timestamp: Date.now(),
        ipAddress: '192.168.1.1'
      };
      
      Logger.userAction('User Login', actionData);
      
      expect(mockConsole.log).toHaveBeenCalledWith(
        expect.stringContaining('User Login'),
        expect.objectContaining(actionData)
      );
    });

    it('should sanitize sensitive data in user actions', () => {
      const actionData = {
        userId: 123,
        action: 'login',
        password: 'secret123',
        email: 'user@example.com'
      };
      
      Logger.userAction('User Login', actionData);
      
      const logCall = mockConsole.log.mock.calls[0][1];
      expect(logCall.password).toBe('[REDACTED]');
      expect(logCall.email).toBe('user@example.com');
    });
  });

  describe('Security Logging', () => {
    it('should log security events', () => {
      const securityData = {
        event: 'failed_login',
        userId: 123,
        ipAddress: '192.168.1.1',
        userAgent: 'Mozilla/5.0...'
      };
      
      Logger.security('Failed Login Attempt', securityData);
      
      expect(mockConsole.warn).toHaveBeenCalledWith(
        expect.stringContaining('Failed Login Attempt'),
        expect.objectContaining(securityData)
      );
    });

    it('should log security violations', () => {
      const violationData = {
        event: 'unauthorized_access',
        userId: 123,
        resource: '/admin/users',
        ipAddress: '192.168.1.1'
      };
      
      Logger.security('Unauthorized Access', violationData);
      
      expect(mockConsole.error).toHaveBeenCalledWith(
        expect.stringContaining('Unauthorized Access'),
        expect.objectContaining(violationData)
      );
    });
  });

  describe('Log Persistence', () => {
    it('should persist logs to localStorage', () => {
      Logger.setPersistence(true);
      
      Logger.info('Test message', { userId: 123 });
      
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'app_logs',
        expect.stringContaining('Test message')
      );
    });

    it('should persist logs to sessionStorage', () => {
      Logger.setPersistence(true, 'session');
      
      Logger.info('Test message', { userId: 123 });
      
      expect(mockSessionStorage.setItem).toHaveBeenCalledWith(
        'app_logs',
        expect.stringContaining('Test message')
      );
    });

    it('should not persist logs when persistence is disabled', () => {
      Logger.setPersistence(false);
      
      Logger.info('Test message', { userId: 123 });
      
      expect(mockLocalStorage.setItem).not.toHaveBeenCalled();
      expect(mockSessionStorage.setItem).not.toHaveBeenCalled();
    });
  });

  describe('Log Filtering and Search', () => {
    it('should filter logs by level', () => {
      Logger.setLogLevel('warn');
      
      Logger.info('This should not be logged');
      Logger.warn('This should be logged');
      Logger.error('This should be logged');
      
      const logs = Logger.getLogs();
      
      expect(logs).toHaveLength(2);
      expect(logs.every(log => log.level === 'warn' || log.level === 'error')).toBe(true);
    });

    it('should filter logs by component', () => {
      Logger.info('Message 1', {}, 'UserService');
      Logger.info('Message 2', {}, 'AuthService');
      Logger.info('Message 3', {}, 'UserService');
      
      const logs = Logger.getLogs('UserService');
      
      expect(logs).toHaveLength(2);
      expect(logs.every(log => log.component === 'UserService')).toBe(true);
    });

    it('should search logs by message content', () => {
      Logger.info('User login successful');
      Logger.info('User logout successful');
      Logger.info('Database connection failed');
      
      const logs = Logger.searchLogs('login');
      
      expect(logs).toHaveLength(1);
      expect(logs[0].message).toContain('login');
    });
  });

  describe('Log Export', () => {
    it('should export logs as JSON', () => {
      Logger.info('Test message 1');
      Logger.warn('Test message 2');
      
      const exportedLogs = Logger.exportLogs('json');
      
      expect(() => JSON.parse(exportedLogs)).not.toThrow();
      const parsedLogs = JSON.parse(exportedLogs);
      expect(parsedLogs).toHaveLength(2);
    });

    it('should export logs as CSV', () => {
      Logger.info('Test message 1');
      Logger.warn('Test message 2');
      
      const exportedLogs = Logger.exportLogs('csv');
      
      expect(exportedLogs).toContain('timestamp,level,message');
      expect(exportedLogs).toContain('Test message 1');
      expect(exportedLogs).toContain('Test message 2');
    });

    it('should export logs as text', () => {
      Logger.info('Test message 1');
      Logger.warn('Test message 2');
      
      const exportedLogs = Logger.exportLogs('text');
      
      expect(exportedLogs).toContain('Test message 1');
      expect(exportedLogs).toContain('Test message 2');
    });
  });

  describe('Log Cleanup', () => {
    it('should clear all logs', () => {
      Logger.info('Test message 1');
      Logger.warn('Test message 2');
      
      Logger.clearLogs();
      
      const logs = Logger.getLogs();
      expect(logs).toHaveLength(0);
    });

    it('should clear logs older than specified time', () => {
      const oldTime = Date.now() - 24 * 60 * 60 * 1000; // 24 hours ago
      const newTime = Date.now();
      
      // Mock Date.now to return old time for first log
      jest.spyOn(Date, 'now').mockReturnValueOnce(oldTime);
      Logger.info('Old message');
      
      // Mock Date.now to return new time for second log
      jest.spyOn(Date, 'now').mockReturnValueOnce(newTime);
      Logger.info('New message');
      
      Logger.clearOldLogs(12 * 60 * 60 * 1000); // Clear logs older than 12 hours
      
      const logs = Logger.getLogs();
      expect(logs).toHaveLength(1);
      expect(logs[0].message).toContain('New message');
    });
  });

  describe('Log Analytics', () => {
    it('should provide log statistics', () => {
      Logger.info('Info message 1');
      Logger.info('Info message 2');
      Logger.warn('Warning message');
      Logger.error('Error message');
      
      const stats = Logger.getLogStats();
      
      expect(stats.total).toBe(4);
      expect(stats.byLevel.info).toBe(2);
      expect(stats.byLevel.warn).toBe(1);
      expect(stats.byLevel.error).toBe(1);
    });

    it('should provide log trends', () => {
      // Mock different timestamps
      jest.spyOn(Date, 'now')
        .mockReturnValueOnce(1000)
        .mockReturnValueOnce(2000)
        .mockReturnValueOnce(3000);
      
      Logger.info('Message 1');
      Logger.info('Message 2');
      Logger.info('Message 3');
      
      const trends = Logger.getLogTrends();
      
      expect(trends).toHaveProperty('timeline');
      expect(trends.timeline).toHaveLength(3);
    });
  });

  describe('Log Configuration', () => {
    it('should configure log format', () => {
      Logger.setLogFormat('json');
      
      Logger.info('Test message');
      
      const logCall = mockConsole.info.mock.calls[0][0];
      expect(() => JSON.parse(logCall)).not.toThrow();
    });

    it('should configure log output', () => {
      Logger.setLogOutput('file');
      
      Logger.info('Test message');
      
      // Should not call console methods when output is set to file
      expect(mockConsole.info).not.toHaveBeenCalled();
    });

    it('should configure log rotation', () => {
      Logger.setLogRotation(1000, 5); // 1000 bytes, 5 files
      
      Logger.info('Test message');
      
      expect(Logger.getLogRotationConfig()).toEqual({
        maxSize: 1000,
        maxFiles: 5
      });
    });
  });

  describe('Log Validation', () => {
    it('should validate log data', () => {
      const validData = { userId: 123, action: 'login' };
      const invalidData = { userId: 'invalid', action: 123 };
      
      Logger.info('Valid log', validData);
      Logger.info('Invalid log', invalidData);
      
      // Should handle both valid and invalid data without throwing
      expect(mockConsole.info).toHaveBeenCalledTimes(2);
    });

    it('should sanitize log data', () => {
      const sensitiveData = {
        password: 'secret123',
        token: 'abc123',
        email: 'user@example.com'
      };
      
      Logger.info('Sensitive data', sensitiveData);
      
      const logCall = mockConsole.info.mock.calls[0][1];
      expect(logCall.password).toBe('[REDACTED]');
      expect(logCall.token).toBe('[REDACTED]');
      expect(logCall.email).toBe('user@example.com');
    });
  });

  describe('Log Performance', () => {
    it('should handle high volume logging', () => {
      const startTime = Date.now();
      
      // Log 1000 messages
      for (let i = 0; i < 1000; i++) {
        Logger.info(`Message ${i}`, { index: i });
      }
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      // Should complete within reasonable time (less than 1 second)
      expect(duration).toBeLessThan(1000);
      expect(mockConsole.info).toHaveBeenCalledTimes(1000);
    });

    it('should handle concurrent logging', async () => {
      const promises = [];
      
      // Create 100 concurrent log operations
      for (let i = 0; i < 100; i++) {
        promises.push(
          new Promise(resolve => {
            setTimeout(() => {
              Logger.info(`Concurrent message ${i}`);
              resolve();
            }, Math.random() * 10);
          })
        );
      }
      
      await Promise.all(promises);
      
      expect(mockConsole.info).toHaveBeenCalledTimes(100);
    });
  });
});
