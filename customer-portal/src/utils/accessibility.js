/**
 * Accessibility utilities for color contrast validation, focus management, and screen reader support
 */

/**
 * Calculate relative luminance of a color
 * @param {number} r - Red component (0-255)
 * @param {number} g - Green component (0-255)
 * @param {number} b - Blue component (0-255)
 * @returns {number} Relative luminance
 */
export const getRelativeLuminance = (r, g, b) => {
  const [rs, gs, bs] = [r, g, b].map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
};

/**
 * Calculate contrast ratio between two colors
 * @param {string} color1 - First color (hex, rgb, or hsl)
 * @param {string} color2 - Second color (hex, rgb, or hsl)
 * @returns {number} Contrast ratio
 */
export const getContrastRatio = (color1, color2) => {
  const rgb1 = parseColor(color1);
  const rgb2 = parseColor(color2);
  
  const lum1 = getRelativeLuminance(rgb1.r, rgb1.g, rgb1.b);
  const lum2 = getRelativeLuminance(rgb2.r, rgb2.g, rgb2.b);
  
  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);
  
  return (lighter + 0.05) / (darker + 0.05);
};

/**
 * Parse color string to RGB values
 * @param {string} color - Color string
 * @returns {Object} RGB values
 */
export const parseColor = (color) => {
  // Remove whitespace and convert to lowercase
  color = color.trim().toLowerCase();
  
  // Handle hex colors
  if (color.startsWith('#')) {
    const hex = color.slice(1);
    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return { r, g, b };
  }
  
  // Handle rgb() colors
  if (color.startsWith('rgb(')) {
    const values = color.slice(4, -1).split(',').map(v => parseInt(v.trim()));
    return { r: values[0], g: values[1], b: values[2] };
  }
  
  // Handle named colors (basic set)
  const namedColors = {
    black: { r: 0, g: 0, b: 0 },
    white: { r: 255, g: 255, b: 255 },
    red: { r: 255, g: 0, b: 0 },
    green: { r: 0, g: 128, b: 0 },
    blue: { r: 0, g: 0, b: 255 },
    yellow: { r: 255, g: 255, b: 0 },
    cyan: { r: 0, g: 255, b: 255 },
    magenta: { r: 255, g: 0, b: 255 },
    gray: { r: 128, g: 128, b: 128 },
    grey: { r: 128, g: 128, b: 128 }
  };
  
  if (namedColors[color]) {
    return namedColors[color];
  }
  
  // Default to black if color cannot be parsed
  return { r: 0, g: 0, b: 0 };
};

/**
 * Check if contrast ratio meets WCAG standards
 * @param {string} foreground - Foreground color
 * @param {string} background - Background color
 * @param {string} level - WCAG level ('AA' or 'AAA')
 * @param {string} size - Text size ('normal' or 'large')
 * @returns {Object} Validation result
 */
export const validateContrast = (foreground, background, level = 'AA', size = 'normal') => {
  const ratio = getContrastRatio(foreground, background);
  
  const requirements = {
    AA: { normal: 4.5, large: 3 },
    AAA: { normal: 7, large: 4.5 }
  };
  
  const requiredRatio = requirements[level][size];
  const passes = ratio >= requiredRatio;
  
  return {
    ratio: Math.round(ratio * 100) / 100,
    required: requiredRatio,
    passes,
    level,
    size,
    rating: ratio >= 7 ? 'AAA' : ratio >= 4.5 ? 'AA' : 'Fail'
  };
};

/**
 * Focus management utilities
 */
export const focusManager = {
  /**
   * Trap focus within an element
   * @param {HTMLElement} element - Element to trap focus in
   */
  trapFocus: (element) => {
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    const handleTabKey = (e) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    };
    
    element.addEventListener('keydown', handleTabKey);
    
    // Return cleanup function
    return () => element.removeEventListener('keydown', handleTabKey);
  },
  
  /**
   * Restore focus to a previously focused element
   * @param {HTMLElement} element - Element to restore focus to
   */
  restoreFocus: (element) => {
    if (element && typeof element.focus === 'function') {
      element.focus();
    }
  },
  
  /**
   * Get the currently focused element
   * @returns {HTMLElement|null} Currently focused element
   */
  getCurrentFocus: () => document.activeElement,
  
  /**
   * Check if an element is focusable
   * @param {HTMLElement} element - Element to check
   * @returns {boolean} Whether element is focusable
   */
  isFocusable: (element) => {
    if (!element) return false;
    
    const tagName = element.tagName.toLowerCase();
    const tabIndex = element.getAttribute('tabindex');
    
    // Elements that are naturally focusable
    const naturallyFocusable = ['button', 'input', 'select', 'textarea', 'a', 'area'];
    
    if (naturallyFocusable.includes(tagName)) {
      return !element.disabled;
    }
    
    // Elements with tabindex
    if (tabIndex !== null) {
      return parseInt(tabIndex) >= 0;
    }
    
    return false;
  }
};

