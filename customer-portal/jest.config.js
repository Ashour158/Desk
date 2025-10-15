module.exports = {
  // Test environment
  testEnvironment: 'jsdom',
  
  // Setup files
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  
  // Module name mapping for absolute imports
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@components/(.*)$': '<rootDir>/src/components/$1',
    '^@pages/(.*)$': '<rootDir>/src/pages/$1',
    '^@utils/(.*)$': '<rootDir>/src/utils/$1',
    '^@hooks/(.*)$': '<rootDir>/src/hooks/$1',
    '^@contexts/(.*)$': '<rootDir>/src/contexts/$1'
  },
  
  // Transform files
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
    '^.+\\.css$': 'jest-transform-stub',
    '^.+\\.(png|jpg|jpeg|gif|svg)$': 'jest-transform-stub'
  },
  
  // Test file patterns - run tests in smaller batches
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{test,spec}.{js,jsx,ts,tsx}'
  ],
  
  // Memory optimization settings
  maxWorkers: 1, // Run tests sequentially to reduce memory usage
  workerIdleMemoryLimit: '512MB', // Limit worker memory
  
  // Coverage configuration - disable for now to reduce memory usage
  collectCoverage: false,
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.js',
    '!src/setupTests.js',
    '!src/**/__tests__/**',
    '!src/**/*.test.{js,jsx,ts,tsx}',
    '!src/**/*.spec.{js,jsx,ts,tsx}'
  ],
  
  // Coverage thresholds - reduced for initial testing
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },
  
  // Coverage reporters
  coverageReporters: [
    'text',
    'lcov'
  ],
  
  // Coverage directory
  coverageDirectory: 'coverage',
  
  // Module file extensions
  moduleFileExtensions: ['js', 'jsx', 'ts', 'tsx', 'json'],
  
  // Transform ignore patterns
  transformIgnorePatterns: [
    'node_modules/(?!(react-query|react-router|react-router-dom|react-hot-toast)/)'
  ],
  
  // Test timeout - reduced for faster execution
  testTimeout: 5000,
  
  // Verbose output - disabled to reduce memory usage
  verbose: false,
  
  // Clear mocks between tests
  clearMocks: true,
  
  // Restore mocks between tests
  restoreMocks: true,
  
  // Reset modules between tests
  resetModules: true,
  
  // Memory optimization
  cache: false, // Disable caching to reduce memory usage
  maxConcurrency: 1, // Run one test at a time
  bail: 1 // Stop on first failure to save memory
};
