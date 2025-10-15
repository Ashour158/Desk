/**
 * TypeScript Type Definitions
 * 
 * This file contains comprehensive type definitions for the customer portal
 * to improve type safety, documentation, and developer experience.
 */

// ============================================================================
// Base Types
// ============================================================================

export interface BaseEntity {
  id: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  status: 'success' | 'error';
  errors?: string[];
}

// ============================================================================
// User and Authentication Types
// ============================================================================

export interface User extends BaseEntity {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  phone?: string;
  avatar?: string;
  timezone: string;
  language: string;
  is_verified: boolean;
  last_active_at: string;
  is_agent: boolean;
  is_customer: boolean;
  is_technician: boolean;
  role: UserRole;
  organization: Organization;
}

export type UserRole = 'admin' | 'agent' | 'customer' | 'technician';

export interface Organization extends BaseEntity {
  name: string;
  slug: string;
  domain?: string;
  settings: OrganizationSettings;
  subscription: Subscription;
}

export interface OrganizationSettings {
  timezone: string;
  language: string;
  features: FeatureFlags;
  branding: BrandingSettings;
}

export interface BrandingSettings {
  logo?: string;
  primary_color: string;
  secondary_color: string;
  custom_css?: string;
}

export interface Subscription {
  plan: 'free' | 'standard' | 'premium' | 'enterprise';
  status: 'active' | 'inactive' | 'suspended';
  expires_at?: string;
  features: string[];
}

// ============================================================================
// Feature Flags Types
// ============================================================================

export interface FeatureFlags {
  AI_ML_FEATURES: boolean;
  ADVANCED_ANALYTICS: boolean;
  REAL_TIME_NOTIFICATIONS: boolean;
  MOBILE_APP: boolean;
  IOT_INTEGRATION: boolean;
  ADVANCED_SECURITY: boolean;
  WORKFLOW_AUTOMATION: boolean;
  CUSTOMER_EXPERIENCE: boolean;
  INTEGRATION_PLATFORM: boolean;
  ADVANCED_COMMUNICATION: boolean;
}

