/**
 * Module Federation Configuration for Micro-frontend Architecture
 * Enables splitting the application into smaller, independent modules
 */

import { ModuleFederationPlugin } from '@module-federation/webpack';

/**
 * Micro-frontend modules configuration
 */
export const microfrontendModules = {
  // Core modules
  core: {
    name: 'core',
    filename: 'remoteEntry.js',
    exposes: {
      './AuthContext': './src/contexts/AuthContext',
      './SocketContext': './src/contexts/SocketContext',
      './Layout': './src/components/Layout',
      './ErrorBoundary': './src/components/ErrorBoundary'
    },
    shared: {
      react: { singleton: true, requiredVersion: '^18.0.0' },
      'react-dom': { singleton: true, requiredVersion: '^18.0.0' },
      'react-router-dom': { singleton: true, requiredVersion: '^6.0.0' }
    }
  },

  // Ticket management module
  tickets: {
    name: 'tickets',
    filename: 'remoteEntry.js',
    exposes: {
      './TicketList': './src/components/TicketList',
      './TicketForm': './src/components/TicketForm',
      './TicketDetail': './src/pages/TicketDetail',
      './NewTicket': './src/pages/NewTicket',
      './VirtualizedTicketList': './src/components/VirtualizedTicketList'
    },
    shared: {
      react: { singleton: true, requiredVersion: '^18.0.0' },
      'react-dom': { singleton: true, requiredVersion: '^18.0.0' },
      'react-query': { singleton: true, requiredVersion: '^3.0.0' }
    }
  },

  // Dashboard module
  dashboard: {
    name: 'dashboard',
    filename: 'remoteEntry.js',
    exposes: {
      './Dashboard': './src/pages/Dashboard',
      './PerformanceDashboard': './src/components/PerformanceDashboard',
      './MetricsChart': './src/components/MetricsChart'
    },
    shared: {
      react: { singleton: true, requiredVersion: '^18.0.0' },
      'react-dom': { singleton: true, requiredVersion: '^18.0.0' },
      'chart.js': { singleton: true, requiredVersion: '^3.0.0' }
    }
  },

  // Knowledge base module
  knowledge: {
    name: 'knowledge',
    filename: 'remoteEntry.js',
    exposes: {
      './KnowledgeBase': './src/pages/KnowledgeBase',
      './SearchInput': './src/components/DebouncedSearchInput'
    },
    shared: {
      react: { singleton: true, requiredVersion: '^18.0.0' },
      'react-dom': { singleton: true, requiredVersion: '^18.0.0' }
    }
  },

  // Communication module
  communication: {
    name: 'communication',
    filename: 'remoteEntry.js',
    exposes: {
      './LiveChat': './src/components/LiveChat',
      './ChatMessage': './src/components/ChatMessage',
      './ChatInput': './src/components/ChatInput'
    },
    shared: {
      react: { singleton: true, requiredVersion: '^18.0.0' },
      'react-dom': { singleton: true, requiredVersion: '^18.0.0' },
      'socket.io-client': { singleton: true, requiredVersion: '^4.0.0' }
    }
  },

  // User management module
  user: {
    name: 'user',
    filename: 'remoteEntry.js',
    exposes: {
      './Profile': './src/pages/Profile',
      './UserSettings': './src/components/UserSettings',
      './Avatar': './src/components/Avatar'
    },
    shared: {
      react: { singleton: true, requiredVersion: '^18.0.0' },
      'react-dom': { singleton: true, requiredVersion: '^18.0.0' }
    }
  }
};

/**
 * Webpack configuration for Module Federation
 */
export const getModuleFederationConfig = (moduleName) => {
  const module = microfrontendModules[moduleName];
  
  if (!module) {
    throw new Error(`Module ${moduleName} not found`);
  }

  return {
    plugins: [
      new ModuleFederationPlugin({
        ...module,
        remotes: {
          // Import other modules as remotes
          ...Object.keys(microfrontendModules)
            .filter(name => name !== moduleName)
            .reduce((remotes, name) => {
              remotes[name] = `${name}@http://localhost:300${getPortForModule(name)}/remoteEntry.js`;
              return remotes;
            }, {})
        }
      })
    ]
  };
};

