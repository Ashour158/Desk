/**
 * Design System for Customer Portal
 * Comprehensive component library with consistent design tokens
 */

/**
 * Design tokens
 */
export const designTokens = {
  // Colors
  colors: {
    primary: {
      50: '#f0f9ff',
      100: '#e0f2fe',
      200: '#bae6fd',
      300: '#7dd3fc',
      400: '#38bdf8',
      500: '#0ea5e9',
      600: '#0284c7',
      700: '#0369a1',
      800: '#075985',
      900: '#0c4a6e'
    },
    secondary: {
      50: '#f8fafc',
      100: '#f1f5f9',
      200: '#e2e8f0',
      300: '#cbd5e1',
      400: '#94a3b8',
      500: '#64748b',
      600: '#475569',
      700: '#334155',
      800: '#1e293b',
      900: '#0f172a'
    },
    success: {
      50: '#f0fdf4',
      100: '#dcfce7',
      200: '#bbf7d0',
      300: '#86efac',
      400: '#4ade80',
      500: '#22c55e',
      600: '#16a34a',
      700: '#15803d',
      800: '#166534',
      900: '#14532d'
    },
    warning: {
      50: '#fffbeb',
      100: '#fef3c7',
      200: '#fde68a',
      300: '#fcd34d',
      400: '#fbbf24',
      500: '#f59e0b',
      600: '#d97706',
      700: '#b45309',
      800: '#92400e',
      900: '#78350f'
    },
    error: {
      50: '#fef2f2',
      100: '#fee2e2',
      200: '#fecaca',
      300: '#fca5a5',
      400: '#f87171',
      500: '#ef4444',
      600: '#dc2626',
      700: '#b91c1c',
      800: '#991b1b',
      900: '#7f1d1d'
    }
  },

  // Typography
  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'monospace']
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
      '5xl': '3rem'
    },
    fontWeight: {
      light: '300',
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
      extrabold: '800'
    },
    lineHeight: {
      tight: '1.25',
      snug: '1.375',
      normal: '1.5',
      relaxed: '1.625',
      loose: '2'
    }
  },

  // Spacing
  spacing: {
    0: '0',
    1: '0.25rem',
    2: '0.5rem',
    3: '0.75rem',
    4: '1rem',
    5: '1.25rem',
    6: '1.5rem',
    8: '2rem',
    10: '2.5rem',
    12: '3rem',
    16: '4rem',
    20: '5rem',
    24: '6rem',
    32: '8rem'
  },

  // Border radius
  borderRadius: {
    none: '0',
    sm: '0.125rem',
    base: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    '2xl': '1rem',
    '3xl': '1.5rem',
    full: '9999px'
  },

  // Shadows
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
  },

  // Breakpoints
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px'
  },

  // Z-index
  zIndex: {
    hide: -1,
    auto: 'auto',
    base: 0,
    docked: 10,
    dropdown: 1000,
    sticky: 1100,
    banner: 1200,
    overlay: 1300,
    modal: 1400,
    popover: 1500,
    skipLink: 1600,
    toast: 1700,
    tooltip: 1800
  }
};

/**
 * Component variants
 */
