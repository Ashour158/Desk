/**
 * Form documentation generator
 * Creates comprehensive documentation for forms, validation rules, and usage
 */

/**
 * Form documentation configuration
 */
export const documentationConfig = {
  outputFormats: ['markdown', 'html', 'json'],
  includeExamples: true,
  includeValidationRules: true,
  includeAccessibilityInfo: true,
  includeTestingInfo: true,
  includeAnalyticsInfo: true
};

/**
 * Form documentation generator
 */
class FormDocumentationGenerator {
  constructor() {
    this.forms = new Map();
    this.validationRules = new Map();
    this.components = new Map();
  }

  /**
   * Register a form for documentation
   * @param {string} formId - Form ID
   * @param {Object} formConfig - Form configuration
   */
  registerForm(formId, formConfig) {
    this.forms.set(formId, {
      id: formId,
      name: formConfig.name || formId,
      description: formConfig.description || '',
      fields: formConfig.fields || [],
      validationRules: formConfig.validationRules || {},
      submitEndpoint: formConfig.submitEndpoint || '',
      methods: formConfig.methods || ['POST'],
      authentication: formConfig.authentication || 'required',
      permissions: formConfig.permissions || [],
      examples: formConfig.examples || [],
      accessibility: formConfig.accessibility || {},
      testing: formConfig.testing || {},
      analytics: formConfig.analytics || {},
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    });
  }

  /**
   * Register validation rules
   * @param {string} fieldName - Field name
   * @param {Array} rules - Validation rules
   */
  registerValidationRules(fieldName, rules) {
    this.validationRules.set(fieldName, rules);
  }

  /**
   * Register a component
   * @param {string} componentName - Component name
   * @param {Object} componentConfig - Component configuration
   */
  registerComponent(componentName, componentConfig) {
    this.components.set(componentName, {
      name: componentName,
      description: componentConfig.description || '',
      props: componentConfig.props || [],
      examples: componentConfig.examples || [],
      usage: componentConfig.usage || '',
      accessibility: componentConfig.accessibility || {},
      createdAt: new Date().toISOString()
    });
  }

  /**
   * Generate form documentation
   * @param {string} formId - Form ID
   * @param {string} format - Output format
   * @returns {string} Generated documentation
   */
  generateFormDocumentation(formId, format = 'markdown') {
    const form = this.forms.get(formId);
    if (!form) {
      throw new Error(`Form ${formId} not found`);
    }

    switch (format) {
      case 'markdown':
        return this.generateMarkdownDocumentation(form);
      case 'html':
        return this.generateHTMLDocumentation(form);
      case 'json':
        return this.generateJSONDocumentation(form);
      default:
        throw new Error(`Unsupported format: ${format}`);
    }
  }

  /**
   * Generate markdown documentation
   * @param {Object} form - Form configuration
   * @returns {string} Markdown documentation
   */
  generateMarkdownDocumentation(form) {
    const doc = `# ${form.name}

${form.description}

## Form Information

- **Form ID**: \`${form.id}\`
- **Submit Endpoint**: \`${form.submitEndpoint}\`
- **Methods**: ${form.methods.join(', ')}
- **Authentication**: ${form.authentication}
- **Permissions**: ${form.permissions.join(', ') || 'None'}

## Fields

${form.fields.map(field => this.generateFieldDocumentation(field)).join('\n\n')}

## Validation Rules

${this.generateValidationRulesDocumentation(form.validationRules)}

## Usage Examples

${this.generateUsageExamples(form.examples)}

## Accessibility

${this.generateAccessibilityDocumentation(form.accessibility)}

## Testing

${this.generateTestingDocumentation(form.testing)}

## Analytics

${this.generateAnalyticsDocumentation(form.analytics)}

## API Reference

### Submit Form

\`\`\`javascript
const response = await fetch('${form.submitEndpoint}', {
  method: '${form.methods[0]}',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <token>'
  },
  body: JSON.stringify(formData)
});
\`\`\`

### Response Format

\`\`\`json
{
  "success": true,
  "data": {
    "id": "form_id",
    "status": "submitted"
  },
  "errors": {}
}
\`\`\`

---

*Generated on ${new Date().toLocaleString()}*
`;

    return doc;
  }