/**
 * Get port for module
 */
const getPortForModule = (moduleName) => {
  const portMap = {
    core: 1,
    tickets: 2,
    dashboard: 3,
    knowledge: 4,
    communication: 5,
    user: 6
  };
  
  return portMap[moduleName] || 1;
};

/**
 * Dynamic module loader
 */
export class DynamicModuleLoader {
  constructor() {
    this.loadedModules = new Set();
    this.moduleCache = new Map();
  }

  /**
   * Load module dynamically
   */
  async loadModule(moduleName, componentName) {
    const cacheKey = `${moduleName}:${componentName}`;
    
    if (this.moduleCache.has(cacheKey)) {
      return this.moduleCache.get(cacheKey);
    }

    try {
      const module = await import(`${moduleName}/${componentName}`);
      this.moduleCache.set(cacheKey, module);
      this.loadedModules.add(moduleName);
      return module;
    } catch (error) {
      console.error(`Failed to load module ${moduleName}/${componentName}:`, error);
      throw error;
    }
  }

  /**
   * Preload module
   */
  async preloadModule(moduleName) {
    try {
      const module = await import(`${moduleName}/remoteEntry.js`);
      this.loadedModules.add(moduleName);
      return module;
    } catch (error) {
      console.error(`Failed to preload module ${moduleName}:`, error);
      throw error;
    }
  }

  /**
   * Get loaded modules
   */
  getLoadedModules() {
    return Array.from(this.loadedModules);
  }

  /**
   * Clear module cache
   */
  clearCache() {
    this.moduleCache.clear();
    this.loadedModules.clear();
  }
}

/**
 * Micro-frontend router
 */
export class MicrofrontendRouter {
  constructor() {
    this.routes = new Map();
    this.moduleLoader = new DynamicModuleLoader();
  }

  /**
   * Register route
   */
  registerRoute(path, moduleName, componentName) {
    this.routes.set(path, { moduleName, componentName });
  }

  /**
   * Get route component
   */
  async getRouteComponent(path) {
    const route = this.routes.get(path);
    
    if (!route) {
      throw new Error(`Route ${path} not found`);
    }

    const { moduleName, componentName } = route;
    const module = await this.moduleLoader.loadModule(moduleName, componentName);
    
    return module.default || module[componentName];
  }

  /**
   * Preload route
   */
  async preloadRoute(path) {
    const route = this.routes.get(path);
    
    if (!route) {
      return;
    }

    const { moduleName } = route;
    await this.moduleLoader.preloadModule(moduleName);
  }
}

/**
 * Micro-frontend communication
 */
export class MicrofrontendCommunication {
  constructor() {
    this.eventBus = new EventTarget();
    this.subscribers = new Map();
  }

  /**
   * Publish event
   */
  publish(eventName, data) {
    const event = new CustomEvent(eventName, { detail: data });
    this.eventBus.dispatchEvent(event);
  }

  /**
   * Subscribe to event
   */
  subscribe(eventName, callback) {
    const handler = (event) => callback(event.detail);
    this.eventBus.addEventListener(eventName, handler);
    
    if (!this.subscribers.has(eventName)) {
      this.subscribers.set(eventName, new Set());
    }
    
    this.subscribers.get(eventName).add(handler);
    
    return () => this.unsubscribe(eventName, handler);
  }

  /**
   * Unsubscribe from event
   */
  unsubscribe(eventName, handler) {
    this.eventBus.removeEventListener(eventName, handler);
    
    if (this.subscribers.has(eventName)) {
      this.subscribers.get(eventName).delete(handler);
    }
  }

  /**
   * Get subscribers for event
   */
  getSubscribers(eventName) {
    return this.subscribers.get(eventName) || new Set();
  }
}

// Create global instances
export const moduleLoader = new DynamicModuleLoader();
export const microfrontendRouter = new MicrofrontendRouter();
export const microfrontendCommunication = new MicrofrontendCommunication();

export default {
  microfrontendModules,
  getModuleFederationConfig,
  DynamicModuleLoader,
  MicrofrontendRouter,
  MicrofrontendCommunication,
  moduleLoader,
  microfrontendRouter,
  microfrontendCommunication
};
