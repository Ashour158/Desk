import { useState, useEffect } from 'react';

/**
 * Custom hook for debouncing values
 * @param {any} value - The value to debounce
 * @param {number} delay - The delay in milliseconds
 * @returns {any} The debounced value
 */
export const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);
  
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);
  
  return debouncedValue;
};

/**
 * Custom hook for debouncing callbacks
 * @param {Function} callback - The callback function to debounce
 * @param {number} delay - The delay in milliseconds
 * @param {Object} options - Additional options
 * @returns {Function} The debounced callback
 */
export const useDebouncedCallback = (callback, delay, options = {}) => {
  const {
    leading = false,
    trailing = true,
    maxWait = null
  } = options;
  
  const [timeoutId, setTimeoutId] = useState(null);
  const [maxTimeoutId, setMaxTimeoutId] = useState(null);
  const [lastCallTime, setLastCallTime] = useState(0);
  const [lastInvokeTime, setLastInvokeTime] = useState(0);
  
  const debouncedCallback = useCallback((...args) => {
    const now = Date.now();
    const timeSinceLastCall = now - lastCallTime;
    const timeSinceLastInvoke = now - lastInvokeTime;
    
    setLastCallTime(now);
    
    // Clear existing timeouts
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    if (maxTimeoutId) {
      clearTimeout(maxTimeoutId);
    }
    
    // Leading edge
    if (leading && timeSinceLastCall >= delay) {
      setLastInvokeTime(now);
      callback(...args);
      return;
    }
    
    // Max wait timeout
    if (maxWait && timeSinceLastInvoke >= maxWait) {
      setLastInvokeTime(now);
      callback(...args);
      return;
    }
    
    // Regular debounce
    const newTimeoutId = setTimeout(() => {
      if (trailing) {
        setLastInvokeTime(Date.now());
        callback(...args);
      }
    }, delay);
    
    setTimeoutId(newTimeoutId);
    
    // Max wait timeout
    if (maxWait) {
      const newMaxTimeoutId = setTimeout(() => {
        setLastInvokeTime(Date.now());
        callback(...args);
      }, maxWait);
      setMaxTimeoutId(newMaxTimeoutId);
    }
  }, [callback, delay, leading, trailing, maxWait, timeoutId, maxTimeoutId, lastCallTime, lastInvokeTime]);
  
  useEffect(() => {
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      if (maxTimeoutId) {
        clearTimeout(maxTimeoutId);
      }
    };
  }, [timeoutId, maxTimeoutId]);
  
  return debouncedCallback;
};

export default useDebounce;
