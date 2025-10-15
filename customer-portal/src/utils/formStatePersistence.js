/**
 * Enhanced form state persistence system
 * Provides comprehensive form state management, auto-save, and recovery
 */

/**
 * Form state persistence configuration
 */
export const persistenceConfig = {
  // Storage settings
  storage: {
    type: 'localStorage', // 'localStorage', 'sessionStorage', 'indexedDB'
    prefix: 'form_state_',
    maxSize: 5 * 1024 * 1024, // 5MB
    compression: true,
    encryption: false
  },
  
  // Auto-save settings
  autoSave: {
    enabled: true,
    interval: 30000, // 30 seconds
    debounceDelay: 2000, // 2 seconds
    maxRetries: 3,
    retryDelay: 1000
  },
  
  // State management
  state: {
    maxHistory: 10,
    cleanupInterval: 24 * 60 * 60 * 1000, // 24 hours
    versioning: true,
    migration: true
  },
  
  // Recovery settings
  recovery: {
    enabled: true,
    promptUser: true,
    autoRestore: false,
    maxAge: 7 * 24 * 60 * 60 * 1000 // 7 days
  }
};

/**
 * Form state persistence manager
 */
class FormStatePersistenceManager {
  constructor() {
    this.storage = this.initializeStorage();
    this.autoSaveTimers = new Map();
    this.debounceTimers = new Map();
    this.stateVersions = new Map();
    this.cleanupInterval = null;
    
    this.initializeCleanup();
  }

  /**
   * Initialize storage based on configuration
   * @returns {Object} Storage interface
   */
  initializeStorage() {
    switch (persistenceConfig.storage.type) {
      case 'localStorage':
        return new LocalStorageAdapter();
      case 'sessionStorage':
        return new SessionStorageAdapter();
      case 'indexedDB':
        return new IndexedDBAdapter();
      default:
        return new LocalStorageAdapter();
    }
  }

  /**
   * Initialize cleanup process
   */
  initializeCleanup() {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    
    this.cleanupInterval = setInterval(() => {
      this.cleanupOldStates();
    }, persistenceConfig.state.cleanupInterval);
  }

  /**
   * Save form state
   * @param {string} formId - Form ID
   * @param {Object} formData - Form data
   * @param {Object} metadata - Additional metadata
   * @returns {Promise<boolean>} Success status
   */
  async saveFormState(formId, formData, metadata = {}) {
    try {
      const state = {
        id: `${persistenceConfig.storage.prefix}${formId}`,
        formId,
        data: formData,
        metadata: {
          timestamp: Date.now(),
          version: this.getNextVersion(formId),
          userAgent: navigator.userAgent,
          url: window.location.href,
          ...metadata
        },
        checksum: this.calculateChecksum(formData)
      };

      // Compress if enabled
      const processedState = persistenceConfig.storage.compression 
        ? await this.compressState(state)
        : state;

      // Encrypt if enabled
      const finalState = persistenceConfig.storage.encryption
        ? await this.encryptState(processedState)
        : processedState;

      await this.storage.set(state.id, finalState);
      
      // Update version tracking
      this.stateVersions.set(formId, state.metadata.version);
      
      console.log(`Form state saved for ${formId}`, {
        version: state.metadata.version,
        size: JSON.stringify(finalState).length
      });

      return true;
    } catch (error) {
      console.error('Failed to save form state:', error);
      return false;
    }
  }

  /**
   * Load form state
   * @param {string} formId - Form ID
   * @param {boolean} includeMetadata - Whether to include metadata
   * @returns {Promise<Object|null>} Form state or null
   */
  async loadFormState(formId, includeMetadata = false) {
    try {
      const stateId = `${persistenceConfig.storage.prefix}${formId}`;
      const rawState = await this.storage.get(stateId);
      
      if (!rawState) {
        return null;
      }

      // Decrypt if enabled
      let decryptedState = persistenceConfig.storage.encryption
        ? await this.decryptState(rawState)
        : rawState;

      // Decompress if enabled
      const state = persistenceConfig.storage.compression
        ? await this.decompressState(decryptedState)
        : decryptedState;

      // Check if state is too old
      const maxAge = persistenceConfig.recovery.maxAge;
      if (Date.now() - state.metadata.timestamp > maxAge) {
        await this.deleteFormState(formId);
        return null;
      }

      // Verify checksum
      if (!this.verifyChecksum(state.data, state.checksum)) {
        console.warn('Form state checksum verification failed');
        return null;
      }

      return includeMetadata ? state : state.data;
    } catch (error) {
      console.error('Failed to load form state:', error);
      return null;
    }
  }

