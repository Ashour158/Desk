/**
 * Component Type Definitions
 * 
 * This file contains type definitions for React components
 * including props, state, and event handlers.
 */

import React from 'react';
import { BaseEntity, User, Ticket, WorkOrder, Notification } from './index';

// ============================================================================
// Base Component Types
// ============================================================================

export interface ComponentProps {
  className?: string;
  children?: React.ReactNode;
  id?: string;
  'data-testid'?: string;
  style?: React.CSSProperties;
}

export interface StyledComponentProps extends ComponentProps {
  variant?: string;
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';
}

// ============================================================================
// Button Component Types
// ============================================================================

export interface ButtonProps extends ComponentProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning' | 'info' | 'ghost' | 'link';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  type?: 'button' | 'submit' | 'reset';
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  href?: string;
  target?: string;
  rel?: string;
}

export interface ButtonGroupProps extends ComponentProps {
  orientation?: 'horizontal' | 'vertical';
  spacing?: 'none' | 'small' | 'medium' | 'large';
  children: React.ReactElement<ButtonProps>[];
}

// ============================================================================
// Input Component Types
// ============================================================================

export interface InputProps extends ComponentProps {
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search';
  value?: string;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  onFocus?: (event: React.FocusEvent<HTMLInputElement>) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  label?: string;
  helperText?: string;
  prefix?: React.ReactNode;
  suffix?: React.ReactNode;
  size?: 'small' | 'medium' | 'large';
  variant?: 'outlined' | 'filled' | 'underlined';
}

export interface TextAreaProps extends ComponentProps {
  value?: string;
  onChange?: (event: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onBlur?: (event: React.FocusEvent<HTMLTextAreaElement>) => void;
  onFocus?: (event: React.FocusEvent<HTMLTextAreaElement>) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  label?: string;
  helperText?: string;
  rows?: number;
  cols?: number;
  resize?: 'none' | 'both' | 'horizontal' | 'vertical';
  size?: 'small' | 'medium' | 'large';
  variant?: 'outlined' | 'filled' | 'underlined';
}

export interface SelectProps extends ComponentProps {
  value?: string | string[];
  onChange?: (value: string | string[]) => void;
  options: SelectOption[];
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  label?: string;
  helperText?: string;
  multiple?: boolean;
  searchable?: boolean;
  clearable?: boolean;
  size?: 'small' | 'medium' | 'large';
  variant?: 'outlined' | 'filled' | 'underlined';
}

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
  group?: string;
}

export interface CheckboxProps extends ComponentProps {
  checked?: boolean;
  onChange?: (checked: boolean) => void;
  label?: string;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';
}

export interface RadioProps extends ComponentProps {
  value?: string;
  onChange?: (value: string) => void;
  options: RadioOption[];
  name: string;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  label?: string;
  helperText?: string;
  orientation?: 'horizontal' | 'vertical';
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';
}

export interface RadioOption {
  value: string;
  label: string;
  disabled?: boolean;
}

// ============================================================================
// Form Component Types
// ============================================================================

export interface FormProps extends ComponentProps {
  onSubmit?: (values: Record<string, any>) => void | Promise<void>;
  initialValues?: Record<string, any>;
  validation?: FormValidation;
  children: React.ReactNode;
}

export interface FormFieldProps extends ComponentProps {
  name: string;
  label?: string;
  required?: boolean;
  error?: string;
  helperText?: string;
  children: React.ReactElement;
}

export interface FormValidation {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
  min?: number;
  max?: number;
  custom?: (value: any) => string | null;
}

export interface FormErrors {
  [key: string]: string;
}

// ============================================================================
// Modal Component Types
// ============================================================================

export interface ModalProps extends ComponentProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: 'small' | 'medium' | 'large' | 'full';
  closable?: boolean;
  maskClosable?: boolean;
  centered?: boolean;
  footer?: React.ReactNode;
  destroyOnClose?: boolean;
  zIndex?: number;
}

export interface ConfirmModalProps extends ModalProps {
  onConfirm: () => void | Promise<void>;
  onCancel?: () => void;
  confirmText?: string;
  cancelText?: string;
  confirmLoading?: boolean;
  danger?: boolean;
}

export interface DrawerProps extends ComponentProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  placement?: 'left' | 'right' | 'top' | 'bottom';
  size?: 'small' | 'medium' | 'large' | 'full';
  closable?: boolean;
  maskClosable?: boolean;
  footer?: React.ReactNode;
  destroyOnClose?: boolean;
  zIndex?: number;
}

// ============================================================================
// Table Component Types
// ============================================================================

export interface TableProps<T = any> extends ComponentProps {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  pagination?: PaginationProps;
  sorting?: SortingProps;
  filtering?: FilteringProps;
  selection?: SelectionProps;
  rowKey?: keyof T | ((record: T) => string);
  onRow?: (record: T, index: number) => RowProps;
  emptyText?: string;
  size?: 'small' | 'medium' | 'large';
  bordered?: boolean;
  striped?: boolean;
  hoverable?: boolean;
}

