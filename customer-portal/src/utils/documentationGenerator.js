/**
 * Documentation Generator Utility
 * Automatically generates documentation for React components
 */

/**
 * Extract component information from source code
 */
export const extractComponentInfo = (sourceCode) => {
  const info = {
    name: '',
    props: {},
    methods: [],
    hooks: [],
    imports: [],
    exports: []
  };

  // Extract component name
  const componentNameMatch = sourceCode.match(/const\s+(\w+)\s*=/);
  if (componentNameMatch) {
    info.name = componentNameMatch[1];
  }

  // Extract PropTypes
  const propTypesMatch = sourceCode.match(/\.propTypes\s*=\s*{([^}]+)}/s);
  if (propTypesMatch) {
    const propTypesCode = propTypesMatch[1];
    const propMatches = propTypesCode.match(/(\w+):\s*PropTypes\.(\w+)/g);
    if (propMatches) {
      propMatches.forEach(match => {
        const [, propName, propType] = match.match(/(\w+):\s*PropTypes\.(\w+)/);
        info.props[propName] = {
          type: propType,
          required: false
        };
      });
    }
  }

  // Extract default props
  const defaultPropsMatch = sourceCode.match(/\.defaultProps\s*=\s*{([^}]+)}/s);
  if (defaultPropsMatch) {
    const defaultPropsCode = defaultPropsMatch[1];
    const defaultMatches = defaultPropsCode.match(/(\w+):\s*([^,}]+)/g);
    if (defaultMatches) {
      defaultMatches.forEach(match => {
        const [, propName, defaultValue] = match.match(/(\w+):\s*([^,}]+)/);
        if (info.props[propName]) {
          info.props[propName].defaultValue = defaultValue.trim();
        }
      });
    }
  }

  // Extract hooks
  const hookMatches = sourceCode.match(/use\w+\(/g);
  if (hookMatches) {
    info.hooks = hookMatches.map(hook => hook.replace('(', ''));
  }

  // Extract imports
  const importMatches = sourceCode.match(/import\s+.*?from\s+['"]([^'"]+)['"]/g);
  if (importMatches) {
    info.imports = importMatches.map(imp => {
      const match = imp.match(/from\s+['"]([^'"]+)['"]/);
      return match ? match[1] : '';
    });
  }

  return info;
};

/**
 * Generate component documentation
 */
export const generateComponentDocumentation = (componentInfo) => {
  const { name, props, methods, hooks, imports } = componentInfo;

  return {
    name,
    description: `The ${name} component is a reusable React component.`,
    props: Object.entries(props).map(([propName, propInfo]) => ({
      name: propName,
      type: propInfo.type,
      required: propInfo.required,
      defaultValue: propInfo.defaultValue,
      description: `The ${propName} prop`
    })),
    methods: methods.map(method => ({
      name: method,
      description: `The ${method} method`
    })),
    hooks: hooks.map(hook => ({
      name: hook,
      description: `Uses the ${hook} hook`
    })),
    imports: imports.map(imp => ({
      path: imp,
      description: `Imported from ${imp}`
    })),
    examples: generateUsageExamples(name, props),
    api: generateAPIReference(name, props, methods)
  };
};

/**
 * Generate usage examples
 */
export const generateUsageExamples = (componentName, props) => {
  const examples = [];

  // Basic usage example
  const basicProps = Object.keys(props).slice(0, 3).map(prop => {
    const propInfo = props[prop];
    if (propInfo.defaultValue) {
      return `${prop}={${propInfo.defaultValue}}`;
    }
    return `${prop}="example"`;
  }).join(' ');

  examples.push({
    title: 'Basic Usage',
    description: `Basic usage of the ${componentName} component`,
    code: `<${componentName} ${basicProps} />`
  });

  // Advanced usage example
  const advancedProps = Object.keys(props).map(prop => {
    const propInfo = props[prop];
    if (propInfo.type === 'function') {
      return `${prop}={handle${prop.charAt(0).toUpperCase() + prop.slice(1)}}`;
    }
    if (propInfo.type === 'boolean') {
      return `${prop}={true}`;
    }
    if (propInfo.type === 'number') {
      return `${prop}={42}`;
    }
    return `${prop}="example"`;
  }).join('\n  ');

  examples.push({
    title: 'Advanced Usage',
    description: `Advanced usage with all props`,
    code: `<${componentName}\n  ${advancedProps}\n/>`
  });

  return examples;
};

