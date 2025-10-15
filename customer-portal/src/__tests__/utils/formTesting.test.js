/**
 * Comprehensive Form Testing Utilities Tests
 * Tests critical form testing utilities including validation, submission, and user interactions.
 */

import { 
  formTestConfig, 
  formTestUtils, 
  formTestSuites, 
  runFormTests 
} from '../../utils/formTesting';

// Mock DOM elements
const mockForm = {
  querySelector: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  submit: jest.fn(),
  reset: jest.fn(),
  checkValidity: jest.fn(),
  reportValidity: jest.fn()
};

const mockInput = {
  value: '',
  checked: false,
  dispatchEvent: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn()
};

const mockButton = {
  click: jest.fn(),
  disabled: false,
  addEventListener: jest.fn(),
  removeEventListener: jest.fn()
};

// Mock document
Object.defineProperty(document, 'querySelector', {
  value: jest.fn(),
  writable: true
});

Object.defineProperty(document, 'createElement', {
  value: jest.fn(),
  writable: true
});

// Mock window
Object.defineProperty(window, 'setTimeout', {
  value: jest.fn((callback) => {
    callback();
    return 1;
  }),
  writable: true
});

Object.defineProperty(window, 'clearTimeout', {
  value: jest.fn(),
  writable: true
});

describe('Form Testing Utilities', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    document.querySelector.mockImplementation((selector) => {
      if (selector.includes('input')) return mockInput;
      if (selector.includes('button')) return mockButton;
      if (selector.includes('form')) return mockForm;
      return null;
    });
  });

  describe('formTestConfig', () => {
    it('should have correct default timeout values', () => {
      expect(formTestConfig.defaultTimeout).toBe(5000);
      expect(formTestConfig.validationTimeout).toBe(1000);
      expect(formTestConfig.submissionTimeout).toBe(10000);
    });

    it('should have valid test data', () => {
      expect(formTestConfig.validTestData.email).toBe('test@example.com');
      expect(formTestConfig.validTestData.password).toBe('TestPassword123');
      expect(formTestConfig.validTestData.firstName).toBe('John');
      expect(formTestConfig.validTestData.lastName).toBe('Doe');
    });

    it('should have invalid test data', () => {
      expect(formTestConfig.invalidTestData.email).toBe('invalid-email');
      expect(formTestConfig.invalidTestData.password).toBe('123');
      expect(formTestConfig.invalidTestData.firstName).toBe('');
      expect(formTestConfig.invalidTestData.lastName).toBe('');
    });
  });

  describe('formTestUtils.waitForElement', () => {
    it('should resolve immediately if element exists', async () => {
      const mockElement = { id: 'test-element' };
      document.querySelector.mockReturnValue(mockElement);

      const result = await formTestUtils.waitForElement('#test-element');

      expect(result).toBe(mockElement);
      expect(document.querySelector).toHaveBeenCalledWith('#test-element');
    });

    it('should wait for element to appear', async () => {
      let callCount = 0;
      document.querySelector.mockImplementation(() => {
        callCount++;
        return callCount > 2 ? { id: 'test-element' } : null;
      });

      // Mock MutationObserver
      const mockObserver = {
        observe: jest.fn(),
        disconnect: jest.fn()
      };
      global.MutationObserver = jest.fn(() => mockObserver);

      const result = await formTestUtils.waitForElement('#test-element');

      expect(result).toEqual({ id: 'test-element' });
      expect(mockObserver.observe).toHaveBeenCalledWith(document.body, {
        childList: true,
        subtree: true
      });
    });

    it('should reject after timeout', async () => {
      document.querySelector.mockReturnValue(null);
      
      // Mock MutationObserver
      const mockObserver = {
        observe: jest.fn(),
        disconnect: jest.fn()
      };
      global.MutationObserver = jest.fn(() => mockObserver);

      await expect(formTestUtils.waitForElement('#test-element', 100)).rejects.toThrow(
        'Element #test-element not found within 100ms'
      );
    });
  });

  describe('formTestUtils.fillField', () => {
    it('should fill input field with value', () => {
      const mockElement = { ...mockInput };
      document.querySelector.mockReturnValue(mockElement);

      formTestUtils.fillField('email', 'test@example.com', 'input');

      expect(document.querySelector).toHaveBeenCalledWith('input[name="email"]');
      expect(mockElement.value).toBe('test@example.com');
      expect(mockElement.dispatchEvent).toHaveBeenCalledWith(
        expect.objectContaining({ type: 'change', bubbles: true })
      );
      expect(mockElement.dispatchEvent).toHaveBeenCalledWith(
        expect.objectContaining({ type: 'blur', bubbles: true })
      );
    });

    it('should fill checkbox field', () => {
      const mockElement = { ...mockInput };
      document.querySelector.mockReturnValue(mockElement);

      formTestUtils.fillField('agree', true, 'checkbox');

      expect(document.querySelector).toHaveBeenCalledWith('input[name="agree"]');
      expect(mockElement.checked).toBe(true);
    });

    it('should fill select field', () => {
      const mockElement = { ...mockInput };
      document.querySelector.mockReturnValue(mockElement);

      formTestUtils.fillField('country', 'US', 'select');

      expect(document.querySelector).toHaveBeenCalledWith('select[name="country"]');
      expect(mockElement.value).toBe('US');
    });

    it('should throw error if field not found', () => {
      document.querySelector.mockReturnValue(null);

      expect(() => {
        formTestUtils.fillField('nonexistent', 'value', 'input');
      }).toThrow('Field nonexistent not found');
    });
  });

  describe('formTestUtils.getFieldValue', () => {
    it('should get input field value', () => {
      const mockElement = { value: 'test@example.com' };
      document.querySelector.mockReturnValue(mockElement);

      const value = formTestUtils.getFieldValue('email', 'input');

      expect(value).toBe('test@example.com');
      expect(document.querySelector).toHaveBeenCalledWith('input[name="email"]');
    });

    it('should get checkbox field value', () => {
      const mockElement = { checked: true };
      document.querySelector.mockReturnValue(mockElement);

      const value = formTestUtils.getFieldValue('agree', 'checkbox');

      expect(value).toBe(true);
    });

    it('should return null if field not found', () => {
      document.querySelector.mockReturnValue(null);

      const value = formTestUtils.getFieldValue('nonexistent', 'input');

      expect(value).toBeNull();
    });
  });

  describe('formTestUtils.submitForm', () => {
    it('should submit form successfully', async () => {
      const mockElement = { ...mockForm };
      document.querySelector.mockReturnValue(mockElement);
      mockElement.submit.mockResolvedValue();

      await formTestUtils.submitForm('test-form');

      expect(document.querySelector).toHaveBeenCalledWith('#test-form');
      expect(mockElement.submit).toHaveBeenCalled();
    });

    it('should handle form submission error', async () => {
      const mockElement = { ...mockForm };
      document.querySelector.mockReturnValue(mockElement);
      mockElement.submit.mockRejectedValue(new Error('Submission failed'));

      await expect(formTestUtils.submitForm('test-form')).rejects.toThrow('Submission failed');
    });
  });

  describe('formTestUtils.clearForm', () => {
    it('should clear all form fields', () => {
      const mockElement = { ...mockForm };
      document.querySelector.mockReturnValue(mockElement);

      formTestUtils.clearForm('test-form');

      expect(document.querySelector).toHaveBeenCalledWith('#test-form');
      expect(mockElement.reset).toHaveBeenCalled();
    });
  });

  describe('formTestUtils.validateForm', () => {
    it('should validate form successfully', () => {
      const mockElement = { ...mockForm };
      document.querySelector.mockReturnValue(mockElement);
      mockElement.checkValidity.mockReturnValue(true);

      const isValid = formTestUtils.validateForm('test-form');

      expect(isValid).toBe(true);
      expect(mockElement.checkValidity).toHaveBeenCalled();
    });

    it('should return false for invalid form', () => {
      const mockElement = { ...mockForm };
      document.querySelector.mockReturnValue(mockElement);
      mockElement.checkValidity.mockReturnValue(false);

      const isValid = formTestUtils.validateForm('test-form');

      expect(isValid).toBe(false);
    });
  });

  describe('formTestSuites.testValidation', () => {
    it('should test validation with invalid data', async () => {
      const mockElement = { ...mockForm };
      document.querySelector.mockReturnValue(mockElement);
      mockElement.checkValidity.mockReturnValue(false);

      const result = await formTestSuites.testValidation(formTestConfig.invalidTestData);

      expect(result.passed).toBe(0);
      expect(result.failed).toBeGreaterThan(0);
      expect(result.errors).toBeDefined();
    });

    it('should test validation with valid data', async () => {
      const mockElement = { ...mockForm };
      document.querySelector.mockReturnValue(mockElement);
      mockElement.checkValidity.mockReturnValue(true);

      const result = await formTestSuites.testValidation(formTestConfig.validTestData);

      expect(result.passed).toBeGreaterThan(0);
      expect(result.failed).toBe(0);
      expect(result.errors).toBeDefined();
    });

    it('should test validation with custom error messages', async () => {
      const mockElement = { ...mockForm };
      document.querySelector.mockReturnValue(mockElement);
      mockElement.checkValidity.mockReturnValue(false);

      const customErrors = {
        email: 'Please enter a valid email address',
        password: 'Password must be at least 8 characters'
      };

      const result = await formTestSuites.testValidation(
        formTestConfig.invalidTestData,
        customErrors
      );

      expect(result.passed).toBe(0);
      expect(result.failed).toBeGreaterThan(0);
      expect(result.errors).toBeDefined();
    });
  });

  describe('formTestSuites.testSubmission', () => {
    it('should test successful form submission', async () => {
      const mockElement = { ...mockForm };
      document.querySelector.mockReturnValue(mockElement);
      mockElement.submit.mockResolvedValue();

      const result = await formTestSuites.testSubmission(
        formTestConfig.validTestData,
        true
      );

      expect(result.passed).toBeGreaterThan(0);
      expect(result.failed).toBe(0);
      expect(result.submissionTime).toBeDefined();
    });

    it('should test form submission with error', async () => {
      const mockElement = { ...mockForm };
      document.querySelector.mockReturnValue(mockElement);
      mockElement.submit.mockRejectedValue(new Error('Submission failed'));

      const result = await formTestSuites.testSubmission(
        formTestConfig.validTestData,
        true
      );

      expect(result.passed).toBe(0);
      expect(result.failed).toBeGreaterThan(0);
      expect(result.errors).toBeDefined();
    });

    it('should test form submission without validation', async () => {
      const mockElement = { ...mockForm };
      document.querySelector.mockReturnValue(mockElement);
      mockElement.submit.mockResolvedValue();

      const result = await formTestSuites.testSubmission(
        formTestConfig.validTestData,
        false
      );

      expect(result.passed).toBeGreaterThan(0);
      expect(result.failed).toBe(0);
    });
  });

  describe('formTestSuites.testUserInteractions', () => {
    it('should test user interactions', async () => {
      const mockElement = { ...mockForm };
      document.querySelector.mockReturnValue(mockElement);

      const result = await formTestSuites.testUserInteractions();

      expect(result.passed).toBeGreaterThan(0);
      expect(result.failed).toBe(0);
      expect(result.interactions).toBeDefined();
    });
  });

  describe('formTestSuites.testAccessibility', () => {
    it('should test form accessibility', async () => {
      const mockElement = { ...mockForm };
      document.querySelector.mockReturnValue(mockElement);

      const result = await formTestSuites.testAccessibility();

      expect(result.passed).toBeGreaterThan(0);
      expect(result.failed).toBe(0);
      expect(result.accessibility).toBeDefined();
    });
  });

  describe('formTestSuites.testPerformance', () => {
    it('should test form performance', async () => {
      const mockElement = { ...mockForm };
      document.querySelector.mockReturnValue(mockElement);

      const result = await formTestSuites.testPerformance();

      expect(result.passed).toBeGreaterThan(0);
      expect(result.failed).toBe(0);
      expect(result.performance).toBeDefined();
    });
  });

  describe('runFormTests', () => {
    it('should run comprehensive form tests', async () => {
      const mockElement = { ...mockForm };
      document.querySelector.mockReturnValue(mockElement);
      mockElement.checkValidity.mockReturnValue(true);
      mockElement.submit.mockResolvedValue();

      const result = await runFormTests('test-form');

      expect(result.formId).toBe('test-form');
      expect(result.totalTests).toBeGreaterThan(0);
      expect(result.testSuites).toBeDefined();
      expect(result.testSuites.validation).toBeDefined();
      expect(result.testSuites.submission).toBeDefined();
      expect(result.testSuites.userInteractions).toBeDefined();
      expect(result.testSuites.accessibility).toBeDefined();
      expect(result.testSuites.performance).toBeDefined();
    });

    it('should handle form test errors gracefully', async () => {
      document.querySelector.mockReturnValue(null);

      const result = await runFormTests('nonexistent-form');

      expect(result.formId).toBe('nonexistent-form');
      expect(result.totalTests).toBe(0);
      expect(result.passed).toBe(0);
      expect(result.failed).toBe(0);
      expect(result.error).toBeDefined();
    });
  });

  describe('Error Handling', () => {
    it('should handle DOM errors gracefully', async () => {
      document.querySelector.mockImplementation(() => {
        throw new Error('DOM error');
      });

      await expect(formTestUtils.waitForElement('#test-element')).rejects.toThrow('DOM error');
    });

    it('should handle form validation errors', async () => {
      const mockElement = { ...mockForm };
      document.querySelector.mockReturnValue(mockElement);
      mockElement.checkValidity.mockImplementation(() => {
        throw new Error('Validation error');
      });

      const isValid = formTestUtils.validateForm('test-form');

      expect(isValid).toBe(false);
    });

    it('should handle form submission errors', async () => {
      const mockElement = { ...mockForm };
      document.querySelector.mockReturnValue(mockElement);
      mockElement.submit.mockImplementation(() => {
        throw new Error('Submission error');
      });

      await expect(formTestUtils.submitForm('test-form')).rejects.toThrow('Submission error');
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty form data', async () => {
      const result = await formTestSuites.testValidation({});

      expect(result.passed).toBe(0);
      expect(result.failed).toBe(0);
    });

    it('should handle null form data', async () => {
      const result = await formTestSuites.testValidation(null);

      expect(result.passed).toBe(0);
      expect(result.failed).toBe(0);
    });

    it('should handle undefined form data', async () => {
      const result = await formTestSuites.testValidation(undefined);

      expect(result.passed).toBe(0);
      expect(result.failed).toBe(0);
    });

    it('should handle very large form data', async () => {
      const largeData = {};
      for (let i = 0; i < 1000; i++) {
        largeData[`field${i}`] = `value${i}`;
      }

      const result = await formTestSuites.testValidation(largeData);

      expect(result.passed).toBeGreaterThan(0);
      expect(result.failed).toBe(0);
    });
  });

  describe('Performance Tests', () => {
    it('should complete form tests within reasonable time', async () => {
      const startTime = Date.now();
      
      const result = await runFormTests('test-form');
      
      const endTime = Date.now();
      const duration = endTime - startTime;

      expect(duration).toBeLessThan(5000); // Should complete within 5 seconds
      expect(result.totalTests).toBeGreaterThan(0);
    });

    it('should handle concurrent form tests', async () => {
      const promises = [];
      for (let i = 0; i < 5; i++) {
        promises.push(runFormTests(`test-form-${i}`));
      }

      const results = await Promise.all(promises);

      expect(results).toHaveLength(5);
      results.forEach(result => {
        expect(result.formId).toBeDefined();
        expect(result.totalTests).toBeGreaterThan(0);
      });
    });
  });
});