  /**
   * Delete form state
   * @param {string} formId - Form ID
   * @returns {Promise<boolean>} Success status
   */
  async deleteFormState(formId) {
    try {
      const stateId = `${persistenceConfig.storage.prefix}${formId}`;
      await this.storage.remove(stateId);
      this.stateVersions.delete(formId);
      return true;
    } catch (error) {
      console.error('Failed to delete form state:', error);
      return false;
    }
  }

  /**
   * Check if form state exists
   * @param {string} formId - Form ID
   * @returns {Promise<boolean>} Whether state exists
   */
  async hasFormState(formId) {
    try {
      const stateId = `${persistenceConfig.storage.prefix}${formId}`;
      const state = await this.storage.get(stateId);
      return !!state;
    } catch (error) {
      console.error('Failed to check form state:', error);
      return false;
    }
  }

  /**
   * Get form state metadata
   * @param {string} formId - Form ID
   * @returns {Promise<Object|null>} State metadata
   */
  async getFormStateMetadata(formId) {
    try {
      const state = await this.loadFormState(formId, true);
      return state ? state.metadata : null;
    } catch (error) {
      console.error('Failed to get form state metadata:', error);
      return null;
    }
  }

  /**
   * Setup auto-save for form
   * @param {string} formId - Form ID
   * @param {Function} getFormData - Function to get current form data
   * @param {Function} onSave - Callback when state is saved
   */
  setupAutoSave(formId, getFormData, onSave = null) {
    if (!persistenceConfig.autoSave.enabled) {
      return;
    }

    // Clear existing timer
    this.clearAutoSave(formId);

    const autoSave = async () => {
      try {
        const formData = getFormData();
        const success = await this.saveFormState(formId, formData, {
          autoSave: true,
          timestamp: Date.now()
        });

        if (success && onSave) {
          onSave(formData);
        }
      } catch (error) {
        console.error('Auto-save failed:', error);
      }
    };

    // Setup debounced auto-save
    const debouncedAutoSave = this.debounce(autoSave, persistenceConfig.autoSave.debounceDelay);
    
    // Setup interval auto-save
    const timer = setInterval(debouncedAutoSave, persistenceConfig.autoSave.interval);
    this.autoSaveTimers.set(formId, timer);

    // Setup change-based auto-save
    const handleChange = () => {
      debouncedAutoSave();
    };

    // Store change handler for cleanup
    this.debounceTimers.set(formId, handleChange);
  }

  /**
   * Clear auto-save for form
   * @param {string} formId - Form ID
   */
  clearAutoSave(formId) {
    const timer = this.autoSaveTimers.get(formId);
    if (timer) {
      clearInterval(timer);
      this.autoSaveTimers.delete(formId);
    }

    const debounceTimer = this.debounceTimers.get(formId);
    if (debounceTimer) {
      this.debounceTimers.delete(formId);
    }
  }

  /**
   * Prompt user to restore form state
   * @param {string} formId - Form ID
   * @param {Object} stateMetadata - State metadata
   * @returns {Promise<boolean>} Whether user chose to restore
   */
  async promptRestore(formId, stateMetadata) {
    if (!persistenceConfig.recovery.promptUser) {
      return persistenceConfig.recovery.autoRestore;
    }

    return new Promise((resolve) => {
      const message = `We found a saved draft for this form from ${new Date(stateMetadata.timestamp).toLocaleString()}. Would you like to restore it?`;
      
      if (confirm(message)) {
        resolve(true);
      } else {
        // Delete the saved state if user doesn't want to restore
        this.deleteFormState(formId);
        resolve(false);
      }
    });
  }