/**
 * Screen reader utilities
 */
export const screenReader = {
  /**
   * Announce a message to screen readers
   * @param {string} message - Message to announce
   * @param {string} priority - Priority level ('polite' or 'assertive')
   */
  announce: (message, priority = 'polite') => {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', priority);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    // Remove after announcement
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  },
  
  /**
   * Create a live region for dynamic content
   * @param {string} id - Unique ID for the region
   * @param {string} priority - Priority level
   * @returns {HTMLElement} Live region element
   */
  createLiveRegion: (id, priority = 'polite') => {
    const region = document.createElement('div');
    region.id = id;
    region.setAttribute('aria-live', priority);
    region.setAttribute('aria-atomic', 'true');
    region.className = 'sr-only';
    return region;
  },
  
  /**
   * Update live region content
   * @param {string} id - Live region ID
   * @param {string} content - New content
   */
  updateLiveRegion: (id, content) => {
    const region = document.getElementById(id);
    if (region) {
      region.textContent = content;
    }
  }
};

/**
 * Keyboard navigation utilities
 */
export const keyboardNavigation = {
  /**
   * Handle arrow key navigation for lists
   * @param {Event} e - Keyboard event
   * @param {HTMLElement[]} items - List of focusable items
   * @param {string} orientation - 'horizontal' or 'vertical'
   */
  handleArrowKeys: (e, items, orientation = 'vertical') => {
    const currentIndex = items.indexOf(document.activeElement);
    if (currentIndex === -1) return;
    
    let nextIndex = currentIndex;
    
    if (orientation === 'vertical') {
      if (e.key === 'ArrowDown') {
        nextIndex = (currentIndex + 1) % items.length;
      } else if (e.key === 'ArrowUp') {
        nextIndex = currentIndex === 0 ? items.length - 1 : currentIndex - 1;
      }
    } else {
      if (e.key === 'ArrowRight') {
        nextIndex = (currentIndex + 1) % items.length;
      } else if (e.key === 'ArrowLeft') {
        nextIndex = currentIndex === 0 ? items.length - 1 : currentIndex - 1;
      }
    }
    
    if (nextIndex !== currentIndex) {
      e.preventDefault();
      items[nextIndex].focus();
    }
  },
  
  /**
   * Handle escape key to close modals/dropdowns
   * @param {Event} e - Keyboard event
   * @param {Function} onClose - Close handler
   */
  handleEscape: (e, onClose) => {
    if (e.key === 'Escape') {
      e.preventDefault();
      onClose();
    }
  },
  
  /**
   * Handle enter and space keys for buttons/links
   * @param {Event} e - Keyboard event
   * @param {Function} onClick - Click handler
   */
  handleActivation: (e, onClick) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClick();
    }
  }
};

/**
 * ARIA utilities
 */
export const ariaUtils = {
  /**
   * Generate unique ID for ARIA attributes
   * @param {string} prefix - ID prefix
   * @returns {string} Unique ID
   */
  generateId: (prefix = 'aria') => {
    return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
  },
  
  /**
   * Set ARIA attributes on an element
   * @param {HTMLElement} element - Target element
   * @param {Object} attributes - ARIA attributes to set
   */
  setAttributes: (element, attributes) => {
    Object.entries(attributes).forEach(([key, value]) => {
      element.setAttribute(key, value);
    });
  },
  
  /**
   * Create accessible button
   * @param {Object} options - Button options
   * @returns {HTMLElement} Accessible button
   */
  createButton: (options = {}) => {
    const button = document.createElement('button');
    button.textContent = options.text || '';
    button.setAttribute('type', options.type || 'button');
    
    if (options.ariaLabel) {
      button.setAttribute('aria-label', options.ariaLabel);
    }
    
    if (options.ariaDescribedBy) {
      button.setAttribute('aria-describedby', options.ariaDescribedBy);
    }
    
    if (options.onClick) {
      button.addEventListener('click', options.onClick);
    }
    
    return button;
  }
};

export default {
  getContrastRatio,
  validateContrast,
  focusManager,
  screenReader,
  keyboardNavigation,
  ariaUtils
};