export interface TableColumn<T = any> {
  key: keyof T | string;
  title: string;
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: any, record: T, index: number) => React.ReactNode;
  width?: number;
  align?: 'left' | 'center' | 'right';
  fixed?: 'left' | 'right';
  ellipsis?: boolean;
  sorter?: (a: T, b: T) => number;
  filters?: TableFilter[];
  onFilter?: (value: any, record: T) => boolean;
}

export interface TableFilter {
  text: string;
  value: any;
}

export interface RowProps {
  onClick?: (event: React.MouseEvent<HTMLTableRowElement>) => void;
  onDoubleClick?: (event: React.MouseEvent<HTMLTableRowElement>) => void;
  className?: string;
  style?: React.CSSProperties;
}

export interface PaginationProps {
  current: number;
  pageSize: number;
  total: number;
  onChange: (page: number, pageSize: number) => void;
  showSizeChanger?: boolean;
  showQuickJumper?: boolean;
  showTotal?: (total: number, range: [number, number]) => React.ReactNode;
  pageSizeOptions?: number[];
  size?: 'small' | 'default';
  simple?: boolean;
}

export interface SortingProps {
  field?: string;
  order?: 'asc' | 'desc';
  onChange: (field: string, order: 'asc' | 'desc') => void;
}

export interface FilteringProps {
  filters: Record<string, any>;
  onChange: (filters: Record<string, any>) => void;
}

export interface SelectionProps {
  selectedRowKeys: string[];
  onChange: (selectedRowKeys: string[]) => void;
  getCheckboxProps?: (record: any) => { disabled?: boolean };
  type?: 'checkbox' | 'radio';
}

// ============================================================================
// Card Component Types
// ============================================================================

export interface CardProps extends ComponentProps {
  title?: string;
  subtitle?: string;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  actions?: React.ReactNode;
  loading?: boolean;
  hoverable?: boolean;
  bordered?: boolean;
  shadow?: 'none' | 'small' | 'medium' | 'large';
  size?: 'small' | 'medium' | 'large';
}

export interface CardHeaderProps extends ComponentProps {
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export interface CardBodyProps extends ComponentProps {
  padding?: 'none' | 'small' | 'medium' | 'large';
}

export interface CardFooterProps extends ComponentProps {
  actions?: React.ReactNode;
  align?: 'left' | 'center' | 'right';
}

// ============================================================================
// Layout Component Types
// ============================================================================

export interface LayoutProps extends ComponentProps {
  direction?: 'horizontal' | 'vertical';
  wrap?: boolean;
  justify?: 'start' | 'end' | 'center' | 'between' | 'around' | 'evenly';
  align?: 'start' | 'end' | 'center' | 'baseline' | 'stretch';
  gap?: 'none' | 'small' | 'medium' | 'large';
  children: React.ReactNode;
}

export interface ContainerProps extends ComponentProps {
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
  padding?: 'none' | 'small' | 'medium' | 'large';
  center?: boolean;
  children: React.ReactNode;
}

export interface GridProps extends ComponentProps {
  columns?: number;
  gap?: 'none' | 'small' | 'medium' | 'large';
  children: React.ReactNode;
}

export interface GridItemProps extends ComponentProps {
  span?: number;
  offset?: number;
  order?: number;
  children: React.ReactNode;
}

export interface StackProps extends ComponentProps {
  direction?: 'row' | 'column';
  spacing?: 'none' | 'small' | 'medium' | 'large';
  align?: 'start' | 'end' | 'center' | 'baseline' | 'stretch';
  justify?: 'start' | 'end' | 'center' | 'between' | 'around' | 'evenly';
  wrap?: boolean;
  children: React.ReactNode;
}

// ============================================================================
// Navigation Component Types
// ============================================================================

export interface NavProps extends ComponentProps {
  items: NavItem[];
  activeKey?: string;
  onSelect?: (key: string) => void;
  orientation?: 'horizontal' | 'vertical';
  size?: 'small' | 'medium' | 'large';
  variant?: 'default' | 'pills' | 'tabs';
}

export interface NavItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
  disabled?: boolean;
  children?: NavItem[];
}

export interface BreadcrumbProps extends ComponentProps {
  items: BreadcrumbItem[];
  separator?: React.ReactNode;
  maxItems?: number;
}

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: React.ReactNode;
}

export interface MenuProps extends ComponentProps {
  items: MenuItem[];
  activeKey?: string;
  onSelect?: (key: string) => void;
  mode?: 'horizontal' | 'vertical' | 'inline';
  theme?: 'light' | 'dark';
  size?: 'small' | 'medium' | 'large';
}

export interface MenuItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
  disabled?: boolean;
  children?: MenuItem[];
  type?: 'item' | 'divider' | 'group';
}

// ============================================================================
// Data Display Component Types
// ============================================================================

export interface BadgeProps extends ComponentProps {
  count?: number;
  maxCount?: number;
  showZero?: boolean;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'small' | 'medium' | 'large';
  variant?: 'solid' | 'outline' | 'soft';
}

