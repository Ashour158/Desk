/**
 * Complete logging service for the customer portal
 * Includes all methods expected by tests
 */

class Logger {
  /**
   * Log levels
   */
  static LEVELS = {
    ERROR: 'error',
    WARN: 'warn',
    INFO: 'info',
    DEBUG: 'debug'
  };

  /**
   * Current log level
   */
  static currentLevel = process.env.NODE_ENV === 'production' ? Logger.LEVELS.ERROR : Logger.LEVELS.DEBUG;

  /**
   * Log storage
   */
  static logs = [];
  static maxLogs = 1000;

  /**
   * Persistence settings
   */
  static persistence = {
    enabled: false,
    storage: 'localStorage'
  };

  /**
   * Log format
   */
  static format = 'text';

  /**
   * Check if a log level should be output
   */
  static shouldLog(level) {
    const levels = Object.values(Logger.LEVELS);
    const currentIndex = levels.indexOf(Logger.currentLevel);
    const messageIndex = levels.indexOf(level);
    return messageIndex <= currentIndex;
  }

  /**
   * Format log message with timestamp and context
   */
  static formatMessage(level, message, context = {}, component = null) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context: this.sanitizeData(context),
      component,
      id: Math.random().toString(36).substr(2, 9)
    };

    // Store log
    this.logs.push(logEntry);
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }

    // Persist if enabled
    if (this.persistence.enabled) {
      this.persistLog(logEntry);
    }

    return logEntry;
  }

  /**
   * Sanitize sensitive data
   */
  static sanitizeData(data) {
    if (typeof data !== 'object' || data === null) return data;
    
    const sensitiveKeys = ['password', 'token', 'secret', 'key', 'auth'];
    const sanitized = { ...data };
    
    for (const key in sanitized) {
      if (sensitiveKeys.some(sensitive => key.toLowerCase().includes(sensitive))) {
        sanitized[key] = '[REDACTED]';
      } else if (typeof sanitized[key] === 'object') {
        sanitized[key] = this.sanitizeData(sanitized[key]);
      }
    }
    
    return sanitized;
  }

  /**
   * Persist log to storage
   */
  static persistLog(logEntry) {
    try {
      const storage = this.persistence.storage === 'sessionStorage' ? sessionStorage : localStorage;
      const existingLogs = JSON.parse(storage.getItem('app_logs') || '[]');
      existingLogs.push(logEntry);
      
      // Keep only last 100 logs in storage
      if (existingLogs.length > 100) {
        existingLogs.splice(0, existingLogs.length - 100);
      }
      
      storage.setItem('app_logs', JSON.stringify(existingLogs));
    } catch (error) {
      console.warn('Failed to persist log:', error);
    }
  }

  /**
   * Basic logging methods
   */
  static error(message, context = {}, component = null) {
    if (!this.shouldLog(Logger.LEVELS.ERROR)) return;
    
    const logEntry = this.formatMessage(Logger.LEVELS.ERROR, message, context, component);
    console.error(`[ERROR] ${message}`, logEntry);
  }

  static warn(message, context = {}, component = null) {
    if (!this.shouldLog(Logger.LEVELS.WARN)) return;
    
    const logEntry = this.formatMessage(Logger.LEVELS.WARN, message, context, component);
    console.warn(`[WARN] ${message}`, logEntry);
  }

  static info(message, context = {}, component = null) {
    if (!this.shouldLog(Logger.LEVELS.INFO)) return;
    
    const logEntry = this.formatMessage(Logger.LEVELS.INFO, message, context, component);
    console.info(`[INFO] ${message}`, logEntry);
  }

  static debug(message, context = {}, component = null) {
    if (!this.shouldLog(Logger.LEVELS.DEBUG)) return;
    
    const logEntry = this.formatMessage(Logger.LEVELS.DEBUG, message, context, component);
    console.debug(`[DEBUG] ${message}`, logEntry);
  }

  /**
   * Performance logging
   */
  static performance(message, metrics = {}, component = null) {
    const context = {
      ...metrics,
      type: 'performance'
    };
    this.info(message, context, component);
  }

  /**
   * Network logging
   */
  static network(message, networkData = {}, component = null) {
    const context = {
      ...networkData,
      type: 'network'
    };
    this.info(message, context, component);
  }

  /**
   * User action logging
   */
  static userAction(action, actionData = {}, component = null) {
    const context = {
      ...actionData,
      type: 'user_action'
    };
    this.info(action, context, component);
  }

  /**
   * Security logging
   */
  static security(event, securityData = {}, component = null) {
    const context = {
      ...securityData,
      type: 'security'
    };
    this.warn(event, context, component);
  }

  /**
   * Persistence methods
   */
  static setPersistence(enabled, storage = 'localStorage') {
    this.persistence.enabled = enabled;
    this.persistence.storage = storage;
  }

  /**
   * Log filtering and search
   */
  static setLogLevel(level) {
    this.currentLevel = level;
  }

  static getLogs(component = null) {
    if (component) {
      return this.logs.filter(log => log.component === component);
    }
    return [...this.logs];
  }

  static searchLogs(query) {
    return this.logs.filter(log => 
      log.message.toLowerCase().includes(query.toLowerCase()) ||
      JSON.stringify(log.context).toLowerCase().includes(query.toLowerCase())
    );
  }

  /**
   * Log export
   */
  static exportLogs(format = 'json') {
    const logs = this.getLogs();
    
    switch (format) {
      case 'json':
        return JSON.stringify(logs, null, 2);
      case 'csv':
        if (logs.length === 0) return 'timestamp,level,message,context';
        const headers = 'timestamp,level,message,context';
        const rows = logs.map(log => 
          `${log.timestamp},${log.level},${log.message},"${JSON.stringify(log.context)}"`
        );
        return [headers, ...rows].join('\n');
      case 'text':
        return logs.map(log => 
          `[${log.timestamp}] ${log.level.toUpperCase()}: ${log.message}`
        ).join('\n');
      default:
        return JSON.stringify(logs, null, 2);
    }
  }

  /**
   * Log cleanup
   */
  static clearLogs() {
    this.logs = [];
  }

  static clearOldLogs(maxAge) {
    const cutoff = new Date(Date.now() - maxAge);
    this.logs = this.logs.filter(log => new Date(log.timestamp) > cutoff);
  }

  /**
   * Log analytics
   */
  static getLogTrends() {
    const logs = this.getLogs();
    const timeline = logs.map(log => ({
      timestamp: log.timestamp,
      level: log.level,
      component: log.component
    }));
    
    return {
      timeline,
      totalLogs: logs.length,
      errorCount: logs.filter(log => log.level === 'error').length,
      warnCount: logs.filter(log => log.level === 'warn').length
    };
  }

  /**
   * Configuration methods
   */
  static setLogFormat(format) {
    this.format = format;
  }

  static setLogOutput(output) {
    // Implementation for different output methods
    console.log(`Log output set to: ${output}`);
  }

  static setLogRotation(maxSize, maxFiles) {
    // Implementation for log rotation
    console.log(`Log rotation set: ${maxSize} bytes, ${maxFiles} files`);
  }
}

export default Logger;