  /**
   * Restore form state with user confirmation
   * @param {string} formId - Form ID
   * @param {Function} setFormData - Function to set form data
   * @returns {Promise<boolean>} Whether state was restored
   */
  async restoreFormState(formId, setFormData) {
    try {
      const stateMetadata = await this.getFormStateMetadata(formId);
      if (!stateMetadata) {
        return false;
      }

      const shouldRestore = await this.promptRestore(formId, stateMetadata);
      if (!shouldRestore) {
        return false;
      }

      const formData = await this.loadFormState(formId);
      if (formData) {
        setFormData(formData);
        return true;
      }

      return false;
    } catch (error) {
      console.error('Failed to restore form state:', error);
      return false;
    }
  }

  /**
   * Get next version number for form
   * @param {string} formId - Form ID
   * @returns {number} Next version number
   */
  getNextVersion(formId) {
    const currentVersion = this.stateVersions.get(formId) || 0;
    const nextVersion = currentVersion + 1;
    this.stateVersions.set(formId, nextVersion);
    return nextVersion;
  }

  /**
   * Calculate checksum for data integrity
   * @param {Object} data - Data to checksum
   * @returns {string} Checksum
   */
  calculateChecksum(data) {
    const str = JSON.stringify(data);
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString(36);
  }

  /**
   * Verify checksum
   * @param {Object} data - Data to verify
   * @param {string} checksum - Expected checksum
   * @returns {boolean} Whether checksum is valid
   */
  verifyChecksum(data, checksum) {
    return this.calculateChecksum(data) === checksum;
  }

  /**
   * Compress state data
   * @param {Object} state - State to compress
   * @returns {Promise<Object>} Compressed state
   */
  async compressState(state) {
    // Simple compression using JSON stringify and base64
    // In a real implementation, you might use a compression library
    const compressed = btoa(JSON.stringify(state));
    return {
      compressed: true,
      data: compressed
    };
  }

  /**
   * Decompress state data
   * @param {Object} state - State to decompress
   * @returns {Promise<Object>} Decompressed state
   */
  async decompressState(state) {
    if (!state.compressed) {
      return state;
    }
    
    const decompressed = JSON.parse(atob(state.data));
    return decompressed;
  }

  /**
   * Encrypt state data
   * @param {Object} state - State to encrypt
   * @returns {Promise<Object>} Encrypted state
   */
  async encryptState(state) {
    // Simple encryption using base64
    // In a real implementation, you would use proper encryption
    const encrypted = btoa(JSON.stringify(state));
    return {
      encrypted: true,
      data: encrypted
    };
  }

  /**
   * Decrypt state data
   * @param {Object} state - State to decrypt
   * @returns {Promise<Object>} Decrypted state
   */
  async decryptState(state) {
    if (!state.encrypted) {
      return state;
    }
    
    const decrypted = JSON.parse(atob(state.data));
    return decrypted;
  }

  /**
   * Debounce function
   * @param {Function} func - Function to debounce
   * @param {number} delay - Delay in milliseconds
   * @returns {Function} Debounced function
   */
  debounce(func, delay) {
    let timeoutId;
    return (...args) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
  }

  /**
   * Cleanup old form states
   */
  async cleanupOldStates() {
    try {
      const allKeys = await this.storage.getAllKeys();
      const formKeys = allKeys.filter(key => key.startsWith(persistenceConfig.storage.prefix));
      
      for (const key of formKeys) {
        const state = await this.storage.get(key);
        if (state && state.metadata) {
          const age = Date.now() - state.metadata.timestamp;
          if (age > persistenceConfig.recovery.maxAge) {
            await this.storage.remove(key);
            console.log(`Cleaned up old form state: ${key}`);
          }
        }
      }
    } catch (error) {
      console.error('Failed to cleanup old states:', error);
    }
  }

