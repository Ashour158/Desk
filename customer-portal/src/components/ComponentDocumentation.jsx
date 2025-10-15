import React, { useState, useMemo, memo } from 'react';
import PropTypes from 'prop-types';

/**
 * Component Documentation Generator
 * Automatically generates documentation for React components
 */
const ComponentDocumentation = memo(({ 
  componentName,
  componentPath,
  props = {},
  examples = [],
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState('overview');
  
  // Generate prop documentation
  const propDocumentation = useMemo(() => {
    return Object.entries(props).map(([propName, propInfo]) => ({
      name: propName,
      type: propInfo.type || 'any',
      required: propInfo.required || false,
      defaultValue: propInfo.defaultValue,
      description: propInfo.description || 'No description available'
    }));
  }, [props]);

  // Generate usage examples
  const usageExamples = useMemo(() => {
    return examples.map((example, index) => ({
      id: index,
      title: example.title || `Example ${index + 1}`,
      code: example.code,
      description: example.description
    }));
  }, [examples]);

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'props', label: 'Props' },
    { id: 'examples', label: 'Examples' },
    { id: 'api', label: 'API' }
  ];

  return (
    <div className={`component-documentation ${className}`}>
      <div className="doc-header">
        <h2>{componentName}</h2>
        <span className="component-path">{componentPath}</span>
      </div>

      <div className="doc-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="doc-content">
        {activeTab === 'overview' && (
          <div className="overview-section">
            <h3>Overview</h3>
            <p>
              The <code>{componentName}</code> component is a reusable React component
              that provides specific functionality for the application.
            </p>
            
            <h4>Features</h4>
            <ul>
              <li>Optimized with React.memo for performance</li>
              <li>Comprehensive prop validation with PropTypes</li>
              <li>Accessible design with ARIA attributes</li>
              <li>Responsive design for all screen sizes</li>
              <li>TypeScript support (when applicable)</li>
            </ul>

            <h4>Installation</h4>
            <pre className="code-block">
              <code>{`import { ${componentName} } from '${componentPath}';`}</code>
            </pre>
          </div>
        )}

        {activeTab === 'props' && (
          <div className="props-section">
            <h3>Props</h3>
            <div className="props-table">
              <div className="props-header">
                <div className="prop-name">Name</div>
                <div className="prop-type">Type</div>
                <div className="prop-required">Required</div>
                <div className="prop-default">Default</div>
                <div className="prop-description">Description</div>
              </div>
              {propDocumentation.map(prop => (
                <div key={prop.name} className="prop-row">
                  <div className="prop-name">
                    <code>{prop.name}</code>
                  </div>
                  <div className="prop-type">
                    <code>{prop.type}</code>
                  </div>
                  <div className="prop-required">
                    {prop.required ? (
                      <span className="required">Yes</span>
                    ) : (
                      <span className="optional">No</span>
                    )}
                  </div>
                  <div className="prop-default">
                    {prop.defaultValue ? (
                      <code>{prop.defaultValue}</code>
                    ) : (
                      <span className="no-default">-</span>
                    )}
                  </div>
                  <div className="prop-description">
                    {prop.description}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'examples' && (
          <div className="examples-section">
            <h3>Usage Examples</h3>
            {usageExamples.map(example => (
              <div key={example.id} className="example">
                <h4>{example.title}</h4>
                {example.description && (
                  <p>{example.description}</p>
                )}
                <pre className="code-block">
                  <code>{example.code}</code>
                </pre>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'api' && (
          <div className="api-section">
            <h3>API Reference</h3>
            
            <h4>Component Methods</h4>
            <div className="method-list">
              <div className="method">
                <code>render()</code>
                <p>Renders the component to the DOM</p>
              </div>
              <div className="method">
                <code>componentDidMount()</code>
                <p>Called after component is mounted</p>
              </div>
              <div className="method">
                <code>componentWillUnmount()</code>
                <p>Called before component is unmounted</p>
              </div>
            </div>

            <h4>Event Handlers</h4>
            <div className="event-list">
              <div className="event">
                <code>onClick</code>
                <p>Handles click events</p>
              </div>
              <div className="event">
                <code>onChange</code>
                <p>Handles change events</p>
              </div>
              <div className="event">
                <code>onSubmit</code>
                <p>Handles form submission</p>
              </div>
            </div>

            <h4>CSS Classes</h4>
            <div className="css-classes">
              <div className="css-class">
                <code>.component-name</code>
                <p>Main component class</p>
              </div>
              <div className="css-class">
                <code>.component-name--modifier</code>
                <p>Component modifier class</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

ComponentDocumentation.propTypes = {
  componentName: PropTypes.string.isRequired,
  componentPath: PropTypes.string.isRequired,
  props: PropTypes.object,
  examples: PropTypes.arrayOf(PropTypes.shape({
    title: PropTypes.string,
    code: PropTypes.string.isRequired,
    description: PropTypes.string
  })),
  className: PropTypes.string
};

ComponentDocumentation.displayName = 'ComponentDocumentation';

export default ComponentDocumentation;
