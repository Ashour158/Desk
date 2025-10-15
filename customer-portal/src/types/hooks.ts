/**
 * Hook Type Definitions
 * 
 * This file contains type definitions for custom React hooks
 * including state management, API calls, and form handling.
 */

import { ReactNode } from 'react';
import { 
  User, 
  Ticket, 
  WorkOrder, 
  Notification, 
  PaginatedResponse,
  FormData,
  FormErrors 
} from './index';

// ============================================================================
// API Hook Types
// ============================================================================

export interface UseApiOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
  retry?: number;
  retryDelay?: number;
  cacheTime?: number;
  staleTime?: number;
}

export interface UseApiResult<T = any> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  mutate: (data: any) => Promise<void>;
  isSuccess: boolean;
  isError: boolean;
  isIdle: boolean;
}

export interface UseMutationOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
  onSettled?: (data: any, error: Error | null) => void;
}

export interface UseMutationResult<T = any> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  mutate: (variables: any) => Promise<T>;
  reset: () => void;
  isSuccess: boolean;
  isError: boolean;
  isIdle: boolean;
}

// ============================================================================
// Form Hook Types
// ============================================================================

export interface UseFormOptions<T = any> {
  initialValues?: T;
  validation?: FormValidation;
  onSubmit?: (values: T) => void | Promise<void>;
  validateOnChange?: boolean;
  validateOnBlur?: boolean;
  validateOnMount?: boolean;
}

export interface UseFormResult<T = any> {
  values: T;
  errors: FormErrors;
  touched: Record<string, boolean>;
  isValid: boolean;
  isSubmitting: boolean;
  isDirty: boolean;
  setValue: (name: string, value: any) => void;
  setError: (name: string, error: string) => void;
  setTouched: (name: string, touched: boolean) => void;
  setValues: (values: Partial<T>) => void;
  setErrors: (errors: FormErrors) => void;
  handleSubmit: (event?: React.FormEvent) => void;
  handleChange: (name: string, value: any) => void;
  handleBlur: (name: string) => void;
  reset: () => void;
  validate: () => Promise<boolean>;
  validateField: (name: string) => Promise<boolean>;
}

export interface FormValidation {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
  min?: number;
  max?: number;
  email?: boolean;
  url?: boolean;
  custom?: (value: any) => string | null;
}

// ============================================================================
// State Management Hook Types
// ============================================================================

export interface UseStateOptions<T> {
  initialValue: T;
  validator?: (value: T) => boolean;
  transformer?: (value: T) => T;
}

export interface UseStateResult<T> {
  value: T;
  setValue: (value: T | ((prev: T) => T)) => void;
  reset: () => void;
  isValid: boolean;
}

export interface UseToggleOptions {
  initialValue?: boolean;
  onToggle?: (value: boolean) => void;
}

export interface UseToggleResult {
  value: boolean;
  toggle: () => void;
  setTrue: () => void;
  setFalse: () => void;
  setValue: (value: boolean) => void;
}

export interface UseCounterOptions {
  initialValue?: number;
  min?: number;
  max?: number;
  step?: number;
  onCount?: (count: number) => void;
}

export interface UseCounterResult {
  count: number;
  increment: () => void;
  decrement: () => void;
  setCount: (count: number) => void;
  reset: () => void;
  canIncrement: boolean;
  canDecrement: boolean;
}

// ============================================================================
// Local Storage Hook Types
// ============================================================================

export interface UseLocalStorageOptions<T> {
  initialValue: T;
  serializer?: {
    serialize: (value: T) => string;
    deserialize: (value: string) => T;
  };
  validator?: (value: any) => value is T;
}

export interface UseLocalStorageResult<T> {
  value: T;
  setValue: (value: T | ((prev: T) => T)) => void;
  removeValue: () => void;
  isPersisted: boolean;
}

export interface UseSessionStorageOptions<T> {
  initialValue: T;
  serializer?: {
    serialize: (value: T) => string;
    deserialize: (value: string) => T;
  };
  validator?: (value: any) => value is T;
}

