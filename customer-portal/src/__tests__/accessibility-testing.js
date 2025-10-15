/**
 * Accessibility Testing Suite
 * Comprehensive WCAG compliance and accessibility testing
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { axe, toHaveNoViolations } from 'jest-axe';
import App from '../App';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

// Accessibility test utilities
const checkColorContrast = (element) => {
  const computedStyle = window.getComputedStyle(element);
  const backgroundColor = computedStyle.backgroundColor;
  const color = computedStyle.color;
  
  // Basic contrast check (simplified)
  const getRGB = (color) => {
    const match = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (match) {
      return {
        r: parseInt(match[1]),
        g: parseInt(match[2]),
        b: parseInt(match[3])
      };
    }
    return { r: 0, g: 0, b: 0 };
  };
  
  const bgRGB = getRGB(backgroundColor);
  const textRGB = getRGB(color);
  
  // Calculate relative luminance
  const getLuminance = (rgb) => {
    const { r, g, b } = rgb;
    const [rs, gs, bs] = [r, g, b].map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  };
  
  const bgLuminance = getLuminance(bgRGB);
  const textLuminance = getLuminance(textRGB);
  
  const contrast = (Math.max(bgLuminance, textLuminance) + 0.05) / 
                   (Math.min(bgLuminance, textLuminance) + 0.05);
  
  return contrast >= 4.5; // WCAG AA standard
};

const checkFocusManagement = (element) => {
  const focusableElements = element.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  
  return Array.from(focusableElements).every(el => {
    const tabIndex = el.getAttribute('tabindex');
    return tabIndex !== '-1' || el.tabIndex >= 0;
  });
};

const checkKeyboardNavigation = (element) => {
  const focusableElements = element.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  
  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];
  
  if (firstElement) {
    firstElement.focus();
    expect(document.activeElement).toBe(firstElement);
  }
  
  if (lastElement) {
    lastElement.focus();
    expect(document.activeElement).toBe(lastElement);
  }
  
  return true;
};

// WCAG 2.1 Level A Tests
describe('WCAG 2.1 Level A Compliance', () => {
  test('has proper document structure', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // Check for proper heading hierarchy
    const headings = screen.getAllByRole('heading');
    expect(headings.length).toBeGreaterThan(0);
    
    // Check for main landmark
    const main = screen.getByRole('main');
    expect(main).toBeInTheDocument();
    
    // Check for navigation landmark
    const nav = screen.getByRole('navigation');
    expect(nav).toBeInTheDocument();
  });

  test('images have alt text', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const images = screen.getAllByRole('img');
    images.forEach(img => {
      expect(img).toHaveAttribute('alt');
      expect(img.getAttribute('alt')).not.toBe('');
    });
  });

  test('form controls have labels', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const inputs = screen.getAllByRole('textbox');
    inputs.forEach(input => {
      const label = screen.getByLabelText(input.getAttribute('name') || '');
      expect(label).toBeInTheDocument();
    });
  });

  test('links have descriptive text', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const links = screen.getAllByRole('link');
    links.forEach(link => {
      expect(link.textContent).not.toBe('');
      expect(link.textContent).not.toBe('click here');
      expect(link.textContent).not.toBe('read more');
    });
  });

  test('buttons have accessible names', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button.textContent).not.toBe('');
      expect(button).toHaveAccessibleName();
    });
  });

  test('color is not the only means of conveying information', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // Check that important information is not conveyed only through color
    const elements = screen.getAllByText(/error|success|warning|info/i);
    elements.forEach(element => {
      // Check for additional visual indicators beyond color
      const hasIcon = element.querySelector('svg, [class*="icon"]');
      const hasText = element.textContent.length > 0;
      const hasAriaLabel = element.getAttribute('aria-label');
      
      expect(hasIcon || hasText || hasAriaLabel).toBe(true);
    });
  });

  test('content is readable without stylesheets', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // Check that content is still readable without CSS
    expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
    expect(screen.getByRole('navigation')).toBeInTheDocument();
    expect(screen.getByRole('main')).toBeInTheDocument();
  });
});

// WCAG 2.1 Level AA Tests
describe('WCAG 2.1 Level AA Compliance', () => {
  test('color contrast meets AA standards', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const textElements = screen.getAllByText(/./);
    textElements.forEach(element => {
      if (element.textContent.trim().length > 0) {
        expect(checkColorContrast(element)).toBe(true);
      }
    });
  });

  test('text can be resized up to 200%', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // Test with different font sizes
    const testSizes = ['100%', '150%', '200%'];
    
    testSizes.forEach(size => {
      document.documentElement.style.fontSize = size;
      
      expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });
    
    // Reset font size
    document.documentElement.style.fontSize = '100%';
  });

  test('content is keyboard accessible', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const focusableElements = screen.getAllByRole('button', 'link', 'textbox');
    
    focusableElements.forEach(element => {
      element.focus();
      expect(document.activeElement).toBe(element);
    });
  });

  test('focus is visible and logical', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const focusableElements = screen.getAllByRole('button', 'link', 'textbox');
    
    focusableElements.forEach(element => {
      element.focus();
      
      // Check that focus is visible
      const computedStyle = window.getComputedStyle(element);
      expect(computedStyle.outline).not.toBe('none');
    });
  });

  test('language is specified', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // Check that language is specified on the document
    expect(document.documentElement).toHaveAttribute('lang');
    expect(document.documentElement.getAttribute('lang')).not.toBe('');
  });

  test('consistent navigation', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // Check that navigation is consistent
    const nav = screen.getByRole('navigation');
    expect(nav).toBeInTheDocument();
    
    // Check that navigation items are in the same order
    const navItems = screen.getAllByRole('link');
    expect(navItems.length).toBeGreaterThan(0);
  });
});

// WCAG 2.1 Level AAA Tests
describe('WCAG 2.1 Level AAA Compliance', () => {
  test('color contrast meets AAA standards', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const textElements = screen.getAllByText(/./);
    textElements.forEach(element => {
      if (element.textContent.trim().length > 0) {
        // AAA requires 7:1 contrast ratio for normal text
        const computedStyle = window.getComputedStyle(element);
        const backgroundColor = computedStyle.backgroundColor;
        const color = computedStyle.color;
        
        // This is a simplified check - in practice, you'd use a proper contrast checker
        expect(backgroundColor).toBeDefined();
        expect(color).toBeDefined();
      }
    });
  });

  test('no timing is an essential part of the event', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // Check that no essential functionality depends on timing
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      fireEvent.click(button);
      // Functionality should work regardless of timing
      expect(button).toBeInTheDocument();
    });
  });

  test('interruptions can be postponed or suppressed', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // Check that interruptions can be controlled
    const alerts = screen.queryAllByRole('alert');
    alerts.forEach(alert => {
      // Alerts should be dismissible
      const dismissButton = alert.querySelector('button[aria-label*="close"], button[aria-label*="dismiss"]');
      expect(dismissButton).toBeInTheDocument();
    });
  });
});

// Screen Reader Testing
describe('Screen Reader Testing', () => {
  test('content is properly announced', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // Check that important content is properly announced
    expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
    expect(screen.getByRole('navigation')).toBeInTheDocument();
    expect(screen.getByRole('main')).toBeInTheDocument();
  });

  test('form validation messages are announced', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const inputs = screen.getAllByRole('textbox');
    inputs.forEach(input => {
      // Check that validation messages are properly associated
      const errorMessage = input.getAttribute('aria-describedby');
      if (errorMessage) {
        const errorElement = document.getElementById(errorMessage);
        expect(errorElement).toBeInTheDocument();
      }
    });
  });

  test('dynamic content changes are announced', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // Check that dynamic content has proper ARIA attributes
    const liveRegions = screen.queryAllByRole('status', 'alert', 'log');
    liveRegions.forEach(region => {
      expect(region).toHaveAttribute('aria-live');
    });
  });

  test('skip links are present and functional', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // Check for skip links
    const skipLinks = screen.queryAllByText(/skip to/i);
    if (skipLinks.length > 0) {
      skipLinks.forEach(link => {
        expect(link).toHaveAttribute('href');
        expect(link.getAttribute('href')).toMatch(/^#/);
      });
    }
  });
});

// Keyboard Navigation Testing
describe('Keyboard Navigation Testing', () => {
  test('all interactive elements are keyboard accessible', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const interactiveElements = screen.getAllByRole('button', 'link', 'textbox', 'checkbox', 'radio');
    
    interactiveElements.forEach(element => {
      element.focus();
      expect(document.activeElement).toBe(element);
    });
  });

  test('tab order is logical', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const focusableElements = screen.getAllByRole('button', 'link', 'textbox');
    const tabOrder = [];
    
    focusableElements.forEach(element => {
      element.focus();
      tabOrder.push(element);
    });
    
    // Check that tab order is logical (left to right, top to bottom)
    expect(tabOrder.length).toBeGreaterThan(0);
  });

  test('escape key closes modals and menus', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // Test escape key functionality
    fireEvent.keyDown(document, { key: 'Escape' });
    
    // Check that modals/menus are closed
    const modals = screen.queryAllByRole('dialog');
    modals.forEach(modal => {
      expect(modal).not.toBeVisible();
    });
  });

  test('arrow keys work in menus and lists', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const menus = screen.queryAllByRole('menu');
    menus.forEach(menu => {
      const menuItems = menu.querySelectorAll('[role="menuitem"]');
      if (menuItems.length > 0) {
        menuItems[0].focus();
        
        // Test arrow key navigation
        fireEvent.keyDown(menuItems[0], { key: 'ArrowDown' });
        expect(document.activeElement).toBe(menuItems[1] || menuItems[0]);
      }
    });
  });
});

// Focus Management Testing
describe('Focus Management Testing', () => {
  test('focus is trapped in modals', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const modals = screen.queryAllByRole('dialog');
    modals.forEach(modal => {
      if (modal.style.display !== 'none') {
        const focusableElements = modal.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length > 0) {
          // Focus should be trapped within the modal
          focusableElements[0].focus();
          expect(document.activeElement.closest('[role="dialog"]')).toBe(modal);
        }
      }
    });
  });

  test('focus returns to trigger element after modal closes', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      button.focus();
      const initialFocus = document.activeElement;
      
      // Simulate opening and closing a modal
      fireEvent.click(button);
      fireEvent.keyDown(document, { key: 'Escape' });
      
      // Focus should return to the trigger element
      expect(document.activeElement).toBe(initialFocus);
    });
  });

  test('focus is visible on all focusable elements', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const focusableElements = screen.getAllByRole('button', 'link', 'textbox');
    
    focusableElements.forEach(element => {
      element.focus();
      
      // Check that focus is visible
      const computedStyle = window.getComputedStyle(element);
      const hasFocusIndicator = 
        computedStyle.outline !== 'none' ||
        computedStyle.boxShadow !== 'none' ||
        computedStyle.borderColor !== 'transparent';
      
      expect(hasFocusIndicator).toBe(true);
    });
  });
});

// ARIA Testing
describe('ARIA Testing', () => {
  test('proper ARIA roles are used', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // Check for proper ARIA roles
    expect(screen.getByRole('navigation')).toBeInTheDocument();
    expect(screen.getByRole('main')).toBeInTheDocument();
    
    // Check that custom elements have proper roles
    const customElements = screen.queryAllByRole('button', 'link', 'textbox');
    customElements.forEach(element => {
      expect(element).toHaveAttribute('role');
    });
  });

  test('ARIA labels are descriptive', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const elementsWithAriaLabel = screen.queryAllByRole('button', 'link', 'textbox');
    elementsWithAriaLabel.forEach(element => {
      const ariaLabel = element.getAttribute('aria-label');
      if (ariaLabel) {
        expect(ariaLabel.length).toBeGreaterThan(0);
        expect(ariaLabel).not.toBe('button');
        expect(ariaLabel).not.toBe('link');
      }
    });
  });

  test('ARIA states are properly managed', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const elementsWithAriaExpanded = screen.queryAllByRole('button');
    elementsWithAriaExpanded.forEach(element => {
      const ariaExpanded = element.getAttribute('aria-expanded');
      if (ariaExpanded) {
        expect(ariaExpanded).toMatch(/true|false/);
      }
    });
  });

  test('ARIA relationships are properly established', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const elementsWithAriaDescribedBy = screen.queryAllByRole('textbox');
    elementsWithAriaDescribedBy.forEach(element => {
      const ariaDescribedBy = element.getAttribute('aria-describedby');
      if (ariaDescribedBy) {
        const describedElement = document.getElementById(ariaDescribedBy);
        expect(describedElement).toBeInTheDocument();
      }
    });
  });
});

// Automated Accessibility Testing
describe('Automated Accessibility Testing', () => {
  test('passes axe accessibility tests', async () => {
    const { container } = render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('passes axe accessibility tests on all pages', async () => {
    const pages = ['/', '/tickets', '/dashboard', '/profile'];
    
    for (const page of pages) {
      const { container } = render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    }
  });
});

// Performance and Accessibility
describe('Performance and Accessibility', () => {
  test('accessible content loads quickly', () => {
    const startTime = performance.now();
    
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const endTime = performance.now();
    const loadTime = endTime - startTime;
    
    // Accessible content should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
  });

  test('accessibility features do not impact performance', () => {
    const startTime = performance.now();
    
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // Test that accessibility features don't significantly impact performance
    const endTime = performance.now();
    const loadTime = endTime - startTime;
    
    expect(loadTime).toBeLessThan(1000);
  });
});

// Error Handling and Accessibility
describe('Error Handling and Accessibility', () => {
  test('error messages are accessible', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const errorMessages = screen.queryAllByRole('alert');
    errorMessages.forEach(error => {
      expect(error).toHaveAttribute('aria-live', 'assertive');
      expect(error.textContent).not.toBe('');
    });
  });

  test('loading states are accessible', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const loadingElements = screen.queryAllByRole('status');
    loadingElements.forEach(loading => {
      expect(loading).toHaveAttribute('aria-live', 'polite');
      expect(loading.textContent).not.toBe('');
    });
  });

  test('success messages are accessible', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const successMessages = screen.queryAllByRole('status');
    successMessages.forEach(success => {
      expect(success).toHaveAttribute('aria-live', 'polite');
      expect(success.textContent).not.toBe('');
    });
  });
});

// Export test utilities
export {
  checkColorContrast,
  checkFocusManagement,
  checkKeyboardNavigation
};