export interface FeatureFlagContext {
  flags: Record<string, FeatureFlag>;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export interface FeatureFlag {
  name: string;
  is_active: boolean;
  description: string;
  category_name: string;
  status: 'active' | 'inactive' | 'maintenance' | 'beta';
  feature_type: 'core' | 'advanced' | 'integration' | 'automation' | 'analytics' | 'communication' | 'security' | 'mobile';
}

// ============================================================================
// Ticket Management Types
// ============================================================================

export interface Ticket extends BaseEntity {
  title: string;
  description: string;
  status: TicketStatus;
  priority: TicketPriority;
  category: TicketCategory;
  assigned_to?: User;
  created_by: User;
  organization: Organization;
  due_date?: string;
  sla_status: SLAStatus;
  tags: string[];
  attachments: Attachment[];
  comments: Comment[];
  history: TicketHistory[];
  custom_fields: Record<string, any>;
}

export type TicketStatus = 'open' | 'in_progress' | 'pending' | 'resolved' | 'closed';
export type TicketPriority = 'low' | 'medium' | 'high' | 'urgent' | 'critical';

export interface TicketCategory extends BaseEntity {
  name: string;
  description: string;
  color: string;
  icon: string;
  is_active: boolean;
  parent?: TicketCategory;
  children: TicketCategory[];
}

export interface SLAStatus {
  status: 'on_track' | 'at_risk' | 'breached' | 'no_policy';
  due_date?: string;
  time_remaining_minutes?: number;
  sla_policy?: {
    name: string;
    response_time: number;
    resolution_time: number;
  };
}

export interface Comment extends BaseEntity {
  content: string;
  author: User;
  is_internal: boolean;
  attachments: Attachment[];
  mentions: User[];
}

export interface Attachment extends BaseEntity {
  filename: string;
  file_size: number;
  mime_type: string;
  url: string;
  uploaded_by: User;
}

export interface TicketHistory extends BaseEntity {
  action: string;
  description: string;
  user: User;
  changes: Record<string, { from: any; to: any }>;
}

// ============================================================================
// Field Service Management Types
// ============================================================================

export interface WorkOrder extends BaseEntity {
  title: string;
  description: string;
  status: WorkOrderStatus;
  priority: WorkOrderPriority;
  assigned_technician?: Technician;
  customer: Customer;
  location: Location;
  scheduled_at: string;
  estimated_duration: number;
  actual_duration?: number;
  equipment: Equipment[];
  tasks: WorkOrderTask[];
  materials: Material[];
  notes: string;
  customer_signature?: string;
  photos: string[];
  custom_fields: Record<string, any>;
}

export type WorkOrderStatus = 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'on_hold';
export type WorkOrderPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface Technician extends User {
  skills: string[];
  certifications: string[];
  availability: string[];
  current_location?: Location;
  is_available: boolean;
  rating: number;
  completed_work_orders: number;
}

export interface Customer extends BaseEntity {
  name: string;
  email: string;
  phone: string;
  address: Address;
  tier: CustomerTier;
  notes: string;
  custom_fields: Record<string, any>;
}

export type CustomerTier = 'bronze' | 'silver' | 'gold' | 'platinum';

export interface Location {
  name: string;
  address: Address;
  coordinates: Coordinates;
  access_instructions?: string;
  contact_person?: string;
  contact_phone?: string;
}

export interface Address {
  street: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
}

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface Equipment extends BaseEntity {
  name: string;
  model: string;
  serial_number: string;
  manufacturer: string;
  installation_date: string;
  warranty_expires?: string;
  maintenance_schedule: MaintenanceSchedule[];
  status: EquipmentStatus;
  location: Location;
}

export type EquipmentStatus = 'operational' | 'maintenance' | 'out_of_order' | 'retired';

export interface MaintenanceSchedule {
  type: 'preventive' | 'corrective' | 'emergency';
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'annually';
  next_due: string;
  last_performed?: string;
}

export interface WorkOrderTask {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  assigned_to?: Technician;
  estimated_duration: number;
  actual_duration?: number;
  completed_at?: string;
  notes?: string;
}

export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'skipped';

export interface Material {
  id: string;
  name: string;
  quantity: number;
  unit: string;
  cost: number;
  supplier?: string;
}

// ============================================================================
// Knowledge Base Types
// ============================================================================

export interface KnowledgeBaseArticle extends BaseEntity {
  title: string;
  content: string;
  summary: string;
  category: KnowledgeBaseCategory;
  tags: string[];
  author: User;
  status: ArticleStatus;
  views: number;
  helpful_votes: number;
  not_helpful_votes: number;
  attachments: Attachment[];
  related_articles: KnowledgeBaseArticle[];
  seo_title?: string;
  seo_description?: string;
  seo_keywords?: string[];
}

export type ArticleStatus = 'draft' | 'published' | 'archived';

export interface KnowledgeBaseCategory extends BaseEntity {
  name: string;
  description: string;
  parent?: KnowledgeBaseCategory;
  children: KnowledgeBaseCategory[];
  articles_count: number;
  is_active: boolean;
}

// ============================================================================
// Analytics and Reporting Types
// ============================================================================

export interface AnalyticsDashboard {
  id: string;
  name: string;
  widgets: DashboardWidget[];
  layout: DashboardLayout;
  filters: DashboardFilter[];
  is_public: boolean;
  created_by: User;
}

export interface DashboardWidget {
  id: string;
  type: WidgetType;
  title: string;
  data_source: string;
  configuration: Record<string, any>;
  position: WidgetPosition;
  size: WidgetSize;
}

export type WidgetType = 'chart' | 'table' | 'metric' | 'gauge' | 'map' | 'timeline';

export interface WidgetPosition {
  x: number;
  y: number;
}

export interface WidgetSize {
  width: number;
  height: number;
}

export interface DashboardLayout {
  columns: number;
  rows: number;
  gap: number;
}

export interface DashboardFilter {
  field: string;
  operator: FilterOperator;
  value: any;
  label: string;
}

export type FilterOperator = 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'starts_with' | 'ends_with' | 'greater_than' | 'less_than' | 'between' | 'in' | 'not_in';

// ============================================================================
// Notification Types
// ============================================================================

export interface Notification extends BaseEntity {
  title: string;
  message: string;
  type: NotificationType;
  priority: NotificationPriority;
  user: User;
  is_read: boolean;
  read_at?: string;
  action_url?: string;
  metadata: Record<string, any>;
}

export type NotificationType = 'info' | 'success' | 'warning' | 'error' | 'system';
export type NotificationPriority = 'low' | 'medium' | 'high' | 'urgent';

// ============================================================================
// API Types
// ============================================================================

export interface ApiEndpoint {
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  path: string;
  description: string;
  parameters?: ApiParameter[];
  request_body?: ApiRequestBody;
  responses: ApiResponse[];
  authentication_required: boolean;
  rate_limit?: RateLimit;
}

export interface ApiParameter {
  name: string;
  type: string;
  required: boolean;
  description: string;
  example?: any;
}

export interface ApiRequestBody {
  content_type: string;
  schema: Record<string, any>;
  example?: any;
}

export interface ApiResponse {
  status_code: number;
  description: string;
  schema?: Record<string, any>;
  example?: any;
}

export interface RateLimit {
  requests_per_hour: number;
  burst_limit: number;
}

// ============================================================================
// Form Types
// ============================================================================

export interface FormField {
  id: string;
  name: string;
  type: FormFieldType;
  label: string;
  placeholder?: string;
  required: boolean;
  validation?: FormValidation;
  options?: FormFieldOption[];
  value?: any;
  error?: string;
}

export type FormFieldType = 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'textarea' | 'select' | 'checkbox' | 'radio' | 'date' | 'time' | 'datetime' | 'file';

export interface FormValidation {
  required?: boolean;
  min_length?: number;
  max_length?: number;
  pattern?: string;
  min?: number;
  max?: number;
  custom?: (value: any) => string | null;
}

export interface FormFieldOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface FormData {
  [key: string]: any;
}

export interface FormErrors {
  [key: string]: string;
}

// ============================================================================
// Component Props Types
// ============================================================================

export interface ComponentProps {
  className?: string;
  children?: React.ReactNode;
  id?: string;
  'data-testid'?: string;
}

export interface ButtonProps extends ComponentProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning' | 'info';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  type?: 'button' | 'submit' | 'reset';
}