/**
 * Generate API reference
 */
export const generateAPIReference = (componentName, props, methods) => {
  return {
    component: {
      name: componentName,
      description: `The ${componentName} component`,
      props: Object.keys(props),
      methods: methods
    },
    events: [
      { name: 'onClick', description: 'Handles click events' },
      { name: 'onChange', description: 'Handles change events' },
      { name: 'onSubmit', description: 'Handles form submission' }
    ],
    cssClasses: [
      { name: `.${componentName.toLowerCase()}`, description: 'Main component class' },
      { name: `.${componentName.toLowerCase()}--modifier`, description: 'Component modifier class' }
    ]
  };
};

/**
 * Generate markdown documentation
 */
export const generateMarkdownDocumentation = (documentation) => {
  const { name, description, props, examples, api } = documentation;

  let markdown = `# ${name}\n\n`;
  markdown += `${description}\n\n`;

  // Props section
  markdown += `## Props\n\n`;
  markdown += `| Name | Type | Required | Default | Description |\n`;
  markdown += `|------|------|----------|---------|-------------|\n`;

  props.forEach(prop => {
    markdown += `| ${prop.name} | ${prop.type} | ${prop.required ? 'Yes' : 'No'} | ${prop.defaultValue || '-'} | ${prop.description} |\n`;
  });

  markdown += `\n`;

  // Examples section
  markdown += `## Examples\n\n`;
  examples.forEach((example, index) => {
    markdown += `### ${example.title}\n\n`;
    markdown += `${example.description}\n\n`;
    markdown += `\`\`\`jsx\n${example.code}\n\`\`\`\n\n`;
  });

  // API section
  markdown += `## API Reference\n\n`;
  markdown += `### Component\n\n`;
  markdown += `- **Name**: ${api.component.name}\n`;
  markdown += `- **Description**: ${api.component.description}\n`;
  markdown += `- **Props**: ${api.component.props.join(', ')}\n`;
  markdown += `- **Methods**: ${api.component.methods.join(', ')}\n\n`;

  return markdown;
};

/**
 * Generate HTML documentation
 */
export const generateHTMLDocumentation = (documentation) => {
  const { name, description, props, examples, api } = documentation;

  let html = `<div class="component-documentation">`;
  html += `<h1>${name}</h1>`;
  html += `<p>${description}</p>`;

  // Props section
  html += `<h2>Props</h2>`;
  html += `<table class="props-table">`;
  html += `<thead><tr><th>Name</th><th>Type</th><th>Required</th><th>Default</th><th>Description</th></tr></thead>`;
  html += `<tbody>`;

  props.forEach(prop => {
    html += `<tr>`;
    html += `<td><code>${prop.name}</code></td>`;
    html += `<td><code>${prop.type}</code></td>`;
    html += `<td>${prop.required ? 'Yes' : 'No'}</td>`;
    html += `<td>${prop.defaultValue || '-'}</td>`;
    html += `<td>${prop.description}</td>`;
    html += `</tr>`;
  });

  html += `</tbody></table>`;

  // Examples section
  html += `<h2>Examples</h2>`;
  examples.forEach((example, index) => {
    html += `<h3>${example.title}</h3>`;
    html += `<p>${example.description}</p>`;
    html += `<pre><code>${example.code}</code></pre>`;
  });

  html += `</div>`;

  return html;
};

/**
 * Auto-generate documentation for all components
 */
export const generateAllComponentDocumentation = (components) => {
  return components.map(component => {
    const info = extractComponentInfo(component.source);
    const documentation = generateComponentDocumentation(info);
    return {
      ...documentation,
      markdown: generateMarkdownDocumentation(documentation),
      html: generateHTMLDocumentation(documentation)
    };
  });
};

export default {
  extractComponentInfo,
  generateComponentDocumentation,
  generateUsageExamples,
  generateAPIReference,
  generateMarkdownDocumentation,
  generateHTMLDocumentation,
  generateAllComponentDocumentation
};