export interface UseSessionStorageResult<T> {
  value: T;
  setValue: (value: T | ((prev: T) => T)) => void;
  removeValue: () => void;
  isPersisted: boolean;
}

// ============================================================================
// Async Hook Types
// ============================================================================

export interface UseAsyncOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
  retry?: number;
  retryDelay?: number;
}

export interface UseAsyncResult<T = any> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  execute: (...args: any[]) => Promise<T>;
  reset: () => void;
  isSuccess: boolean;
  isError: boolean;
  isIdle: boolean;
}

export interface UseAsyncCallbackOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
  retry?: number;
  retryDelay?: number;
}

export interface UseAsyncCallbackResult<T = any> {
  callback: (...args: any[]) => Promise<T>;
  loading: boolean;
  error: Error | null;
  data: T | null;
  isSuccess: boolean;
  isError: boolean;
  isIdle: boolean;
}

// ============================================================================
// Debounce and Throttle Hook Types
// ============================================================================

export interface UseDebounceOptions {
  delay?: number;
  leading?: boolean;
  trailing?: boolean;
}

export interface UseDebounceResult<T> {
  value: T;
  cancel: () => void;
  flush: () => void;
}

export interface UseThrottleOptions {
  delay?: number;
  leading?: boolean;
  trailing?: boolean;
}

export interface UseThrottleResult<T> {
  value: T;
  cancel: () => void;
  flush: () => void;
}

// ============================================================================
// Event Hook Types
// ============================================================================

export interface UseEventListenerOptions {
  capture?: boolean;
  once?: boolean;
  passive?: boolean;
}

export interface UseEventListenerResult {
  addEventListener: (type: string, listener: EventListener) => void;
  removeEventListener: (type: string, listener: EventListener) => void;
}

export interface UseClickOutsideOptions {
  enabled?: boolean;
  ignore?: string[];
}

export interface UseClickOutsideResult {
  ref: React.RefObject<HTMLElement>;
  isOutside: boolean;
}

export interface UseKeyboardOptions {
  target?: 'document' | 'window' | HTMLElement;
  preventDefault?: boolean;
  stopPropagation?: boolean;
}

export interface UseKeyboardResult {
  key: string | null;
  code: string | null;
  isPressed: boolean;
  modifiers: {
    ctrl: boolean;
    shift: boolean;
    alt: boolean;
    meta: boolean;
  };
}

// ============================================================================
// Media Query Hook Types
// ============================================================================

export interface UseMediaQueryOptions {
  defaultMatches?: boolean;
  noSsr?: boolean;
}

export interface UseMediaQueryResult {
  matches: boolean;
  media: string;
}

export interface UseBreakpointOptions {
  breakpoints?: Record<string, number>;
  defaultBreakpoint?: string;
}

export interface UseBreakpointResult {
  breakpoint: string;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isLargeDesktop: boolean;
}

// ============================================================================
// Intersection Observer Hook Types
// ============================================================================

export interface UseIntersectionObserverOptions {
  threshold?: number | number[];
  root?: Element | null;
  rootMargin?: string;
  triggerOnce?: boolean;
}

export interface UseIntersectionObserverResult {
  ref: React.RefObject<HTMLElement>;
  isIntersecting: boolean;
  intersectionRatio: number;
  entry: IntersectionObserverEntry | null;
}

// ============================================================================
// WebSocket Hook Types
// ============================================================================

export interface UseWebSocketOptions {
  url: string;
  protocols?: string | string[];
  onOpen?: (event: Event) => void;
  onClose?: (event: CloseEvent) => void;
  onMessage?: (event: MessageEvent) => void;
  onError?: (event: Event) => void;
  reconnect?: boolean;
  reconnectInterval?: number;
  reconnectAttempts?: number;
}