  /**
   * Generate HTML documentation
   * @param {Object} form - Form configuration
   * @returns {string} HTML documentation
   */
  generateHTMLDocumentation(form) {
    const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${form.name} - Form Documentation</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1, h2, h3 { color: #333; }
        .form-info { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .field { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .field-name { font-weight: bold; color: #2c3e50; }
        .field-type { color: #7f8c8d; font-size: 0.9em; }
        .validation-rules { background: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .code { background: #f8f9fa; padding: 10px; border-radius: 3px; font-family: 'Courier New', monospace; }
        .example { background: #e8f5e8; padding: 10px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>${form.name}</h1>
        <p>${form.description}</p>
        
        <div class="form-info">
            <h3>Form Information</h3>
            <ul>
                <li><strong>Form ID:</strong> <code>${form.id}</code></li>
                <li><strong>Submit Endpoint:</strong> <code>${form.submitEndpoint}</code></li>
                <li><strong>Methods:</strong> ${form.methods.join(', ')}</li>
                <li><strong>Authentication:</strong> ${form.authentication}</li>
                <li><strong>Permissions:</strong> ${form.permissions.join(', ') || 'None'}</li>
            </ul>
        </div>

        <h2>Fields</h2>
        ${form.fields.map(field => `
            <div class="field">
                <div class="field-name">${field.name}</div>
                <div class="field-type">${field.type} ${field.required ? '(required)' : '(optional)'}</div>
                <p>${field.description || ''}</p>
                ${field.validation ? `<div class="validation-rules">Validation: ${field.validation.join(', ')}</div>` : ''}
            </div>
        `).join('')}

        <h2>Usage Examples</h2>
        ${form.examples.map(example => `
            <div class="example">
                <h4>${example.title}</h4>
                <div class="code">${example.code}</div>
            </div>
        `).join('')}
    </div>
</body>
</html>`;

    return html;
  }

  /**
   * Generate JSON documentation
   * @param {Object} form - Form configuration
   * @returns {string} JSON documentation
   */
  generateJSONDocumentation(form) {
    return JSON.stringify(form, null, 2);
  }

  /**
   * Generate field documentation
   * @param {Object} field - Field configuration
   * @returns {string} Field documentation
   */
  generateFieldDocumentation(field) {
    return `### ${field.name}

- **Type**: \`${field.type}\`
- **Required**: ${field.required ? 'Yes' : 'No'}
- **Description**: ${field.description || 'No description provided'}

${field.validation ? `**Validation Rules**: ${field.validation.join(', ')}` : ''}

${field.example ? `**Example**: \`${field.example}\`` : ''}`;
  }

  /**
   * Generate validation rules documentation
   * @param {Object} validationRules - Validation rules
   * @returns {string} Validation rules documentation
   */
  generateValidationRulesDocumentation(validationRules) {
    if (!validationRules || Object.keys(validationRules).length === 0) {
      return 'No custom validation rules defined.';
    }

    return Object.entries(validationRules).map(([fieldName, rules]) => `
### ${fieldName}

${rules.map(rule => `- **${rule.type}**: ${rule.message}`).join('\n')}
    `).join('\n');
  }

  /**
   * Generate usage examples
   * @param {Array} examples - Usage examples
   * @returns {string} Usage examples documentation
   */
  generateUsageExamples(examples) {
    if (!examples || examples.length === 0) {
      return 'No usage examples provided.';
    }

    return examples.map(example => `
### ${example.title}

\`\`\`javascript
${example.code}
\`\`\`

${example.description || ''}
    `).join('\n');
  }

  /**
   * Generate accessibility documentation
   * @param {Object} accessibility - Accessibility configuration
   * @returns {string} Accessibility documentation
   */
  generateAccessibilityDocumentation(accessibility) {
    if (!accessibility || Object.keys(accessibility).length === 0) {
      return 'No accessibility information provided.';
    }

    return Object.entries(accessibility).map(([key, value]) => `
- **${key}**: ${value}
    `).join('\n');
  }

  /**
   * Generate testing documentation
   * @param {Object} testing - Testing configuration
   * @returns {string} Testing documentation
   */
  generateTestingDocumentation(testing) {
    if (!testing || Object.keys(testing).length === 0) {
      return 'No testing information provided.';
    }

    return Object.entries(testing).map(([key, value]) => `
- **${key}**: ${value}
    `).join('\n');
  }

  /**
   * Generate analytics documentation
   * @param {Object} analytics - Analytics configuration
   * @returns {string} Analytics documentation
   */
  generateAnalyticsDocumentation(analytics) {
    if (!analytics || Object.keys(analytics).length === 0) {
      return 'No analytics information provided.';
    }

    return Object.entries(analytics).map(([key, value]) => `
- **${key}**: ${value}
    `).join('\n');
  }

  /**
   * Generate comprehensive documentation for all forms
   * @param {string} format - Output format
   * @returns {string} Comprehensive documentation
   */
  generateAllDocumentation(format = 'markdown') {
    const forms = Array.from(this.forms.values());
    
    if (format === 'markdown') {
      return `# Form Documentation

This document provides comprehensive documentation for all forms in the application.

## Forms Overview

${forms.map(form => `- [${form.name}](#${form.id})`).join('\n')}

${forms.map(form => this.generateFormDocumentation(form.id, format)).join('\n\n---\n\n')}
      `;
    }
    
    return forms.map(form => this.generateFormDocumentation(form.id, format)).join('\n\n');
  }

  /**
   * Export documentation to file
   * @param {string} formId - Form ID
   * @param {string} format - Output format
   * @param {string} filename - Output filename
   */
  exportDocumentation(formId, format, filename) {
    const documentation = this.generateFormDocumentation(formId, format);
    
    // Create download link
    const blob = new Blob([documentation], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || `${formId}.${format}`;
    link.click();
    URL.revokeObjectURL(url);
  }
}

/**
 * Create documentation generator instance
 */
const formDocumentation = new FormDocumentationGenerator();

/**
 * Register common forms
 */
formDocumentation.registerForm('login-form', {
  name: 'Login Form',
  description: 'User authentication form for logging into the system',
  fields: [
    {
      name: 'email',
      type: 'email',
      required: true,
      description: 'User email address',
      validation: ['required', 'email'],
      example: 'user@example.com'
    },
    {
      name: 'password',
      type: 'password',
      required: true,
      description: 'User password',
      validation: ['required', 'minLength:8'],
      example: 'SecurePassword123'
    },
    {
      name: 'remember',
      type: 'checkbox',
      required: false,
      description: 'Remember user login',
      example: 'true'
    }
  ],
  submitEndpoint: '/api/v1/auth/login/',
  methods: ['POST'],
  authentication: 'none',
  permissions: [],
  examples: [
    {
      title: 'Basic Login',
      code: `const loginData = {
  email: 'user@example.com',
  password: 'SecurePassword123',
  remember: false
};

const response = await fetch('/api/v1/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(loginData)
});`,
      description: 'Basic login form submission example'
    }
  ],
  accessibility: {
    'ARIA Labels': 'All form fields have proper ARIA labels',
    'Keyboard Navigation': 'Full keyboard navigation support',
    'Screen Reader': 'Compatible with screen readers',
    'Focus Management': 'Proper focus management implemented'
  },
  testing: {
    'Unit Tests': 'Comprehensive unit tests for validation',
    'Integration Tests': 'End-to-end form submission tests',
    'Accessibility Tests': 'WCAG 2.1 AA compliance testing',
    'Browser Tests': 'Cross-browser compatibility testing'
  },
  analytics: {
    'Form Start': 'Tracks when user starts filling form',
    'Field Interactions': 'Tracks field focus, blur, and change events',
    'Validation Errors': 'Tracks validation errors and user corrections',
    'Form Completion': 'Tracks successful form submissions'
  }
});

formDocumentation.registerForm('register-form', {
  name: 'Registration Form',
  description: 'User registration form for creating new accounts',
  fields: [
    {
      name: 'firstName',
      type: 'text',
      required: true,
      description: 'User first name',
      validation: ['required', 'pattern:letters'],
      example: 'John'
    },
    {
      name: 'lastName',
      type: 'text',
      required: true,
      description: 'User last name',
      validation: ['required', 'pattern:letters'],
      example: 'Doe'
    },
    {
      name: 'email',
      type: 'email',
      required: true,
      description: 'User email address',
      validation: ['required', 'email'],
      example: 'user@example.com'
    },
    {
      name: 'password',
      type: 'password',
      required: true,
      description: 'User password',
      validation: ['required', 'minLength:8', 'pattern:complex'],
      example: 'SecurePassword123'
    },
    {
      name: 'confirmPassword',
      type: 'password',
      required: true,
      description: 'Password confirmation',
      validation: ['required', 'match:password'],
      example: 'SecurePassword123'
    },
    {
      name: 'company',
      type: 'text',
      required: false,
      description: 'User company name',
      example: 'Acme Corp'
    },
    {
      name: 'phone',
      type: 'tel',
      required: false,
      description: 'User phone number',
      validation: ['pattern:phone'],
      example: '+1234567890'
    },
    {
      name: 'agreeToTerms',
      type: 'checkbox',
      required: true,
      description: 'Agreement to terms and conditions',
      validation: ['required'],
      example: 'true'
    }
  ],
  submitEndpoint: '/api/v1/auth/register/',
  methods: ['POST'],
  authentication: 'none',
  permissions: [],
  examples: [
    {
      title: 'Basic Registration',
      code: `const registrationData = {
  firstName: 'John',
  lastName: 'Doe',
  email: 'john.doe@example.com',
  password: 'SecurePassword123',
  confirmPassword: 'SecurePassword123',
  company: 'Acme Corp',
  phone: '+1234567890',
  agreeToTerms: true
};

const response = await fetch('/api/v1/auth/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(registrationData)
});`,
      description: 'Complete registration form submission example'
    }
  ],
  accessibility: {
    'ARIA Labels': 'All form fields have proper ARIA labels',
    'Keyboard Navigation': 'Full keyboard navigation support',
    'Screen Reader': 'Compatible with screen readers',
    'Focus Management': 'Proper focus management implemented',
    'Error Announcements': 'Screen reader announcements for validation errors'
  },
  testing: {
    'Unit Tests': 'Comprehensive unit tests for all validation rules',
    'Integration Tests': 'End-to-end registration flow tests',
    'Accessibility Tests': 'WCAG 2.1 AA compliance testing',
    'Browser Tests': 'Cross-browser compatibility testing',
    'Performance Tests': 'Form performance and load time testing'
  },
  analytics: {
    'Form Start': 'Tracks when user starts registration',
    'Field Interactions': 'Tracks all field interactions',
    'Validation Errors': 'Tracks validation errors and corrections',
    'Form Completion': 'Tracks successful registrations',
    'Abandonment': 'Tracks form abandonment with reasons'
  }
});

export default formDocumentation;
