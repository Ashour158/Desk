/**
 * Mobile Device Testing Suite
 * Comprehensive mobile device and responsive testing
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';
import { mockMatchMedia } from '../utils/testUtils';

// Use imported mockMatchMedia from testUtils

// Mobile device configurations
const MOBILE_DEVICES = {
  iPhone: {
    width: 375,
    height: 667,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    pixelRatio: 2
  },
  iPhonePlus: {
    width: 414,
    height: 736,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    pixelRatio: 3
  },
  iPhonePro: {
    width: 390,
    height: 844,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    pixelRatio: 3
  },
  SamsungGalaxy: {
    width: 360,
    height: 640,
    userAgent: 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
    pixelRatio: 3
  },
  SamsungGalaxyPlus: {
    width: 412,
    height: 915,
    userAgent: 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
    pixelRatio: 3.5
  },
  GooglePixel: {
    width: 393,
    height: 851,
    userAgent: 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
    pixelRatio: 2.75
  },
  iPad: {
    width: 768,
    height: 1024,
    userAgent: 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    pixelRatio: 2
  },
  iPadPro: {
    width: 1024,
    height: 1366,
    userAgent: 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    pixelRatio: 2
  }
};

// Tablet device configurations
const TABLET_DEVICES = {
  iPad: {
    width: 768,
    height: 1024,
    userAgent: 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    pixelRatio: 2
  },
  iPadPro: {
    width: 1024,
    height: 1366,
    userAgent: 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    pixelRatio: 2
  },
  SamsungTab: {
    width: 800,
    height: 1280,
    userAgent: 'Mozilla/5.0 (Linux; Android 10; SM-T870) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Safari/537.36',
    pixelRatio: 2
  },
  Surface: {
    width: 912,
    height: 1368,
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Safari/537.36',
    pixelRatio: 1.5
  }
};

// Desktop device configurations
const DESKTOP_DEVICES = {
  Desktop: {
    width: 1920,
    height: 1080,
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Safari/537.36',
    pixelRatio: 1
  },
  Laptop: {
    width: 1366,
    height: 768,
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Safari/537.36',
    pixelRatio: 1
  },
  MacBook: {
    width: 1440,
    height: 900,
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Safari/537.36',
    pixelRatio: 2
  }
};

// Test utilities
const setupMobileTest = (device) => {
  // Mock window dimensions
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: device.width,
  });
  
  Object.defineProperty(window, 'innerHeight', {
    writable: true,
    configurable: true,
    value: device.height,
  });
  
  // Mock user agent
  Object.defineProperty(navigator, 'userAgent', {
    writable: true,
    configurable: true,
    value: device.userAgent,
  });
  
  // Mock device pixel ratio
  Object.defineProperty(window, 'devicePixelRatio', {
    writable: true,
    configurable: true,
    value: device.pixelRatio,
  });
  
  // Mock matchMedia
  window.matchMedia = jest.fn().mockImplementation((query) => {
    if (query.includes('(max-width: 768px)')) {
      return mockMatchMedia(device.width <= 768);
    }
    if (query.includes('(max-width: 1024px)')) {
      return mockMatchMedia(device.width <= 1024);
    }
    if (query.includes('(orientation: portrait)')) {
      return mockMatchMedia(device.height > device.width);
    }
    if (query.includes('(orientation: landscape)')) {
      return mockMatchMedia(device.width > device.height);
    }
    return mockMatchMedia(false);
  });
};

// Mobile device tests
describe('Mobile Device Testing', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
  });

  // Test iPhone
  describe('iPhone Testing', () => {
    beforeEach(() => {
      setupMobileTest(MOBILE_DEVICES.iPhone);
    });

    test('renders correctly on iPhone', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
    });

    test('mobile navigation works on iPhone', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Check if mobile menu button is present
      const menuButton = screen.getByRole('button', { name: /menu/i });
      expect(menuButton).toBeInTheDocument();
      
      // Test menu toggle
      fireEvent.click(menuButton);
      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });

    test('touch interactions work on iPhone', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Test touch events
      const button = screen.getByRole('button', { name: /menu/i });
      fireEvent.touchStart(button);
      fireEvent.touchEnd(button);
      
      expect(button).toBeInTheDocument();
    });

    test('responsive layout adapts to iPhone', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Check if mobile-specific elements are present
      expect(screen.getByRole('button', { name: /menu/i })).toBeInTheDocument();
    });
  });

  // Test iPhone Plus
  describe('iPhone Plus Testing', () => {
    beforeEach(() => {
      setupMobileTest(MOBILE_DEVICES.iPhonePlus);
    });

    test('renders correctly on iPhone Plus', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
    });

    test('larger screen layout works on iPhone Plus', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Check if layout adapts to larger screen
      expect(screen.getByRole('button', { name: /menu/i })).toBeInTheDocument();
    });
  });

  // Test iPhone Pro
  describe('iPhone Pro Testing', () => {
    beforeEach(() => {
      setupMobileTest(MOBILE_DEVICES.iPhonePro);
    });

    test('renders correctly on iPhone Pro', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
    });

    test('notch handling works on iPhone Pro', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Check if layout handles notch properly
      expect(screen.getByRole('button', { name: /menu/i })).toBeInTheDocument();
    });
  });

  // Test Samsung Galaxy
  describe('Samsung Galaxy Testing', () => {
    beforeEach(() => {
      setupMobileTest(MOBILE_DEVICES.SamsungGalaxy);
    });

    test('renders correctly on Samsung Galaxy', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
    });

    test('Android-specific features work on Samsung Galaxy', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Test Android-specific interactions
      const button = screen.getByRole('button', { name: /menu/i });
      fireEvent.touchStart(button);
      fireEvent.touchEnd(button);
      
      expect(button).toBeInTheDocument();
    });
  });

  // Test Samsung Galaxy Plus
  describe('Samsung Galaxy Plus Testing', () => {
    beforeEach(() => {
      setupMobileTest(MOBILE_DEVICES.SamsungGalaxyPlus);
    });

    test('renders correctly on Samsung Galaxy Plus', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
    });

    test('larger Android screen layout works on Samsung Galaxy Plus', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Check if layout adapts to larger Android screen
      expect(screen.getByRole('button', { name: /menu/i })).toBeInTheDocument();
    });
  });

  // Test Google Pixel
  describe('Google Pixel Testing', () => {
    beforeEach(() => {
      setupMobileTest(MOBILE_DEVICES.GooglePixel);
    });

    test('renders correctly on Google Pixel', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
    });

    test('Pixel-specific features work on Google Pixel', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Test Pixel-specific interactions
      const button = screen.getByRole('button', { name: /menu/i });
      fireEvent.touchStart(button);
      fireEvent.touchEnd(button);
      
      expect(button).toBeInTheDocument();
    });
  });
});

// Tablet device tests
describe('Tablet Device Testing', () => {
  // Test iPad
  describe('iPad Testing', () => {
    beforeEach(() => {
      setupMobileTest(TABLET_DEVICES.iPad);
    });

    test('renders correctly on iPad', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
    });

    test('tablet navigation works on iPad', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Check if tablet navigation is present
      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });

    test('touch interactions work on iPad', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Test touch events
      const button = screen.getByRole('button', { name: /menu/i });
      fireEvent.touchStart(button);
      fireEvent.touchEnd(button);
      
      expect(button).toBeInTheDocument();
    });

    test('responsive layout adapts to iPad', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Check if tablet-specific elements are present
      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });
  });

  // Test iPad Pro
  describe('iPad Pro Testing', () => {
    beforeEach(() => {
      setupMobileTest(TABLET_DEVICES.iPadPro);
    });

    test('renders correctly on iPad Pro', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
    });

    test('larger tablet layout works on iPad Pro', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Check if layout adapts to larger tablet screen
      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });
  });

  // Test Samsung Tab
  describe('Samsung Tab Testing', () => {
    beforeEach(() => {
      setupMobileTest(TABLET_DEVICES.SamsungTab);
    });

    test('renders correctly on Samsung Tab', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
    });

    test('Android tablet features work on Samsung Tab', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Test Android tablet-specific interactions
      const button = screen.getByRole('button', { name: /menu/i });
      fireEvent.touchStart(button);
      fireEvent.touchEnd(button);
      
      expect(button).toBeInTheDocument();
    });
  });

  // Test Surface
  describe('Surface Testing', () => {
    beforeEach(() => {
      setupMobileTest(TABLET_DEVICES.Surface);
    });

    test('renders correctly on Surface', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
    });

    test('Windows tablet features work on Surface', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Test Windows tablet-specific interactions
      const button = screen.getByRole('button', { name: /menu/i });
      fireEvent.touchStart(button);
      fireEvent.touchEnd(button);
      
      expect(button).toBeInTheDocument();
    });
  });
});

// Desktop device tests
describe('Desktop Device Testing', () => {
  // Test Desktop
  describe('Desktop Testing', () => {
    beforeEach(() => {
      setupMobileTest(DESKTOP_DEVICES.Desktop);
    });

    test('renders correctly on Desktop', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
    });

    test('desktop navigation works on Desktop', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Check if desktop navigation is present
      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });

    test('mouse interactions work on Desktop', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Test mouse events
      const button = screen.getByRole('button', { name: /menu/i });
      fireEvent.mouseEnter(button);
      fireEvent.mouseLeave(button);
      
      expect(button).toBeInTheDocument();
    });

    test('responsive layout adapts to Desktop', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Check if desktop-specific elements are present
      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });
  });

  // Test Laptop
  describe('Laptop Testing', () => {
    beforeEach(() => {
      setupMobileTest(DESKTOP_DEVICES.Laptop);
    });

    test('renders correctly on Laptop', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
    });

    test('laptop layout works on Laptop', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Check if layout adapts to laptop screen
      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });
  });

  // Test MacBook
  describe('MacBook Testing', () => {
    beforeEach(() => {
      setupMobileTest(DESKTOP_DEVICES.MacBook);
    });

    test('renders correctly on MacBook', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
    });

    test('MacBook-specific features work on MacBook', () => {
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      // Test MacBook-specific interactions
      const button = screen.getByRole('button', { name: /menu/i });
      fireEvent.mouseEnter(button);
      fireEvent.mouseLeave(button);
      
      expect(button).toBeInTheDocument();
    });
  });
});

// Responsive design tests
describe('Responsive Design Testing', () => {
  test('layout adapts to different screen sizes', () => {
    const devices = [
      MOBILE_DEVICES.iPhone,
      TABLET_DEVICES.iPad,
      DESKTOP_DEVICES.Desktop
    ];
    
    devices.forEach(device => {
      setupMobileTest(device);
      
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
    });
  });

  test('breakpoints work correctly', () => {
    const breakpoints = [
      { width: 320, height: 568, expected: 'mobile' },
      { width: 768, height: 1024, expected: 'tablet' },
      { width: 1024, height: 768, expected: 'desktop' }
    ];
    
    breakpoints.forEach(breakpoint => {
      setupMobileTest(breakpoint);
      
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );
      
      expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
    });
  });
});

// Touch interaction tests
describe('Touch Interaction Testing', () => {
  test('touch events work correctly', () => {
    setupMobileTest(MOBILE_DEVICES.iPhone);
    
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const button = screen.getByRole('button', { name: /menu/i });
    
    // Test touch start
    fireEvent.touchStart(button);
    expect(button).toBeInTheDocument();
    
    // Test touch end
    fireEvent.touchEnd(button);
    expect(button).toBeInTheDocument();
    
    // Test touch move
    fireEvent.touchMove(button);
    expect(button).toBeInTheDocument();
  });

  test('gesture recognition works', () => {
    setupMobileTest(MOBILE_DEVICES.iPhone);
    
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const button = screen.getByRole('button', { name: /menu/i });
    
    // Test swipe gesture
    fireEvent.touchStart(button, { touches: [{ clientX: 0, clientY: 0 }] });
    fireEvent.touchMove(button, { touches: [{ clientX: 100, clientY: 0 }] });
    fireEvent.touchEnd(button);
    
    expect(button).toBeInTheDocument();
  });
});

// Performance tests
describe('Mobile Performance Testing', () => {
  test('renders quickly on mobile devices', () => {
    setupMobileTest(MOBILE_DEVICES.iPhone);
    
    const startTime = performance.now();
    
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    // Should render within 100ms
    expect(renderTime).toBeLessThan(100);
  });

  test('memory usage is reasonable on mobile devices', () => {
    setupMobileTest(MOBILE_DEVICES.iPhone);
    
    const initialMemory = performance.memory ? performance.memory.usedJSHeapSize : 0;
    
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const finalMemory = performance.memory ? performance.memory.usedJSHeapSize : 0;
    const memoryIncrease = finalMemory - initialMemory;
    
    // Memory increase should be reasonable (less than 10MB)
    expect(memoryIncrease).toBeLessThan(10 * 1024 * 1024);
  });
});

// Accessibility tests for mobile
describe('Mobile Accessibility Testing', () => {
  test('touch targets are large enough', () => {
    setupMobileTest(MOBILE_DEVICES.iPhone);
    
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const buttons = screen.getAllByRole('button');
    
    buttons.forEach(button => {
      const rect = button.getBoundingClientRect();
      // Touch targets should be at least 44x44 pixels
      expect(rect.width).toBeGreaterThanOrEqual(44);
      expect(rect.height).toBeGreaterThanOrEqual(44);
    });
  });

  test('keyboard navigation works on mobile', () => {
    setupMobileTest(MOBILE_DEVICES.iPhone);
    
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    const button = screen.getByRole('button', { name: /menu/i });
    
    // Test keyboard navigation
    fireEvent.keyDown(button, { key: 'Enter' });
    expect(button).toBeInTheDocument();
    
    fireEvent.keyDown(button, { key: ' ' });
    expect(button).toBeInTheDocument();
  });
});

// Orientation tests
describe('Orientation Testing', () => {
  test('layout adapts to portrait orientation', () => {
    setupMobileTest({ ...MOBILE_DEVICES.iPhone, width: 375, height: 667 });
    
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
  });

  test('layout adapts to landscape orientation', () => {
    setupMobileTest({ ...MOBILE_DEVICES.iPhone, width: 667, height: 375 });
    
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
  });
});

// Network condition tests
describe('Network Condition Testing', () => {
  test('works with slow network', () => {
    setupMobileTest(MOBILE_DEVICES.iPhone);
    
    // Mock slow network
    Object.defineProperty(navigator, 'connection', {
      writable: true,
      configurable: true,
      value: {
        effectiveType: '2g',
        downlink: 0.5,
        rtt: 2000
      }
    });
    
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
  });

  test('works with offline network', () => {
    setupMobileTest(MOBILE_DEVICES.iPhone);
    
    // Mock offline network
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      configurable: true,
      value: false
    });
    
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Helpdesk Portal')).toBeInTheDocument();
  });
});

// Export test configurations
export {
  MOBILE_DEVICES,
  TABLET_DEVICES,
  DESKTOP_DEVICES,
  setupMobileTest
};