export interface UseWebSocketResult {
  socket: WebSocket | null;
  isConnected: boolean;
  isConnecting: boolean;
  isDisconnected: boolean;
  send: (data: string | ArrayBuffer | Blob) => void;
  close: () => void;
  reconnect: () => void;
  lastMessage: MessageEvent | null;
  lastError: Event | null;
}

// ============================================================================
// Timer Hook Types
// ============================================================================

export interface UseIntervalOptions {
  delay: number | null;
  immediate?: boolean;
  onTick?: () => void;
}

export interface UseIntervalResult {
  isActive: boolean;
  start: () => void;
  stop: () => void;
  reset: () => void;
}

export interface UseTimeoutOptions {
  delay: number;
  immediate?: boolean;
  onTimeout?: () => void;
}

export interface UseTimeoutResult {
  isActive: boolean;
  start: () => void;
  stop: () => void;
  reset: () => void;
}

export interface UseCountdownOptions {
  initialCount: number;
  interval?: number;
  onComplete?: () => void;
}

export interface UseCountdownResult {
  count: number;
  isActive: boolean;
  start: () => void;
  stop: () => void;
  reset: () => void;
  isComplete: boolean;
}

// ============================================================================
// Business Logic Hook Types
// ============================================================================

export interface UseTicketsOptions {
  page?: number;
  pageSize?: number;
  filters?: Record<string, any>;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface UseTicketsResult {
  tickets: Ticket[];
  loading: boolean;
  error: Error | null;
  pagination: {
    current: number;
    pageSize: number;
    total: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
  refetch: () => Promise<void>;
  createTicket: (data: any) => Promise<Ticket>;
  updateTicket: (id: string, data: any) => Promise<Ticket>;
  deleteTicket: (id: string) => Promise<void>;
}

export interface UseWorkOrdersOptions {
  page?: number;
  pageSize?: number;
  filters?: Record<string, any>;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface UseWorkOrdersResult {
  workOrders: WorkOrder[];
  loading: boolean;
  error: Error | null;
  pagination: {
    current: number;
    pageSize: number;
    total: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
  refetch: () => Promise<void>;
  createWorkOrder: (data: any) => Promise<WorkOrder>;
  updateWorkOrder: (id: string, data: any) => Promise<WorkOrder>;
  deleteWorkOrder: (id: string) => Promise<void>;
}

export interface UseNotificationsOptions {
  page?: number;
  pageSize?: number;
  filters?: Record<string, any>;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface UseNotificationsResult {
  notifications: Notification[];
  loading: boolean;
  error: Error | null;
  unreadCount: number;
  pagination: {
    current: number;
    pageSize: number;
    total: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
  refetch: () => Promise<void>;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  deleteNotification: (id: string) => Promise<void>;
}

// ============================================================================
// Feature Flag Hook Types
// ============================================================================

export interface UseFeatureFlagOptions {
  flagName: string;
  fallback?: boolean;
}

export interface UseFeatureFlagResult {
  isEnabled: boolean;
  loading: boolean;
  error: Error | null;
  flag: {
    name: string;
    is_active: boolean;
    description: string;
    category_name: string;
  } | null;
}

export interface UseFeatureFlagsResult {
  flags: Record<string, any>;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export interface UseFeatureFlagsByCategoryOptions {
  categoryName: string;
}

export interface UseFeatureFlagsByCategoryResult {
  flags: any[];
  loading: boolean;
  error: Error | null;
}

// ============================================================================
// Search Hook Types
// ============================================================================

export interface UseSearchOptions {
  query: string;
  filters?: Record<string, any>;
  page?: number;
  pageSize?: number;
  debounceMs?: number;
}

export interface UseSearchResult<T = any> {
  results: T[];
  loading: boolean;
  error: Error | null;
  total: number;
  hasNext: boolean;
  hasPrevious: boolean;
  search: (query: string, filters?: Record<string, any>) => void;
  clear: () => void;
  loadMore: () => void;
}

// ============================================================================
// Export all types
// ============================================================================

export * from './index';