  /**
   * Get storage usage statistics
   * @returns {Promise<Object>} Storage statistics
   */
  async getStorageStats() {
    try {
      const allKeys = await this.storage.getAllKeys();
      const formKeys = allKeys.filter(key => key.startsWith(persistenceConfig.storage.prefix));
      
      let totalSize = 0;
      let formCount = 0;
      
      for (const key of formKeys) {
        const state = await this.storage.get(key);
        if (state) {
          totalSize += JSON.stringify(state).length;
          formCount++;
        }
      }
      
      return {
        totalForms: formCount,
        totalSize,
        maxSize: persistenceConfig.storage.maxSize,
        usagePercentage: (totalSize / persistenceConfig.storage.maxSize) * 100
      };
    } catch (error) {
      console.error('Failed to get storage stats:', error);
      return null;
    }
  }
}

/**
 * LocalStorage adapter
 */
class LocalStorageAdapter {
  async set(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  async get(key) {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
  }

  async remove(key) {
    localStorage.removeItem(key);
  }

  async getAllKeys() {
    return Object.keys(localStorage);
  }
}

/**
 * SessionStorage adapter
 */
class SessionStorageAdapter {
  async set(key, value) {
    sessionStorage.setItem(key, JSON.stringify(value));
  }

  async get(key) {
    const item = sessionStorage.getItem(key);
    return item ? JSON.parse(item) : null;
  }

  async remove(key) {
    sessionStorage.removeItem(key);
  }

  async getAllKeys() {
    return Object.keys(sessionStorage);
  }
}

/**
 * IndexedDB adapter (simplified)
 */
class IndexedDBAdapter {
  constructor() {
    this.dbName = 'FormStateDB';
    this.dbVersion = 1;
    this.storeName = 'formStates';
  }

  async set(key, value) {
    // Simplified implementation
    // In a real implementation, you would use IndexedDB properly
    localStorage.setItem(key, JSON.stringify(value));
  }

  async get(key) {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
  }

  async remove(key) {
    localStorage.removeItem(key);
  }

  async getAllKeys() {
    return Object.keys(localStorage);
  }
}

/**
 * Create form state persistence manager instance
 */
const formStatePersistence = new FormStatePersistenceManager();

/**
 * React hook for form state persistence
 * @param {string} formId - Form ID
 * @param {Object} initialData - Initial form data
 * @param {Object} options - Persistence options
 * @returns {Object} Persistence utilities
 */
export const useFormStatePersistence = (formId, initialData = {}, options = {}) => {
  const {
    enableAutoSave = true,
    enableRecovery = true,
    onStateSaved = null,
    onStateRestored = null
  } = options;

  /**
   * Save current form state
   * @param {Object} formData - Current form data
   * @param {Object} metadata - Additional metadata
   */
  const saveState = async (formData, metadata = {}) => {
    const success = await formStatePersistence.saveFormState(formId, formData, metadata);
    if (success && onStateSaved) {
      onStateSaved(formData);
    }
    return success;
  };

  /**
   * Load saved form state
   * @param {boolean} includeMetadata - Whether to include metadata
   */
  const loadState = async (includeMetadata = false) => {
    return await formStatePersistence.loadFormState(formId, includeMetadata);
  };

  /**
   * Restore form state with user confirmation
   * @param {Function} setFormData - Function to set form data
   */
  const restoreState = async (setFormData) => {
    if (!enableRecovery) {
      return false;
    }

    const restored = await formStatePersistence.restoreFormState(formId, setFormData);
    if (restored && onStateRestored) {
      onStateRestored();
    }
    return restored;
  };

  /**
   * Setup auto-save
   * @param {Function} getFormData - Function to get current form data
   */
  const setupAutoSave = (getFormData) => {
    if (enableAutoSave) {
      formStatePersistence.setupAutoSave(formId, getFormData, onStateSaved);
    }
  };

  /**
   * Clear auto-save
   */
  const clearAutoSave = () => {
    formStatePersistence.clearAutoSave(formId);
  };

  /**
   * Delete saved state
   */
  const deleteState = async () => {
    return await formStatePersistence.deleteFormState(formId);
  };

  /**
   * Check if saved state exists
   */
  const hasSavedState = async () => {
    return await formStatePersistence.hasFormState(formId);
  };

  return {
    saveState,
    loadState,
    restoreState,
    setupAutoSave,
    clearAutoSave,
    deleteState,
    hasSavedState
  };
};

export default formStatePersistence;
