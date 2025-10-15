/**
 * Comprehensive form testing utilities
 * Provides automated testing for form validation, submission, and user interactions
 */

/**
 * Form test configuration
 */
export const formTestConfig = {
  // Test timeouts
  defaultTimeout: 5000,
  validationTimeout: 1000,
  submissionTimeout: 10000,
  
  // Test data
  validTestData: {
    email: 'test@example.com',
    password: 'TestPassword123',
    firstName: 'John',
    lastName: 'Doe',
    subject: 'Test Subject',
    description: 'This is a test description with enough content to pass validation.',
    phone: '+1234567890',
    company: 'Test Company'
  },
  
  invalidTestData: {
    email: 'invalid-email',
    password: '123',
    firstName: '',
    lastName: '',
    subject: 'Hi',
    description: 'Short',
    phone: 'invalid-phone'
  }
};

/**
 * Form test utilities
 */
export const formTestUtils = {
  /**
   * Wait for element to be visible
   * @param {string} selector - CSS selector
   * @param {number} timeout - Timeout in milliseconds
   * @returns {Promise<Element>} Element when visible
   */
  waitForElement: (selector, timeout = formTestConfig.defaultTimeout) => {
    return new Promise((resolve, reject) => {
      const element = document.querySelector(selector);
      if (element) {
        resolve(element);
        return;
      }
      
      const observer = new MutationObserver(() => {
        const element = document.querySelector(selector);
        if (element) {
          observer.disconnect();
          resolve(element);
        }
      });
      
      observer.observe(document.body, {
        childList: true,
        subtree: true
      });
      
      setTimeout(() => {
        observer.disconnect();
        reject(new Error(`Element ${selector} not found within ${timeout}ms`));
      }, timeout);
    });
  },

  /**
   * Fill form field
   * @param {string} fieldName - Field name
   * @param {string} value - Value to set
   * @param {string} fieldType - Field type (input, select, textarea, checkbox)
   */
  fillField: (fieldName, value, fieldType = 'input') => {
    const selector = fieldType === 'checkbox' 
      ? `input[name="${fieldName}"]`
      : `${fieldType}[name="${fieldName}"]`;
    
    const element = document.querySelector(selector);
    if (!element) {
      throw new Error(`Field ${fieldName} not found`);
    }
    
    if (fieldType === 'checkbox') {
      element.checked = value;
    } else {
      element.value = value;
    }
    
    // Trigger change event
    element.dispatchEvent(new Event('change', { bubbles: true }));
    element.dispatchEvent(new Event('blur', { bubbles: true }));
  },

  /**
   * Get field value
   * @param {string} fieldName - Field name
   * @param {string} fieldType - Field type
   * @returns {any} Field value
   */
  getFieldValue: (fieldName, fieldType = 'input') => {
    const selector = fieldType === 'checkbox' 
      ? `input[name="${fieldName}"]`
      : `${fieldType}[name="${fieldName}"]`;
    
    const element = document.querySelector(selector);
    if (!element) {
      throw new Error(`Field ${fieldName} not found`);
    }
    
    return fieldType === 'checkbox' ? element.checked : element.value;
  },

  /**
   * Check if field has error
   * @param {string} fieldName - Field name
   * @returns {boolean} True if field has error
   */
  hasFieldError: (fieldName) => {
    const errorElement = document.querySelector(`[id="${fieldName}-error"]`);
    return errorElement && errorElement.textContent.trim() !== '';
  },

  /**
   * Get field error message
   * @param {string} fieldName - Field name
   * @returns {string} Error message
   */
  getFieldError: (fieldName) => {
    const errorElement = document.querySelector(`[id="${fieldName}-error"]`);
    return errorElement ? errorElement.textContent.trim() : '';
  },

  /**
   * Submit form
   * @param {string} formSelector - Form selector
   */
  submitForm: (formSelector = 'form') => {
    const form = document.querySelector(formSelector);
    if (!form) {
      throw new Error('Form not found');
    }
    
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
      submitButton.click();
    } else {
      form.dispatchEvent(new Event('submit', { bubbles: true }));
    }
  },

  /**
   * Wait for form submission to complete
   * @param {string} formSelector - Form selector
   * @param {number} timeout - Timeout in milliseconds
   */
  waitForSubmission: (formSelector = 'form', timeout = formTestConfig.submissionTimeout) => {
    return new Promise((resolve, reject) => {
      const form = document.querySelector(formSelector);
      if (!form) {
        reject(new Error('Form not found'));
        return;
      }
      
      const submitButton = form.querySelector('button[type="submit"]');
      if (!submitButton) {
        resolve();
        return;
      }
      
      const checkSubmission = () => {
        const isDisabled = submitButton.disabled;
        const isLoading = submitButton.textContent.includes('Submitting') || 
                         submitButton.textContent.includes('Loading');
        
        if (!isDisabled && !isLoading) {
          resolve();
        } else {
          setTimeout(checkSubmission, 100);
        }
      };
      
      setTimeout(() => {
        checkSubmission();
      }, 100);
      
      setTimeout(() => {
        reject(new Error(`Form submission timeout after ${timeout}ms`));
      }, timeout);
    });
  }
};

