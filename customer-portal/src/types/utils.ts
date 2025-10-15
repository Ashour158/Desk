/**
 * Utility Type Definitions
 * 
 * This file contains type definitions for utility functions
 * including helpers, formatters, validators, and common utilities.
 */

import { ReactNode } from 'react';

// ============================================================================
// Generic Utility Types
// ============================================================================

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type Required<T, K extends keyof T> = T & { [P in K]-?: T[P] };
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type EventHandler<T = any> = (event: T) => void;
export type AsyncEventHandler<T = any> = (event: T) => Promise<void>;

export type Status = 'idle' | 'loading' | 'success' | 'error';
export type Size = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
export type Color = 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';

// ============================================================================
// Date and Time Types
// ============================================================================

export interface DateRange {
  start: Date;
  end: Date;
}

export interface TimeRange {
  start: string; // HH:MM format
  end: string; // HH:MM format
}

export interface DateTimeFormat {
  date: string;
  time: string;
  datetime: string;
  timezone: string;
}

export interface DateFormatOptions {
  format?: 'short' | 'medium' | 'long' | 'full';
  timezone?: string;
  locale?: string;
}

export interface TimeFormatOptions {
  format?: '12h' | '24h';
  showSeconds?: boolean;
  showMilliseconds?: boolean;
}

// ============================================================================
// Validation Types
// ============================================================================

export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  min?: number;
  max?: number;
  pattern?: RegExp;
  email?: boolean;
  url?: boolean;
  phone?: boolean;
  custom?: (value: any) => string | null;
}

export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
  warnings: Record<string, string>;
}

export interface FieldValidation {
  field: string;
  value: any;
  rules: ValidationRule[];
  result: ValidationResult;
}

// ============================================================================
// Formatting Types
// ============================================================================

export interface NumberFormatOptions {
  locale?: string;
  currency?: string;
  minimumFractionDigits?: number;
  maximumFractionDigits?: number;
  useGrouping?: boolean;
}

export interface CurrencyFormatOptions extends NumberFormatOptions {
  currency: string;
  currencyDisplay?: 'symbol' | 'code' | 'name';
}

export interface PercentageFormatOptions {
  locale?: string;
  minimumFractionDigits?: number;
  maximumFractionDigits?: number;
}

export interface FileSizeFormatOptions {
  binary?: boolean;
  precision?: number;
}

// ============================================================================
// File and Upload Types
// ============================================================================

export interface FileInfo {
  name: string;
  size: number;
  type: string;
  lastModified: Date;
  url?: string;
}

export interface FileUploadProgress {
  loaded: number;
  total: number;
  percentage: number;
  speed: number; // bytes per second
  estimatedTime: number; // seconds
}

export interface FileUploadOptions {
  maxSize?: number;
  maxFiles?: number;
  allowedTypes?: string[];
  allowedExtensions?: string[];
  onProgress?: (progress: FileUploadProgress) => void;
  onSuccess?: (file: FileInfo) => void;
  onError?: (error: string) => void;
}

export interface FileValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

// ============================================================================
// URL and Navigation Types
// ============================================================================

export interface URLParams {
  [key: string]: string | string[] | undefined;
}

export interface QueryParams {
  [key: string]: string | number | boolean | undefined;
}

export interface RouteParams {
  [key: string]: string;
}

export interface NavigationOptions {
  replace?: boolean;
  state?: any;
  scroll?: boolean;
}

// ============================================================================
// Storage Types
// ============================================================================

export interface StorageOptions {
  namespace?: string;
  serializer?: {
    serialize: (value: any) => string;
    deserialize: (value: string) => any;
  };
  validator?: (value: any) => boolean;
}

export interface StorageResult<T> {
  value: T | null;
  setValue: (value: T) => void;
  removeValue: () => void;
  hasValue: boolean;
  clear: () => void;
}

// ============================================================================
// API and HTTP Types
// ============================================================================

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
}

export interface ResponseOptions {
  status: number;
  statusText: string;
  headers: Record<string, string>;
  data: any;
}

export interface ApiError {
  message: string;
  code: string;
  status?: number;
  details?: Record<string, any>;
  timestamp: string;
}

export interface RetryOptions {
  maxRetries: number;
  retryDelay: number;
  retryCondition?: (error: ApiError) => boolean;
}

// ============================================================================
// Event and Observer Types
// ============================================================================

export interface EventEmitter<T = any> {
  on: (event: string, listener: (data: T) => void) => void;
  off: (event: string, listener: (data: T) => void) => void;
  emit: (event: string, data: T) => void;
  once: (event: string, listener: (data: T) => void) => void;
}

export interface Observer<T = any> {
  next: (value: T) => void;
  error: (error: Error) => void;
  complete: () => void;
}

export interface Subscription {
  unsubscribe: () => void;
  closed: boolean;
}

// ============================================================================
// Debounce and Throttle Types
// ============================================================================

export interface DebounceOptions {
  delay: number;
  leading?: boolean;
  trailing?: boolean;
  maxWait?: number;
}

export interface ThrottleOptions {
  delay: number;
  leading?: boolean;
  trailing?: boolean;
}

