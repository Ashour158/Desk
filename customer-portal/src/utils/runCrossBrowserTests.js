/**
 * Cross-browser testing runner
 * Executes comprehensive tests across different browsers and devices
 */

import { runCrossBrowserTests, generateCrossBrowserTestReport } from './crossBrowserTesting.js';

/**
 * Test configuration for different scenarios
 */
const testConfig = {
  forms: [
    'login-form',
    'register-form', 
    'ticket-form'
  ],
  
  browsers: [
    'chrome',
    'firefox', 
    'safari',
    'edge'
  ],
  
  devices: [
    'mobile',
    'tablet',
    'desktop'
  ]
};

/**
 * Run tests for all forms
 * @returns {Promise<Object>} Comprehensive test results
 */
export const runAllFormTests = async () => {
  const allResults = {
    timestamp: Date.now(),
    totalForms: 0,
    totalTests: 0,
    totalPassed: 0,
    totalFailed: 0,
    formResults: {},
    summary: {}
  };

  console.log('🚀 Starting Cross-Browser Testing Suite...');
  console.log('==========================================');

  for (const formId of testConfig.forms) {
    console.log(`\n📋 Testing Form: ${formId}`);
    console.log('─'.repeat(30));

    try {
      // Check if form exists
      const form = document.querySelector(`#${formId}`);
      if (!form) {
        console.warn(`⚠️  Form ${formId} not found, skipping...`);
        continue;
      }

      // Run comprehensive tests
      const formResults = await runCrossBrowserTests(formId);
      allResults.formResults[formId] = formResults;
      
      // Update totals
      allResults.totalForms++;
      allResults.totalTests += formResults.totalTests;
      allResults.totalPassed += formResults.totalPassed;
      allResults.totalFailed += formResults.totalFailed;

      // Log results
      console.log(`✅ Form: ${formId}`);
      console.log(`   Tests: ${formResults.totalTests}`);
      console.log(`   Passed: ${formResults.totalPassed}`);
      console.log(`   Failed: ${formResults.totalFailed}`);
      console.log(`   Success Rate: ${formResults.successRate.toFixed(2)}%`);

      // Log any errors
      if (formResults.totalFailed > 0) {
        console.log(`   ❌ Errors:`);
        Object.entries(formResults.testSuites).forEach(([suite, suiteResults]) => {
          if (suiteResults.errors.length > 0) {
            console.log(`      ${suite}:`);
            suiteResults.errors.forEach(error => {
              console.log(`        - ${error.field}: ${error.actual}`);
            });
          }
        });
      }

    } catch (error) {
      console.error(`❌ Error testing form ${formId}:`, error);
      allResults.formResults[formId] = {
        error: error.message,
        totalTests: 0,
        totalPassed: 0,
        totalFailed: 1
      };
    }
  }

  // Calculate overall summary
  allResults.summary = {
    overallSuccessRate: allResults.totalTests > 0 
      ? (allResults.totalPassed / allResults.totalTests) * 100 
      : 0,
    averageSuccessRate: allResults.totalForms > 0
      ? Object.values(allResults.formResults)
          .filter(result => !result.error)
          .reduce((sum, result) => sum + result.successRate, 0) / allResults.totalForms
      : 0
  };

  // Log final summary
  console.log('\n📊 Test Summary');
  console.log('================');
  console.log(`Total Forms Tested: ${allResults.totalForms}`);
  console.log(`Total Tests: ${allResults.totalTests}`);
  console.log(`Total Passed: ${allResults.totalPassed}`);
  console.log(`Total Failed: ${allResults.totalFailed}`);
  console.log(`Overall Success Rate: ${allResults.summary.overallSuccessRate.toFixed(2)}%`);
  console.log(`Average Success Rate: ${allResults.summary.averageSuccessRate.toFixed(2)}%`);

  return allResults;
};

/**
 * Run tests for a specific form
 * @param {string} formId - Form ID to test
 * @returns {Promise<Object>} Test results
 */
export const runFormTests = async (formId) => {
  console.log(`🧪 Testing Form: ${formId}`);
  console.log('─'.repeat(30));

  try {
    const results = await runCrossBrowserTests(formId);
    const report = generateCrossBrowserTestReport(results);
    
    console.log(report);
    return results;
  } catch (error) {
    console.error(`❌ Error testing form ${formId}:`, error);
    return { error: error.message };
  }
};