export const componentVariants = {
  // Button variants
  button: {
    base: {
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: '0.375rem',
      fontWeight: '500',
      transition: 'all 0.2s ease-in-out',
      cursor: 'pointer',
      border: 'none',
      outline: 'none'
    },
    sizes: {
      sm: {
        padding: '0.5rem 0.75rem',
        fontSize: '0.875rem',
        lineHeight: '1.25rem'
      },
      md: {
        padding: '0.625rem 1rem',
        fontSize: '1rem',
        lineHeight: '1.5rem'
      },
      lg: {
        padding: '0.75rem 1.5rem',
        fontSize: '1.125rem',
        lineHeight: '1.75rem'
      }
    },
    variants: {
      primary: {
        backgroundColor: designTokens.colors.primary[500],
        color: 'white',
        '&:hover': {
          backgroundColor: designTokens.colors.primary[600]
        },
        '&:active': {
          backgroundColor: designTokens.colors.primary[700]
        }
      },
      secondary: {
        backgroundColor: designTokens.colors.secondary[100],
        color: designTokens.colors.secondary[900],
        '&:hover': {
          backgroundColor: designTokens.colors.secondary[200]
        },
        '&:active': {
          backgroundColor: designTokens.colors.secondary[300]
        }
      },
      outline: {
        backgroundColor: 'transparent',
        color: designTokens.colors.primary[500],
        border: `1px solid ${designTokens.colors.primary[500]}`,
        '&:hover': {
          backgroundColor: designTokens.colors.primary[50]
        },
        '&:active': {
          backgroundColor: designTokens.colors.primary[100]
        }
      }
    }
  },

  // Input variants
  input: {
    base: {
      display: 'block',
      width: '100%',
      padding: '0.625rem 0.75rem',
      fontSize: '1rem',
      lineHeight: '1.5rem',
      color: designTokens.colors.secondary[900],
      backgroundColor: 'white',
      border: `1px solid ${designTokens.colors.secondary[300]}`,
      borderRadius: '0.375rem',
      transition: 'border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
      '&:focus': {
        outline: 'none',
        borderColor: designTokens.colors.primary[500],
        boxShadow: `0 0 0 3px ${designTokens.colors.primary[100]}`
      },
      '&:disabled': {
        backgroundColor: designTokens.colors.secondary[100],
        color: designTokens.colors.secondary[500],
        cursor: 'not-allowed'
      }
    },
    sizes: {
      sm: {
        padding: '0.5rem 0.625rem',
        fontSize: '0.875rem'
      },
      md: {
        padding: '0.625rem 0.75rem',
        fontSize: '1rem'
      },
      lg: {
        padding: '0.75rem 1rem',
        fontSize: '1.125rem'
      }
    },
    variants: {
      default: {},
      error: {
        borderColor: designTokens.colors.error[500],
        '&:focus': {
          borderColor: designTokens.colors.error[500],
          boxShadow: `0 0 0 3px ${designTokens.colors.error[100]}`
        }
      },
      success: {
        borderColor: designTokens.colors.success[500],
        '&:focus': {
          borderColor: designTokens.colors.success[500],
          boxShadow: `0 0 0 3px ${designTokens.colors.success[100]}`
        }
      }
    }
  },

  // Card variants
  card: {
    base: {
      backgroundColor: 'white',
      borderRadius: '0.5rem',
      boxShadow: designTokens.shadows.base,
      overflow: 'hidden'
    },
    variants: {
      default: {},
      elevated: {
        boxShadow: designTokens.shadows.lg
      },
      outlined: {
        boxShadow: 'none',
        border: `1px solid ${designTokens.colors.secondary[200]}`
      }
    }
  }
};

/**
 * Design system utilities
 */
export const designSystemUtils = {
  /**
   * Get color value
   */
  getColor: (colorPath) => {
    const [color, shade] = colorPath.split('.');
    return designTokens.colors[color]?.[shade] || colorPath;
  },

  /**
   * Get spacing value
   */
  getSpacing: (size) => {
    return designTokens.spacing[size] || size;
  },

  /**
   * Get typography value
   */
  getTypography: (property, value) => {
    return designTokens.typography[property]?.[value] || value;
  },

  /**
   * Generate responsive styles
   */
  responsive: (styles) => {
    return Object.entries(styles).map(([breakpoint, style]) => {
      if (breakpoint === 'base') {
        return style;
      }
      return `@media (min-width: ${designTokens.breakpoints[breakpoint]}) { ${style} }`;
    }).join(' ');
  },

  /**
   * Generate component styles
   */
  generateStyles: (component, variant, size) => {
    const baseStyles = componentVariants[component]?.base || {};
    const variantStyles = componentVariants[component]?.variants?.[variant] || {};
    const sizeStyles = componentVariants[component]?.sizes?.[size] || {};
    
    return {
      ...baseStyles,
      ...sizeStyles,
      ...variantStyles
    };
  }
};

/**
 * Design system provider
 */
export class DesignSystemProvider {
  constructor() {
    this.theme = 'light';
    this.customTokens = {};
  }

  /**
   * Set theme
   */
  setTheme(theme) {
    this.theme = theme;
    this.updateCSSVariables();
  }

  /**
   * Set custom tokens
   */
  setCustomTokens(tokens) {
    this.customTokens = { ...this.customTokens, ...tokens };
    this.updateCSSVariables();
  }

  /**
   * Update CSS variables
   */
  updateCSSVariables() {
    const root = document.documentElement;
    
    // Update color variables
    Object.entries(designTokens.colors).forEach(([colorName, colorShades]) => {
      Object.entries(colorShades).forEach(([shade, value]) => {
        root.style.setProperty(`--color-${colorName}-${shade}`, value);
      });
    });

    // Update spacing variables
    Object.entries(designTokens.spacing).forEach(([size, value]) => {
      root.style.setProperty(`--spacing-${size}`, value);
    });

    // Update typography variables
    Object.entries(designTokens.typography.fontSize).forEach(([size, value]) => {
      root.style.setProperty(`--font-size-${size}`, value);
    });

    // Update custom tokens
    Object.entries(this.customTokens).forEach(([key, value]) => {
      root.style.setProperty(`--${key}`, value);
    });
  }

  /**
   * Get current theme
   */
  getTheme() {
    return this.theme;
  }

  /**
   * Get design token
   */
  getToken(path) {
    const keys = path.split('.');
    let value = designTokens;
    
    for (const key of keys) {
      value = value?.[key];
      if (value === undefined) break;
    }
    
    return value;
  }
}

// Create global design system provider
export const designSystem = new DesignSystemProvider();

export default {
  designTokens,
  componentVariants,
  designSystemUtils,
  DesignSystemProvider,
  designSystem
};