export interface DebouncedFunction<T extends (...args: any[]) => any> {
  (...args: Parameters<T>): void;
  cancel: () => void;
  flush: () => void;
}

export interface ThrottledFunction<T extends (...args: any[]) => any> {
  (...args: Parameters<T>): void;
  cancel: () => void;
  flush: () => void;
}

// ============================================================================
// Cache Types
// ============================================================================

export interface CacheOptions {
  ttl?: number; // time to live in milliseconds
  maxSize?: number;
  evictionPolicy?: 'lru' | 'lfu' | 'fifo';
}

export interface CacheEntry<T = any> {
  key: string;
  value: T;
  timestamp: number;
  ttl: number;
  hits: number;
}

export interface CacheResult<T = any> {
  value: T | null;
  hit: boolean;
  miss: boolean;
  expired: boolean;
}

// ============================================================================
// Pagination Types
// ============================================================================

export interface PaginationOptions {
  page: number;
  pageSize: number;
  total?: number;
  showSizeChanger?: boolean;
  showQuickJumper?: boolean;
  showTotal?: boolean;
  pageSizeOptions?: number[];
}

export interface PaginationResult {
  current: number;
  pageSize: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
  startIndex: number;
  endIndex: number;
}

// ============================================================================
// Sorting Types
// ============================================================================

export interface SortOptions {
  field: string;
  order: 'asc' | 'desc';
}

export interface SortResult<T = any> {
  data: T[];
  sort: SortOptions;
  sorted: boolean;
}

// ============================================================================
// Filtering Types
// ============================================================================

export interface FilterOptions {
  field: string;
  operator: FilterOperator;
  value: any;
}

export type FilterOperator = 
  | 'equals' 
  | 'not_equals' 
  | 'contains' 
  | 'not_contains' 
  | 'starts_with' 
  | 'ends_with' 
  | 'greater_than' 
  | 'less_than' 
  | 'between' 
  | 'in' 
  | 'not_in'
  | 'is_null'
  | 'is_not_null';

export interface FilterResult<T = any> {
  data: T[];
  filters: FilterOptions[];
  filtered: boolean;
}

// ============================================================================
// Search Types
// ============================================================================

export interface SearchOptions {
  query: string;
  fields?: string[];
  fuzzy?: boolean;
  caseSensitive?: boolean;
  wholeWord?: boolean;
}

export interface SearchResult<T = any> {
  data: T[];
  query: string;
  total: number;
  highlights: Record<string, string[]>;
  score: number;
}

// ============================================================================
// Theme and Styling Types
// ============================================================================

export interface Theme {
  colors: {
    primary: string;
    secondary: string;
    success: string;
    warning: string;
    danger: string;
    info: string;
    light: string;
    dark: string;
    white: string;
    black: string;
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  typography: {
    fontFamily: string;
    fontSize: {
      xs: string;
      sm: string;
      md: string;
      lg: string;
      xl: string;
    };
    fontWeight: {
      normal: number;
      medium: number;
      semibold: number;
      bold: number;
    };
  };
  breakpoints: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  shadows: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  borderRadius: {
    sm: string;
    md: string;
    lg: string;
    full: string;
  };
}

export interface StyledComponentProps {
  theme?: Theme;
  variant?: string;
  size?: Size;
  color?: Color;
  disabled?: boolean;
  loading?: boolean;
}

// ============================================================================
// Animation Types
// ============================================================================

export interface AnimationOptions {
  duration?: number;
  delay?: number;
  easing?: string;
  fill?: 'none' | 'forwards' | 'backwards' | 'both';
  direction?: 'normal' | 'reverse' | 'alternate' | 'alternate-reverse';
  iterationCount?: number | 'infinite';
}

export interface AnimationResult {
  play: () => void;
  pause: () => void;
  reverse: () => void;
  finish: () => void;
  cancel: () => void;
  isPlaying: boolean;
  isPaused: boolean;
  isFinished: boolean;
}

// ============================================================================
// Performance Types
// ============================================================================

export interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  memoryUsage: number;
  cpuUsage: number;
  networkLatency: number;
}

export interface PerformanceOptions {
  measureRender?: boolean;
  measureMemory?: boolean;
  measureNetwork?: boolean;
  threshold?: number;
}

export interface PerformanceResult {
  metrics: PerformanceMetrics;
  isSlow: boolean;
  recommendations: string[];
}

// ============================================================================
// Accessibility Types
// ============================================================================

export interface AccessibilityOptions {
  role?: string;
  ariaLabel?: string;
  ariaDescribedBy?: string;
  ariaLabelledBy?: string;
  tabIndex?: number;
  focusable?: boolean;
  keyboard?: boolean;
  screenReader?: boolean;
}

export interface AccessibilityResult {
  violations: AccessibilityViolation[];
  warnings: AccessibilityWarning[];
  score: number;
  recommendations: string[];
}

export interface AccessibilityViolation {
  rule: string;
  impact: 'minor' | 'moderate' | 'serious' | 'critical';
  description: string;
  help: string;
  nodes: string[];
}

export interface AccessibilityWarning {
  rule: string;
  description: string;
  help: string;
  nodes: string[];
}

// ============================================================================
// Export all types
// ============================================================================

export * from './index';