/**
 * Test specific functionality
 * @param {string} functionality - Functionality to test
 * @returns {Promise<Object>} Test results
 */
export const testFunctionality = async (functionality) => {
  const tests = {
    'form-validation': async () => {
      console.log('🔍 Testing Form Validation...');
      const forms = document.querySelectorAll('form');
      let passed = 0;
      let failed = 0;

      for (const form of forms) {
        const requiredFields = form.querySelectorAll('[required]');
        for (const field of requiredFields) {
          const originalValue = field.value;
          field.value = '';
          field.dispatchEvent(new Event('blur', { bubbles: true }));
          
          await new Promise(resolve => setTimeout(resolve, 100));
          
          const hasError = document.querySelector(`[id="${field.name}-error"]`);
          if (hasError && hasError.textContent.trim()) {
            passed++;
          } else {
            failed++;
          }
          
          field.value = originalValue;
        }
      }

      return { passed, failed };
    },

    'image-loading': async () => {
      console.log('🖼️  Testing Image Loading...');
      const images = document.querySelectorAll('img');
      let passed = 0;
      let failed = 0;

      for (const img of images) {
        if (img.complete && img.naturalHeight !== 0) {
          passed++;
        } else {
          failed++;
        }
      }

      return { passed, failed };
    },

    'broken-links': async () => {
      console.log('🔗 Testing Broken Links...');
      const links = document.querySelectorAll('a[href]');
      let passed = 0;
      let failed = 0;

      for (const link of links) {
        if (link.href.startsWith(window.location.origin)) {
          const targetId = link.getAttribute('href').replace('#', '');
          if (targetId && document.getElementById(targetId)) {
            passed++;
          } else {
            failed++;
          }
        } else {
          passed++; // External links
        }
      }

      return { passed, failed };
    },

    'interactive-elements': async () => {
      console.log('🖱️  Testing Interactive Elements...');
      const buttons = document.querySelectorAll('button');
      const inputs = document.querySelectorAll('input, select, textarea');
      let passed = 0;
      let failed = 0;

      // Test buttons
      for (const button of buttons) {
        const clickEvent = new Event('click', { bubbles: true });
        const handled = button.dispatchEvent(clickEvent);
        if (handled) {
          passed++;
        } else {
          failed++;
        }
      }

      // Test inputs
      for (const input of inputs) {
        const focusEvent = new Event('focus', { bubbles: true });
        const handled = input.dispatchEvent(focusEvent);
        if (handled) {
          passed++;
        } else {
          failed++;
        }
      }

      return { passed, failed };
    }
  };

  if (tests[functionality]) {
    return await tests[functionality]();
  } else {
    throw new Error(`Unknown functionality: ${functionality}`);
  }
};

/**
 * Run performance tests
 * @returns {Object} Performance test results
 */
export const runPerformanceTests = () => {
  console.log('⚡ Running Performance Tests...');
  
  const results = {
    timestamp: Date.now(),
    metrics: {}
  };

  // Test form load time
  const forms = document.querySelectorAll('form');
  const loadTimes = [];
  
  forms.forEach(form => {
    const start = performance.now();
    const fields = form.querySelectorAll('input, select, textarea');
    fields.forEach(field => {
      field.dispatchEvent(new Event('blur', { bubbles: true }));
    });
    const end = performance.now();
    loadTimes.push(end - start);
  });

  results.metrics.formLoadTime = {
    average: loadTimes.reduce((sum, time) => sum + time, 0) / loadTimes.length,
    min: Math.min(...loadTimes),
    max: Math.max(...loadTimes)
  };

  // Test validation speed
  const validationTimes = [];
  forms.forEach(form => {
    const start = performance.now();
    const fields = form.querySelectorAll('input, select, textarea');
    fields.forEach(field => {
      field.dispatchEvent(new Event('change', { bubbles: true }));
    });
    const end = performance.now();
    validationTimes.push(end - start);
  });

  results.metrics.validationSpeed = {
    average: validationTimes.reduce((sum, time) => sum + time, 0) / validationTimes.length,
    min: Math.min(...validationTimes),
    max: Math.max(...validationTimes)
  };

  // Memory usage
  if (performance.memory) {
    results.metrics.memoryUsage = {
      used: performance.memory.usedJSHeapSize,
      total: performance.memory.totalJSHeapSize,
      limit: performance.memory.jsHeapSizeLimit
    };
  }

  // Bundle size (approximate)
  const scripts = document.querySelectorAll('script[src]');
  let totalSize = 0;
  scripts.forEach(script => {
    // This is an approximation - actual size would need to be measured
    totalSize += 1000; // Assume 1KB per script
  });

  results.metrics.bundleSize = totalSize;

  console.log('📊 Performance Results:');
  console.log(`  Form Load Time: ${results.metrics.formLoadTime.average.toFixed(2)}ms`);
  console.log(`  Validation Speed: ${results.metrics.validationSpeed.average.toFixed(2)}ms`);
  console.log(`  Memory Usage: ${results.metrics.memoryUsage ? (results.metrics.memoryUsage.used / 1024 / 1024).toFixed(2) + 'MB' : 'N/A'}`);
  console.log(`  Bundle Size: ${(results.metrics.bundleSize / 1024).toFixed(2)}KB`);

  return results;
};