/**
 * Form test suites
 */
export const formTestSuites = {
  /**
   * Test form validation
   * @param {Object} testData - Test data
   * @param {Object} expectedErrors - Expected validation errors
   */
  testValidation: async (testData, expectedErrors = {}) => {
    const results = {
      passed: 0,
      failed: 0,
      errors: []
    };
    
    try {
      // Fill form with test data
      for (const [fieldName, value] of Object.entries(testData)) {
        const fieldType = fieldName === 'agreeToTerms' ? 'checkbox' : 'input';
        formTestUtils.fillField(fieldName, value, fieldType);
        
        // Wait for validation
        await new Promise(resolve => setTimeout(resolve, formTestConfig.validationTimeout));
        
        // Check for expected error
        const hasError = formTestUtils.hasFieldError(fieldName);
        const expectedError = expectedErrors[fieldName];
        
        if (expectedError) {
          if (hasError) {
            const actualError = formTestUtils.getFieldError(fieldName);
            if (actualError === expectedError) {
              results.passed++;
            } else {
              results.failed++;
              results.errors.push({
                field: fieldName,
                expected: expectedError,
                actual: actualError
              });
            }
          } else {
            results.failed++;
            results.errors.push({
              field: fieldName,
              expected: expectedError,
              actual: 'No error'
            });
          }
        } else {
          if (!hasError) {
            results.passed++;
          } else {
            results.failed++;
            results.errors.push({
              field: fieldName,
              expected: 'No error',
              actual: formTestUtils.getFieldError(fieldName)
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
  },

  /**
   * Test form submission
   * @param {Object} testData - Test data
   * @param {boolean} shouldSucceed - Whether submission should succeed
   */
  testSubmission: async (testData, shouldSucceed = true) => {
    const results = {
      passed: 0,
      failed: 0,
      errors: []
    };
    
    try {
      // Fill form with test data
      for (const [fieldName, value] of Object.entries(testData)) {
        const fieldType = fieldName === 'agreeToTerms' ? 'checkbox' : 'input';
        formTestUtils.fillField(fieldName, value, fieldType);
      }
      
      // Wait for form to be ready
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Submit form
      formTestUtils.submitForm();
      
      // Wait for submission to complete
      await formTestUtils.waitForSubmission();
      
      // Check if submission was successful
      const hasGeneralError = document.querySelector('.bg-red-50, .alert-danger');
      const isSuccess = !hasGeneralError;
      
      if (shouldSucceed && isSuccess) {
        results.passed++;
      } else if (!shouldSucceed && !isSuccess) {
        results.passed++;
      } else {
        results.failed++;
        results.errors.push({
          field: 'submission',
          expected: shouldSucceed ? 'Success' : 'Error',
          actual: isSuccess ? 'Success' : 'Error'
        });
      }
    } catch (error) {
      results.failed++;
      results.errors.push({
        field: 'submission',
        expected: shouldSucceed ? 'Success' : 'Error',
        actual: error.message
      });
    }
    
    return results;
  },

  /**
   * Test form reset functionality
   */
  testReset: async () => {
    const results = {
      passed: 0,
      failed: 0,
      errors: []
    };
    
    try {
      // Fill form with some data
      const testData = {
        email: 'test@example.com',
        firstName: 'John',
        lastName: 'Doe'
      };
      
      for (const [fieldName, value] of Object.entries(testData)) {
        formTestUtils.fillField(fieldName, value);
      }
      
      // Click reset button
      const resetButton = document.querySelector('button[type="button"]');
      if (resetButton && resetButton.textContent.includes('Reset')) {
        resetButton.click();
        
        // Wait for reset to complete
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Check if fields are cleared
        let allCleared = true;
        for (const fieldName of Object.keys(testData)) {
          const value = formTestUtils.getFieldValue(fieldName);
          if (value !== '') {
            allCleared = false;
            break;
          }
        }
        
        if (allCleared) {
          results.passed++;
        } else {
          results.failed++;
          results.errors.push({
            field: 'reset',
            expected: 'All fields cleared',
            actual: 'Some fields not cleared'
          });
        }
      } else {
        results.failed++;
        results.errors.push({
          field: 'reset',
          expected: 'Reset button found',
          actual: 'Reset button not found'
        });
      }
    } catch (error) {
      results.failed++;
      results.errors.push({
        field: 'reset',
        expected: 'No error',
        actual: error.message
      });
    }
    
    return results;
  }
};

/**
 * Run comprehensive form tests
 * @param {string} formId - Form ID to test
 * @returns {Object} Test results
 */
export const runFormTests = async (formId = 'default-form') => {
  const results = {
    formId,
    totalTests: 0,
    passed: 0,
    failed: 0,
    testSuites: {}
  };
  
  try {
    // Test validation with invalid data
    console.log('Testing form validation with invalid data...');
    const validationResults = await formTestSuites.testValidation(
      formTestConfig.invalidTestData,
      {
        email: 'Please enter a valid email address',
        password: 'Password must be at least 8 characters',
        firstName: 'First name is required',
        lastName: 'Last name is required',
        subject: 'Subject must be at least 5 characters',
        description: 'Description must be at least 10 characters'
      }
    );
    
    results.testSuites.validation = validationResults;
    results.totalTests += validationResults.passed + validationResults.failed;
    results.passed += validationResults.passed;
    results.failed += validationResults.failed;
    
    // Test validation with valid data
    console.log('Testing form validation with valid data...');
    const validValidationResults = await formTestSuites.testValidation(
      formTestConfig.validTestData
    );
    
    results.testSuites.validValidation = validValidationResults;
    results.totalTests += validValidationResults.passed + validValidationResults.failed;
    results.passed += validValidationResults.passed;
    results.failed += validValidationResults.failed;
    
    // Test form submission
    console.log('Testing form submission...');
    const submissionResults = await formTestSuites.testSubmission(
      formTestConfig.validTestData,
      true
    );
    
    results.testSuites.submission = submissionResults;
    results.totalTests += submissionResults.passed + submissionResults.failed;
    results.passed += submissionResults.passed;
    results.failed += submissionResults.failed;
    
    // Test form reset
    console.log('Testing form reset...');
    const resetResults = await formTestSuites.testReset();
    
    results.testSuites.reset = resetResults;
    results.totalTests += resetResults.passed + resetResults.failed;
    results.passed += resetResults.passed;
    results.failed += resetResults.failed;
    
  } catch (error) {
    console.error('Form testing failed:', error);
    results.failed++;
    results.totalTests++;
  }
  
  return results;
};

/**
 * Generate test report
 * @param {Object} results - Test results
 * @returns {string} Test report
 */
export const generateTestReport = (results) => {
  const report = `
Form Testing Report
==================

Form ID: ${results.formId}
Total Tests: ${results.totalTests}
Passed: ${results.passed}
Failed: ${results.failed}
Success Rate: ${((results.passed / results.totalTests) * 100).toFixed(2)}%

Test Suites:
${Object.entries(results.testSuites).map(([suite, suiteResults]) => `
${suite}:
  Passed: ${suiteResults.passed}
  Failed: ${suiteResults.failed}
  Errors: ${suiteResults.errors.length > 0 ? suiteResults.errors.map(e => `    - ${e.field}: Expected "${e.expected}", got "${e.actual}"`).join('\n') : 'None'}
`).join('')}

${results.failed > 0 ? `
Failed Tests:
${Object.entries(results.testSuites).flatMap(([suite, suiteResults]) => 
  suiteResults.errors.map(error => `  - ${suite}.${error.field}: ${error.actual}`)
).join('\n')}
` : 'All tests passed!'}
  `;
  
  return report;
};

export default {
  formTestConfig,
  formTestUtils,
  formTestSuites,
  runFormTests,
  generateTestReport
};