export interface TagProps extends ComponentProps {
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  size?: 'small' | 'medium' | 'large';
  variant?: 'solid' | 'outline' | 'soft';
  closable?: boolean;
  onClose?: () => void;
}

export interface AvatarProps extends ComponentProps {
  src?: string;
  alt?: string;
  size?: 'small' | 'medium' | 'large' | number;
  shape?: 'circle' | 'square';
  fallback?: React.ReactNode;
  status?: 'online' | 'offline' | 'away' | 'busy';
}

export interface TooltipProps extends ComponentProps {
  title: string;
  placement?: 'top' | 'bottom' | 'left' | 'right';
  trigger?: 'hover' | 'focus' | 'click';
  arrow?: boolean;
  delay?: number;
  children: React.ReactElement;
}

export interface PopoverProps extends ComponentProps {
  content: React.ReactNode;
  title?: string;
  placement?: 'top' | 'bottom' | 'left' | 'right';
  trigger?: 'hover' | 'focus' | 'click';
  arrow?: boolean;
  children: React.ReactElement;
}

// ============================================================================
// Feedback Component Types
// ============================================================================

export interface AlertProps extends ComponentProps {
  type?: 'success' | 'warning' | 'error' | 'info';
  title?: string;
  description?: string;
  closable?: boolean;
  onClose?: () => void;
  showIcon?: boolean;
  action?: React.ReactNode;
}

export interface ToastProps extends ComponentProps {
  type?: 'success' | 'warning' | 'error' | 'info';
  title?: string;
  description?: string;
  duration?: number;
  closable?: boolean;
  onClose?: () => void;
  action?: React.ReactNode;
}

export interface SpinnerProps extends ComponentProps {
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';
  speed?: 'slow' | 'normal' | 'fast';
}

export interface SkeletonProps extends ComponentProps {
  width?: string | number;
  height?: string | number;
  variant?: 'text' | 'rectangular' | 'circular';
  animation?: 'pulse' | 'wave' | 'none';
  lines?: number;
}

// ============================================================================
// Data Entry Component Types
// ============================================================================

export interface DatePickerProps extends ComponentProps {
  value?: Date;
  onChange?: (date: Date | null) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  label?: string;
  helperText?: string;
  format?: string;
  showTime?: boolean;
  timeFormat?: string;
  minDate?: Date;
  maxDate?: Date;
  size?: 'small' | 'medium' | 'large';
  variant?: 'outlined' | 'filled' | 'underlined';
}

export interface TimePickerProps extends ComponentProps {
  value?: Date;
  onChange?: (date: Date | null) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  label?: string;
  helperText?: string;
  format?: string;
  minTime?: Date;
  maxTime?: Date;
  size?: 'small' | 'medium' | 'large';
  variant?: 'outlined' | 'filled' | 'underlined';
}

export interface FileUploadProps extends ComponentProps {
  accept?: string;
  multiple?: boolean;
  maxSize?: number;
  maxFiles?: number;
  onUpload?: (files: File[]) => void;
  onProgress?: (progress: number) => void;
  onError?: (error: string) => void;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  label?: string;
  helperText?: string;
  size?: 'small' | 'medium' | 'large';
  variant?: 'outlined' | 'filled' | 'underlined';
}

export interface SwitchProps extends ComponentProps {
  checked?: boolean;
  onChange?: (checked: boolean) => void;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  label?: string;
  helperText?: string;
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';
}

// ============================================================================
// Business Component Types
// ============================================================================

export interface TicketCardProps extends ComponentProps {
  ticket: Ticket;
  onEdit?: (ticket: Ticket) => void;
  onDelete?: (ticket: Ticket) => void;
  onStatusChange?: (ticket: Ticket, status: string) => void;
  onPriorityChange?: (ticket: Ticket, priority: string) => void;
  onAssign?: (ticket: Ticket, user: User) => void;
  showActions?: boolean;
  compact?: boolean;
}

export interface WorkOrderCardProps extends ComponentProps {
  workOrder: WorkOrder;
  onEdit?: (workOrder: WorkOrder) => void;
  onDelete?: (workOrder: WorkOrder) => void;
  onStatusChange?: (workOrder: WorkOrder, status: string) => void;
  onAssign?: (workOrder: WorkOrder, technician: User) => void;
  showActions?: boolean;
  compact?: boolean;
}

export interface NotificationItemProps extends ComponentProps {
  notification: Notification;
  onRead?: (notification: Notification) => void;
  onDelete?: (notification: Notification) => void;
  onAction?: (notification: Notification) => void;
  showActions?: boolean;
  compact?: boolean;
}

export interface UserCardProps extends ComponentProps {
  user: User;
  onEdit?: (user: User) => void;
  onDelete?: (user: User) => void;
  onRoleChange?: (user: User, role: string) => void;
  showActions?: boolean;
  compact?: boolean;
}

// ============================================================================
// Export all types
// ============================================================================

export * from './index';