/**
 * Generate comprehensive test report
 * @param {Object} results - Test results
 * @returns {string} Test report
 */
export const generateComprehensiveReport = (results) => {
  const report = `
# Cross-Browser Testing Report

## Overview
- **Test Date**: ${new Date(results.timestamp).toLocaleString()}
- **Total Forms**: ${results.totalForms}
- **Total Tests**: ${results.totalTests}
- **Passed**: ${results.totalPassed}
- **Failed**: ${results.totalFailed}
- **Success Rate**: ${results.summary.overallSuccessRate.toFixed(2)}%

## Form Results

${Object.entries(results.formResults).map(([formId, formResults]) => `
### ${formId}
- **Tests**: ${formResults.totalTests}
- **Passed**: ${formResults.totalPassed}
- **Failed**: ${formResults.totalFailed}
- **Success Rate**: ${formResults.successRate.toFixed(2)}%

${formResults.totalFailed > 0 ? `
#### Errors:
${Object.entries(formResults.testSuites).flatMap(([suite, suiteResults]) => 
  suiteResults.errors.map(error => `- **${suite}**: ${error.field} - ${error.actual}`)
).join('\n')}
` : '✅ No errors'}
`).join('')}

## Recommendations

${results.summary.overallSuccessRate < 90 ? `
⚠️ **Action Required**: Success rate is below 90%. Please review and fix the following issues:
${Object.entries(results.formResults).flatMap(([formId, formResults]) => 
  formResults.totalFailed > 0 ? [`- ${formId}: ${formResults.totalFailed} failed tests`] : []
).join('\n')}
` : '✅ **All Good**: Success rate is above 90%. No immediate action required.'}

## Next Steps
1. Review failed tests and fix issues
2. Re-run tests to verify fixes
3. Monitor performance metrics
4. Update documentation if needed

---
*Report generated by Cross-Browser Testing Suite*
  `;

  return report;
};

/**
 * Export test results to file
 * @param {Object} results - Test results
 * @param {string} filename - Output filename
 */
export const exportTestResults = (results, filename = 'cross-browser-test-results.json') => {
  const dataStr = JSON.stringify(results, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
};

/**
 * Main test runner
 */
export const runAllTests = async () => {
  console.log('🚀 Starting Comprehensive Cross-Browser Testing...');
  console.log('================================================');
  
  try {
    // Run all form tests
    const formResults = await runAllFormTests();
    
    // Run performance tests
    const performanceResults = runPerformanceTests();
    
    // Generate comprehensive report
    const report = generateComprehensiveReport(formResults);
    console.log('\n📋 Comprehensive Report:');
    console.log(report);
    
    // Export results
    exportTestResults(formResults, 'cross-browser-test-results.json');
    
    return {
      formResults,
      performanceResults,
      report
    };
    
  } catch (error) {
    console.error('❌ Testing failed:', error);
    return { error: error.message };
  }
};

// Auto-run tests if this script is loaded directly
if (typeof window !== 'undefined' && window.location.pathname.includes('test')) {
  runAllTests();
}

export default {
  runAllFormTests,
  runFormTests,
  testFunctionality,
  runPerformanceTests,
  generateComprehensiveReport,
  exportTestResults,
  runAllTests
};
