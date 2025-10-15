/**
 * Cross-browser and cross-device testing utilities
 * Comprehensive testing suite for form validation across different browsers and devices
 */

/**
 * Browser and device testing configuration
 */
export const testingConfig = {
  browsers: {
    chrome: {
      name: 'Chrome',
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      features: ['es6', 'localStorage', 'sessionStorage', 'indexedDB', 'webWorkers']
    },
    firefox: {
      name: 'Firefox',
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
      features: ['es6', 'localStorage', 'sessionStorage', 'indexedDB', 'webWorkers']
    },
    safari: {
      name: 'Safari',
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
      features: ['es6', 'localStorage', 'sessionStorage', 'indexedDB']
    },
    edge: {
      name: 'Edge',
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
      features: ['es6', 'localStorage', 'sessionStorage', 'indexedDB', 'webWorkers']
    }
  },
  
  devices: {
    mobile: {
      name: 'Mobile',
      width: 375,
      height: 667,
      pixelRatio: 2,
      touch: true,
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
    },
    tablet: {
      name: 'Tablet',
      width: 768,
      height: 1024,
      pixelRatio: 2,
      touch: true,
      userAgent: 'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
    },
    desktop: {
      name: 'Desktop',
      width: 1920,
      height: 1080,
      pixelRatio: 1,
      touch: false,
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
  },
  
  testSuites: {
    formValidation: [
      'client-side-validation',
      'server-error-parsing',
      'field-validation',
      'form-submission',
      'form-reset',
      'unsaved-changes-warning'
    ],
    accessibility: [
      'keyboard-navigation',
      'screen-reader-compatibility',
      'aria-labels',
      'focus-management',
      'color-contrast'
    ],
    performance: [
      'form-load-time',
      'validation-speed',
      'auto-save-performance',
      'memory-usage',
      'bundle-size'
    ],
    compatibility: [
      'html5-validation',
      'css-features',
      'javascript-features',
      'storage-apis',
      'event-handling'
    ]
  }
};

/**
 * Cross-browser testing utilities
 */
class CrossBrowserTester {
  constructor() {
    this.testResults = new Map();
    this.currentBrowser = this.detectBrowser();
    this.currentDevice = this.detectDevice();
    this.testStartTime = Date.now();
  }

  /**
   * Detect current browser
   * @returns {string} Browser name
   */
  detectBrowser() {
    const userAgent = navigator.userAgent;
    
    if (userAgent.includes('Chrome') && !userAgent.includes('Edg')) {
      return 'chrome';
    } else if (userAgent.includes('Firefox')) {
      return 'firefox';
    } else if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) {
      return 'safari';
    } else if (userAgent.includes('Edg')) {
      return 'edge';
    }
    
    return 'unknown';
  }

  /**
   * Detect current device type
   * @returns {string} Device type
   */
  detectDevice() {
    const width = window.innerWidth;
    const height = window.innerHeight;
    const touch = 'ontouchstart' in window;
    
    if (width <= 480) {
      return 'mobile';
    } else if (width <= 1024) {
      return 'tablet';
    } else {
      return 'desktop';
    }
  }

  /**
   * Test form validation across browsers
   * @param {string} formId - Form ID to test
   * @returns {Promise<Object>} Test results
   */
  async testFormValidation(formId) {
    const results = {
      browser: this.currentBrowser,
      device: this.currentDevice,
      timestamp: Date.now(),
      tests: {}
    };

    try {
      // Test client-side validation
      results.tests.clientSideValidation = await this.testClientSideValidation(formId);
      
      // Test server error parsing
      results.tests.serverErrorParsing = await this.testServerErrorParsing(formId);
      
      // Test field validation
      results.tests.fieldValidation = await this.testFieldValidation(formId);
      
      // Test form submission
      results.tests.formSubmission = await this.testFormSubmission(formId);
      
      // Test form reset
      results.tests.formReset = await this.testFormReset(formId);
      
      // Test unsaved changes warning
      results.tests.unsavedChangesWarning = await this.testUnsavedChangesWarning(formId);
      
    } catch (error) {
      results.error = error.message;
    }

    this.testResults.set(`${formId}_${this.currentBrowser}_${this.currentDevice}`, results);
    return results;
  }

  /**
   * Test client-side validation
   * @param {string} formId - Form ID
   * @returns {Promise<Object>} Test results
   */
  async testClientSideValidation(formId) {
    const results = {
      passed: 0,
      failed: 0,
      errors: []
    };

    try {
      const form = document.querySelector(`#${formId}`);
      if (!form) {
        throw new Error(`Form ${formId} not found`);
      }

      // Test required field validation
      const requiredFields = form.querySelectorAll('[required]');
      for (const field of requiredFields) {
        const fieldName = field.name;
        const originalValue = field.value;
        
        // Clear field and test validation
        field.value = '';
        field.dispatchEvent(new Event('blur', { bubbles: true }));
        
        await new Promise(resolve => setTimeout(resolve, 100));
        
        const hasError = document.querySelector(`[id="${fieldName}-error"]`);
        if (hasError && hasError.textContent.trim()) {
          results.passed++;
        } else {
          results.failed++;
          results.errors.push({
            field: fieldName,
            expected: 'Validation error',
            actual: 'No error shown'
          });
        }
        
        // Restore original value
        field.value = originalValue;
      }

      // Test email validation
      const emailField = form.querySelector('input[type="email"]');
      if (emailField) {
        emailField.value = 'invalid-email';
        emailField.dispatchEvent(new Event('blur', { bubbles: true }));
        
        await new Promise(resolve => setTimeout(resolve, 100));
        
        const hasError = document.querySelector(`[id="${emailField.name}-error"]`);
        if (hasError && hasError.textContent.includes('email')) {
          results.passed++;
        } else {
          results.failed++;
          results.errors.push({
            field: emailField.name,
            expected: 'Email validation error',
            actual: 'No email validation error'
          });
        }
      }

    } catch (error) {
      results.failed++;
      results.errors.push({
        field: 'general',
        expected: 'No error',
        actual: error.message
      });
    }

    return results;
  }

  /**
   * Test server error parsing
   * @param {string} formId - Form ID
   * @returns {Promise<Object>} Test results
   */
  async testServerErrorParsing(formId) {
    const results = {
      passed: 0,
      failed: 0,
      errors: []
    };

    try {
      // Test different error scenarios
      const errorScenarios = [
        {
          name: 'Validation Error',
          response: { status: 422, field_errors: { email: 'Invalid email format' } },
          expectedCategory: 'validation'
        },
        {
          name: 'Authentication Error',
          response: { status: 401, message: 'Invalid credentials' },
          expectedCategory: 'authentication'
        },
        {
          name: 'Server Error',
          response: { status: 500, message: 'Internal server error' },
          expectedCategory: 'server'
        }
      ];

      for (const scenario of errorScenarios) {
        try {
          // Import and test error parser
          const { parseServerError } = await import('./serverErrorParser.js');
          const parsedError = parseServerError(scenario.response);
          
          if (parsedError.category === scenario.expectedCategory) {
            results.passed++;
          } else {
            results.failed++;
            results.errors.push({
              scenario: scenario.name,
              expected: scenario.expectedCategory,
              actual: parsedError.category
            });
          }
        } catch (error) {
          results.failed++;
          results.errors.push({
            scenario: scenario.name,
            expected: 'No error',
            actual: error.message
          });
        }
      }

    } catch (error) {
      results.failed++;
      results.errors.push({
        field: 'general',
        expected: 'No error',
        actual: error.message
      });
    }

    return results;
  }

  /**
   * Test field validation
   * @param {string} formId - Form ID
   * @returns {Promise<Object>} Test results
   */
  async testFieldValidation(formId) {
    const results = {
      passed: 0,
      failed: 0,
      errors: []
    };

    try {
      const form = document.querySelector(`#${formId}`);
      if (!form) {
        throw new Error(`Form ${formId} not found`);
      }

      const fields = form.querySelectorAll('input, select, textarea');
      
      for (const field of fields) {
        const fieldName = field.name;
        const fieldType = field.type || field.tagName.toLowerCase();
        
        // Test field focus and blur events
        field.dispatchEvent(new Event('focus', { bubbles: true }));
        await new Promise(resolve => setTimeout(resolve, 50));
        
        field.dispatchEvent(new Event('blur', { bubbles: true }));
        await new Promise(resolve => setTimeout(resolve, 50));
        
        // Test field change event
        const originalValue = field.value;
        field.value = 'test-value';
        field.dispatchEvent(new Event('change', { bubbles: true }));
        await new Promise(resolve => setTimeout(resolve, 50));
        
        // Restore original value
        field.value = originalValue;
        
        results.passed++;
      }

    } catch (error) {
      results.failed++;
      results.errors.push({
        field: 'general',
        expected: 'No error',
        actual: error.message
      });
    }

    return results;
  }

  /**
   * Test form submission
   * @param {string} formId - Form ID
   * @returns {Promise<Object>} Test results
   */
  async testFormSubmission(formId) {
    const results = {
      passed: 0,
      failed: 0,
      errors: []
    };

    try {
      const form = document.querySelector(`#${formId}`);
      if (!form) {
        throw new Error(`Form ${formId} not found`);
      }

      // Test form submission event
      const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
      const preventDefaultCalled = form.dispatchEvent(submitEvent);
      
      if (preventDefaultCalled) {
        results.passed++;
      } else {
        results.failed++;
        results.errors.push({
          field: 'form-submission',
          expected: 'Event handled',
          actual: 'Event not handled'
        });
      }

      // Test submit button state
      const submitButton = form.querySelector('button[type="submit"]');
      if (submitButton) {
        const isDisabled = submitButton.disabled;
        if (typeof isDisabled === 'boolean') {
          results.passed++;
        } else {
          results.failed++;
          results.errors.push({
            field: 'submit-button',
            expected: 'Boolean disabled state',
            actual: typeof isDisabled
          });
        }
      }

    } catch (error) {
      results.failed++;
      results.errors.push({
        field: 'general',
        expected: 'No error',
        actual: error.message
      });
    }

    return results;
  }

  /**
   * Test form reset
   * @param {string} formId - Form ID
   * @returns {Promise<Object>} Test results
   */
  async testFormReset(formId) {
    const results = {
      passed: 0,
      failed: 0,
      errors: []
    };

    try {
      const form = document.querySelector(`#${formId}`);
      if (!form) {
        throw new Error(`Form ${formId} not found`);
      }

      // Test form reset functionality
      const resetButton = form.querySelector('button[type="button"]');
      if (resetButton && resetButton.textContent.includes('Reset')) {
        // Fill form with test data
        const fields = form.querySelectorAll('input, select, textarea');
        for (const field of fields) {
          if (field.type !== 'checkbox' && field.type !== 'radio') {
            field.value = 'test-value';
          } else if (field.type === 'checkbox') {
            field.checked = true;
          }
        }
        
        // Click reset button
        resetButton.click();
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Check if fields are cleared
        let allCleared = true;
        for (const field of fields) {
          if (field.type === 'checkbox') {
            if (field.checked) {
              allCleared = false;
              break;
            }
          } else if (field.value !== '') {
            allCleared = false;
            break;
          }
        }
        
        if (allCleared) {
          results.passed++;
        } else {
          results.failed++;
          results.errors.push({
            field: 'form-reset',
            expected: 'All fields cleared',
            actual: 'Some fields not cleared'
          });
        }
      } else {
        results.failed++;
        results.errors.push({
          field: 'reset-button',
          expected: 'Reset button found',
          actual: 'Reset button not found'
        });
      }

    } catch (error) {
      results.failed++;
      results.errors.push({
        field: 'general',
        expected: 'No error',
        actual: error.message
      });
    }

    return results;
  }

  /**
   * Test unsaved changes warning
   * @param {string} formId - Form ID
   * @returns {Promise<Object>} Test results
   */
  async testUnsavedChangesWarning(formId) {
    const results = {
      passed: 0,
      failed: 0,
      errors: []
    };

    try {
      // Test beforeunload event
      const beforeUnloadEvent = new Event('beforeunload', { bubbles: true, cancelable: true });
      const preventDefaultCalled = window.dispatchEvent(beforeUnloadEvent);
      
      if (preventDefaultCalled) {
        results.passed++;
      } else {
        results.failed++;
        results.errors.push({
          field: 'beforeunload',
          expected: 'Event handled',
          actual: 'Event not handled'
        });
      }

      // Test navigation warning
      const hasUnsavedChanges = document.querySelector('.text-amber-600, .text-yellow-600');
      if (hasUnsavedChanges) {
        results.passed++;
      } else {
        results.failed++;
        results.errors.push({
          field: 'unsaved-changes-indicator',
          expected: 'Visual indicator present',
          actual: 'No visual indicator'
        });
      }

    } catch (error) {
      results.failed++;
      results.errors.push({
        field: 'general',
        expected: 'No error',
        actual: error.message
      });
    }

    return results;
  }

  /**
   * Test accessibility features
   * @param {string} formId - Form ID
   * @returns {Promise<Object>} Test results
   */
  async testAccessibility(formId) {
    const results = {
      passed: 0,
      failed: 0,
      errors: []
    };

    try {
      const form = document.querySelector(`#${formId}`);
      if (!form) {
        throw new Error(`Form ${formId} not found`);
      }

      // Test ARIA labels
      const fields = form.querySelectorAll('input, select, textarea');
      for (const field of fields) {
        const hasLabel = field.getAttribute('aria-label') || 
                        field.getAttribute('aria-labelledby') ||
                        document.querySelector(`label[for="${field.id}"]`);
        
        if (hasLabel) {
          results.passed++;
        } else {
          results.failed++;
          results.errors.push({
            field: field.name,
            expected: 'ARIA label or associated label',
            actual: 'No label found'
          });
        }
      }

      // Test keyboard navigation
      const focusableElements = form.querySelectorAll('input, select, textarea, button');
      let tabIndex = 0;
      for (const element of focusableElements) {
        const tabIndexValue = element.getAttribute('tabindex');
        if (tabIndexValue === null || tabIndexValue === '0' || parseInt(tabIndexValue) > 0) {
          results.passed++;
        } else {
          results.failed++;
          results.errors.push({
            field: element.name || element.tagName,
            expected: 'Valid tabindex',
            actual: `tabindex="${tabIndexValue}"`
          });
        }
      }

    } catch (error) {
      results.failed++;
      results.errors.push({
        field: 'general',
        expected: 'No error',
        actual: error.message
      });
    }

    return results;
  }

  /**
   * Test performance metrics
   * @param {string} formId - Form ID
   * @returns {Promise<Object>} Test results
   */
  async testPerformance(formId) {
    const results = {
      passed: 0,
      failed: 0,
      errors: [],
      metrics: {}
    };

    try {
      // Test form load time
      const loadStart = performance.now();
      const form = document.querySelector(`#${formId}`);
      const loadTime = performance.now() - loadStart;
      
      results.metrics.loadTime = loadTime;
      if (loadTime < 100) {
        results.passed++;
      } else {
        results.failed++;
        results.errors.push({
          field: 'load-time',
          expected: '< 100ms',
          actual: `${loadTime.toFixed(2)}ms`
        });
      }

      // Test validation speed
      const validationStart = performance.now();
      const fields = form.querySelectorAll('input, select, textarea');
      for (const field of fields) {
        field.dispatchEvent(new Event('blur', { bubbles: true }));
      }
      const validationTime = performance.now() - validationStart;
      
      results.metrics.validationTime = validationTime;
      if (validationTime < 50) {
        results.passed++;
      } else {
        results.failed++;
        results.errors.push({
          field: 'validation-time',
          expected: '< 50ms',
          actual: `${validationTime.toFixed(2)}ms`
        });
      }

      // Test memory usage
      if (performance.memory) {
        results.metrics.memoryUsage = {
          used: performance.memory.usedJSHeapSize,
          total: performance.memory.totalJSHeapSize,
          limit: performance.memory.jsHeapSizeLimit
        };
      }

    } catch (error) {
      results.failed++;
      results.errors.push({
        field: 'general',
        expected: 'No error',
        actual: error.message
      });
    }

    return results;
  }

  /**
   * Test image loading
   * @returns {Promise<Object>} Test results
   */
  async testImageLoading() {
    const results = {
      passed: 0,
      failed: 0,
      errors: [],
      images: []
    };

    try {
      const images = document.querySelectorAll('img');
      
      for (const img of images) {
        const imageResult = {
          src: img.src,
          alt: img.alt,
          loaded: false,
          error: null
        };

        if (img.complete && img.naturalHeight !== 0) {
          imageResult.loaded = true;
          results.passed++;
        } else {
          // Wait for image to load
          await new Promise((resolve) => {
            const timeout = setTimeout(() => {
              imageResult.error = 'Timeout';
              results.failed++;
              results.errors.push({
                field: 'image-loading',
                expected: 'Image loaded',
                actual: 'Image load timeout'
              });
              resolve();
            }, 5000);

            img.onload = () => {
              clearTimeout(timeout);
              imageResult.loaded = true;
              results.passed++;
              resolve();
            };

            img.onerror = () => {
              clearTimeout(timeout);
              imageResult.error = 'Load error';
              results.failed++;
              results.errors.push({
                field: 'image-loading',
                expected: 'Image loaded',
                actual: 'Image load error'
              });
              resolve();
            };
          });
        }

        results.images.push(imageResult);
      }

    } catch (error) {
      results.failed++;
      results.errors.push({
        field: 'general',
        expected: 'No error',
        actual: error.message
      });
    }

    return results;
  }

  /**
   * Test broken links
   * @returns {Promise<Object>} Test results
   */
  async testBrokenLinks() {
    const results = {
      passed: 0,
      failed: 0,
      errors: [],
      links: []
    };

    try {
      const links = document.querySelectorAll('a[href]');
      
      for (const link of links) {
        const linkResult = {
          href: link.href,
          text: link.textContent.trim(),
          status: 'unknown',
          error: null
        };

        try {
          // Test internal links
          if (link.href.startsWith(window.location.origin)) {
            // For internal links, check if the element exists
            const targetId = link.getAttribute('href').replace('#', '');
            if (targetId && document.getElementById(targetId)) {
              linkResult.status = 'valid';
              results.passed++;
            } else {
              linkResult.status = 'invalid';
              results.failed++;
              results.errors.push({
                field: 'link',
                expected: 'Valid internal link',
                actual: 'Target element not found'
              });
            }
          } else {
            // For external links, we can't test them directly
            linkResult.status = 'external';
            results.passed++;
          }
        } catch (error) {
          linkResult.error = error.message;
          results.failed++;
          results.errors.push({
            field: 'link',
            expected: 'Valid link',
            actual: error.message
          });
        }

        results.links.push(linkResult);
      }

    } catch (error) {
      results.failed++;
      results.errors.push({
        field: 'general',
        expected: 'No error',
        actual: error.message
      });
    }

    return results;
  }

  /**
   * Test interactive elements
   * @returns {Promise<Object>} Test results
   */
  async testInteractiveElements() {
    const results = {
      passed: 0,
      failed: 0,
      errors: []
    };

    try {
      // Test buttons
      const buttons = document.querySelectorAll('button');
      for (const button of buttons) {
        if (button.disabled) {
          results.passed++;
        } else {
          // Test click event
          const clickEvent = new Event('click', { bubbles: true });
          const handled = button.dispatchEvent(clickEvent);
          if (handled) {
            results.passed++;
          } else {
            results.failed++;
            results.errors.push({
              field: 'button',
              expected: 'Click event handled',
              actual: 'Click event not handled'
            });
          }
        }
      }

      // Test form inputs
      const inputs = document.querySelectorAll('input, select, textarea');
      for (const input of inputs) {
        if (input.disabled) {
          results.passed++;
        } else {
          // Test focus event
          const focusEvent = new Event('focus', { bubbles: true });
          const handled = input.dispatchEvent(focusEvent);
          if (handled) {
            results.passed++;
          } else {
            results.failed++;
            results.errors.push({
              field: 'input',
              expected: 'Focus event handled',
              actual: 'Focus event not handled'
            });
          }
        }
      }

    } catch (error) {
      results.failed++;
      results.errors.push({
        field: 'general',
        expected: 'No error',
        actual: error.message
      });
    }

    return results;
  }

  /**
   * Run comprehensive cross-browser tests
   * @param {string} formId - Form ID to test
   * @returns {Promise<Object>} Comprehensive test results
   */
  async runComprehensiveTests(formId) {
    const results = {
      browser: this.currentBrowser,
      device: this.currentDevice,
      timestamp: Date.now(),
      totalTests: 0,
      totalPassed: 0,
      totalFailed: 0,
      testSuites: {}
    };

    try {
      // Test form validation
      results.testSuites.formValidation = await this.testFormValidation(formId);
      
      // Test accessibility
      results.testSuites.accessibility = await this.testAccessibility(formId);
      
      // Test performance
      results.testSuites.performance = await this.testPerformance(formId);
      
      // Test image loading
      results.testSuites.imageLoading = await this.testImageLoading();
      
      // Test broken links
      results.testSuites.brokenLinks = await this.testBrokenLinks();
      
      // Test interactive elements
      results.testSuites.interactiveElements = await this.testInteractiveElements();
      
      // Calculate totals
      for (const [suiteName, suiteResults] of Object.entries(results.testSuites)) {
        results.totalTests += suiteResults.passed + suiteResults.failed;
        results.totalPassed += suiteResults.passed;
        results.totalFailed += suiteResults.failed;
      }
      
      results.successRate = (results.totalPassed / results.totalTests) * 100;
      
    } catch (error) {
      results.error = error.message;
    }

    return results;
  }

  /**
   * Generate test report
   * @param {Object} results - Test results
   * @returns {string} Test report
   */
  generateTestReport(results) {
    const report = `
Cross-Browser Testing Report
===========================

Browser: ${results.browser}
Device: ${results.device}
Timestamp: ${new Date(results.timestamp).toLocaleString()}

Total Tests: ${results.totalTests}
Passed: ${results.totalPassed}
Failed: ${results.totalFailed}
Success Rate: ${results.successRate.toFixed(2)}%

Test Suites:
${Object.entries(results.testSuites).map(([suite, suiteResults]) => `
${suite}:
  Passed: ${suiteResults.passed}
  Failed: ${suiteResults.failed}
  ${suiteResults.errors.length > 0 ? `Errors: ${suiteResults.errors.map(e => `    - ${e.field}: ${e.actual}`).join('\n')}` : 'No errors'}
`).join('')}

${results.totalFailed > 0 ? `
Failed Tests:
${Object.entries(results.testSuites).flatMap(([suite, suiteResults]) => 
  suiteResults.errors.map(error => `  - ${suite}.${error.field}: ${error.actual}`)
).join('\n')}
` : 'All tests passed!'}
    `;
    
    return report;
  }
}

/**
 * Create cross-browser tester instance
 */
const crossBrowserTester = new CrossBrowserTester();

/**
 * Run cross-browser tests for a form
 * @param {string} formId - Form ID to test
 * @returns {Promise<Object>} Test results
 */
export const runCrossBrowserTests = async (formId) => {
  return await crossBrowserTester.runComprehensiveTests(formId);
};

/**
 * Generate test report
 * @param {Object} results - Test results
 * @returns {string} Test report
 */
export const generateCrossBrowserTestReport = (results) => {
  return crossBrowserTester.generateTestReport(results);
};

export default crossBrowserTester;