export interface InputProps extends ComponentProps {
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
  value?: string;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  error?: string;
}

export interface ModalProps extends ComponentProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: 'small' | 'medium' | 'large' | 'full';
  closable?: boolean;
}

export interface TableProps<T = any> extends ComponentProps {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  pagination?: PaginationProps;
  sorting?: SortingProps;
  filtering?: FilteringProps;
  selection?: SelectionProps;
}

export interface TableColumn<T = any> {
  key: keyof T | string;
  title: string;
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: any, record: T, index: number) => React.ReactNode;
  width?: number;
  align?: 'left' | 'center' | 'right';
}

export interface PaginationProps {
  current: number;
  pageSize: number;
  total: number;
  onChange: (page: number, pageSize: number) => void;
  showSizeChanger?: boolean;
  showQuickJumper?: boolean;
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
}

// ============================================================================
// Hook Types
// ============================================================================

export interface UseApiOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
  retry?: number;
  retryDelay?: number;
}

export interface UseApiResult<T = any> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  mutate: (data: any) => Promise<void>;
}

export interface UseFormOptions<T = any> {
  initialValues?: T;
  validation?: FormValidation;
  onSubmit?: (values: T) => void | Promise<void>;
}

export interface UseFormResult<T = any> {
  values: T;
  errors: FormErrors;
  touched: Record<string, boolean>;
  setValue: (name: string, value: any) => void;
  setError: (name: string, error: string) => void;
  setTouched: (name: string, touched: boolean) => void;
  handleSubmit: (event?: React.FormEvent) => void;
  reset: () => void;
  isValid: boolean;
  isSubmitting: boolean;
}

// ============================================================================
// Utility Types
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
// Configuration Types
// ============================================================================

export interface AppConfig {
  api: {
    baseUrl: string;
    timeout: number;
    retries: number;
  };
  features: FeatureFlags;
  theme: {
    primaryColor: string;
    secondaryColor: string;
    mode: 'light' | 'dark' | 'auto';
  };
  notifications: {
    enabled: boolean;
    types: NotificationType[];
  };
  analytics: {
    enabled: boolean;
    trackingId?: string;
  };
}

export interface EnvironmentConfig {
  NODE_ENV: 'development' | 'production' | 'test';
  REACT_APP_API_URL: string;
  REACT_APP_WS_URL: string;
  REACT_APP_ANALYTICS_ID?: string;
  REACT_APP_SENTRY_DSN?: string;
}

// ============================================================================
// Error Types
// ============================================================================

export interface ApiError {
  message: string;
  code: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface NetworkError {
  message: string;
  status?: number;
  statusText?: string;
}

// ============================================================================
// Export all types
// ============================================================================

export * from './api';
export * from './components';
export * from './hooks';
export * from './utils';