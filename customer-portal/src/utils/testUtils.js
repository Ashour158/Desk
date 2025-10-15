/**
 * Test utilities for frontend testing
 */

// Mock matchMedia for responsive testing
export const mockMatchMedia = (matches) => {
  return {
    matches,
    media: '',
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  };
};

// Mock IntersectionObserver
export const mockIntersectionObserver = () => {
  return {
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
  };
};

// Mock ResizeObserver
export const mockResizeObserver = () => {
  return {
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
  };
};

// Mock performance API
export const mockPerformance = {
  now: jest.fn(() => Date.now()),
  getEntriesByType: jest.fn(() => []),
  mark: jest.fn(),
  measure: jest.fn(),
  clearMarks: jest.fn(),
  clearMeasures: jest.fn(),
};

// Mock localStorage
export const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

// Mock sessionStorage
export const mockSessionStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

// Mock fetch
export const mockFetch = jest.fn();

// Mock console
export const mockConsole = {
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  info: jest.fn(),
  debug: jest.fn(),
};

// Test data generators
export const createMockUser = (overrides = {}) => ({
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  firstName: 'Test',
  lastName: 'User',
  isActive: true,
  ...overrides,
});

export const createMockTicket = (overrides = {}) => ({
  id: 1,
  title: 'Test Ticket',
  description: 'Test ticket description',
  status: 'open',
  priority: 'medium',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  ...overrides,
});

// Wait for async operations
export const waitFor = (callback, options = {}) => {
  return new Promise((resolve, reject) => {
    const timeout = options.timeout || 1000;
    const interval = options.interval || 50;
    let attempts = 0;
    const maxAttempts = timeout / interval;

    const check = () => {
      attempts++;
      try {
        const result = callback();
        if (result) {
          resolve(result);
        } else if (attempts >= maxAttempts) {
          reject(new Error('Timeout waiting for condition'));
        } else {
          setTimeout(check, interval);
        }
      } catch (error) {
        if (attempts >= maxAttempts) {
          reject(error);
        } else {
          setTimeout(check, interval);
        }
      }
    };

    check();
  });
};
