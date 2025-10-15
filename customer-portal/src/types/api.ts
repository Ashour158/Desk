/**
 * API Type Definitions
 * 
 * This file contains type definitions for API-related functionality
 * including request/response types, error handling, and authentication.
 */

import { BaseEntity, PaginatedResponse, ApiResponse } from './index';

// ============================================================================
// Authentication Types
// ============================================================================

export interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
  expires_in: number;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
  organization_slug: string;
}

export interface RegisterResponse {
  message: string;
  user: User;
  verification_required: boolean;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  expires_in: number;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ForgotPasswordResponse {
  message: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

export interface ResetPasswordResponse {
  message: string;
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
}

export interface ChangePasswordResponse {
  message: string;
}

// ============================================================================
// User Management Types
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

export interface UpdateProfileRequest {
  first_name?: string;
  last_name?: string;
  phone?: string;
  timezone?: string;
  language?: string;
  avatar?: string;
}

export interface UpdateProfileResponse {
  user: User;
  message: string;
}

// ============================================================================
// Organization Types
// ============================================================================

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
// Ticket API Request/Response Types
// ============================================================================

export interface CreateTicketRequest {
  title: string;
  description: string;
  priority: TicketPriority;
  category_id: string;
  tags?: string[];
  attachments?: string[];
  custom_fields?: Record<string, any>;
}

export interface CreateTicketResponse {
  ticket: Ticket;
  message: string;
}

export interface UpdateTicketRequest {
  title?: string;
  description?: string;
  status?: TicketStatus;
  priority?: TicketPriority;
  category_id?: string;
  assigned_to_id?: string;
  tags?: string[];
  custom_fields?: Record<string, any>;
}

export interface UpdateTicketResponse {
  ticket: Ticket;
  message: string;
}

export interface GetTicketsRequest {
  page?: number;
  page_size?: number;
  status?: TicketStatus;
  priority?: TicketPriority;
  category_id?: string;
  assigned_to_id?: string;
  created_by_id?: string;
  search?: string;
  tags?: string[];
  created_after?: string;
  created_before?: string;
  ordering?: string;
}

export interface GetTicketsResponse {
  tickets: PaginatedResponse<Ticket>;
  filters: TicketFilters;
}

export interface TicketFilters {
  statuses: TicketStatus[];
  priorities: TicketPriority[];
  categories: TicketCategory[];
  assignees: User[];
  creators: User[];
  tags: string[];
}

export interface AddCommentRequest {
  content: string;
  is_internal?: boolean;
  mentions?: string[];
  attachments?: string[];
}

export interface AddCommentResponse {
  comment: Comment;
  message: string;
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
  certifications: Certification[];
  availability: Availability[];
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

export interface Certification {
  id: string;
  name: string;
  issuing_authority: string;
  issue_date: string;
  expiry_date?: string;
  certificate_number: string;
}

export interface Availability {
  day_of_week: number; // 0-6 (Sunday-Saturday)
  start_time: string; // HH:MM format
  end_time: string; // HH:MM format
  is_available: boolean;
}

// ============================================================================
// Work Order API Request/Response Types
// ============================================================================

export interface CreateWorkOrderRequest {
  title: string;
  description: string;
  priority: WorkOrderPriority;
  customer_id: string;
  location_id: string;
  scheduled_at: string;
  estimated_duration: number;
  equipment_ids?: string[];
  tasks?: CreateWorkOrderTaskRequest[];
  materials?: CreateMaterialRequest[];
  notes?: string;
  custom_fields?: Record<string, any>;
}

export interface CreateWorkOrderTaskRequest {
  title: string;
  description: string;
  estimated_duration: number;
}

export interface CreateMaterialRequest {
  name: string;
  quantity: number;
  unit: string;
  cost: number;
  supplier?: string;
}

export interface CreateWorkOrderResponse {
  work_order: WorkOrder;
  message: string;
}

export interface UpdateWorkOrderRequest {
  title?: string;
  description?: string;
  status?: WorkOrderStatus;
  priority?: WorkOrderPriority;
  assigned_technician_id?: string;
  scheduled_at?: string;
  estimated_duration?: number;
  actual_duration?: number;
  notes?: string;
  custom_fields?: Record<string, any>;
}

export interface UpdateWorkOrderResponse {
  work_order: WorkOrder;
  message: string;
}

export interface GetWorkOrdersRequest {
  page?: number;
  page_size?: number;
  status?: WorkOrderStatus;
  priority?: WorkOrderPriority;
  customer_id?: string;
  assigned_technician_id?: string;
  scheduled_after?: string;
  scheduled_before?: string;
  search?: string;
  ordering?: string;
}

export interface GetWorkOrdersResponse {
  work_orders: PaginatedResponse<WorkOrder>;
  filters: WorkOrderFilters;
}

export interface WorkOrderFilters {
  statuses: WorkOrderStatus[];
  priorities: WorkOrderPriority[];
  customers: Customer[];
  technicians: Technician[];
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
// Knowledge Base API Request/Response Types
// ============================================================================

export interface CreateArticleRequest {
  title: string;
  content: string;
  summary: string;
  category_id: string;
  tags?: string[];
  status?: ArticleStatus;
  attachments?: string[];
  seo_title?: string;
  seo_description?: string;
  seo_keywords?: string[];
}

export interface CreateArticleResponse {
  article: KnowledgeBaseArticle;
  message: string;
}

export interface UpdateArticleRequest {
  title?: string;
  content?: string;
  summary?: string;
  category_id?: string;
  tags?: string[];
  status?: ArticleStatus;
  attachments?: string[];
  seo_title?: string;
  seo_description?: string;
  seo_keywords?: string[];
}

export interface UpdateArticleResponse {
  article: KnowledgeBaseArticle;
  message: string;
}

export interface GetArticlesRequest {
  page?: number;
  page_size?: number;
  category_id?: string;
  status?: ArticleStatus;
  search?: string;
  tags?: string[];
  author_id?: string;
  ordering?: string;
}

export interface GetArticlesResponse {
  articles: PaginatedResponse<KnowledgeBaseArticle>;
  filters: ArticleFilters;
}

export interface ArticleFilters {
  categories: KnowledgeBaseCategory[];
  statuses: ArticleStatus[];
  authors: User[];
  tags: string[];
}

export interface VoteArticleRequest {
  helpful: boolean;
}

export interface VoteArticleResponse {
  message: string;
  votes: {
    helpful: number;
    not_helpful: number;
  };
}

// ============================================================================
// Analytics Types
// ============================================================================

export interface AnalyticsDashboard extends BaseEntity {
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
// Notification API Request/Response Types
// ============================================================================

export interface GetNotificationsRequest {
  page?: number;
  page_size?: number;
  type?: NotificationType;
  priority?: NotificationPriority;
  is_read?: boolean;
  ordering?: string;
}

export interface GetNotificationsResponse {
  notifications: PaginatedResponse<Notification>;
  unread_count: number;
}

export interface MarkNotificationReadRequest {
  notification_id: string;
}

export interface MarkNotificationReadResponse {
  message: string;
}

export interface MarkAllNotificationsReadResponse {
  message: string;
  marked_count: number;
}

// ============================================================================
// File Upload Types
// ============================================================================

export interface FileUploadRequest {
  file: File;
  category?: string;
  description?: string;
}

export interface FileUploadResponse {
  attachment: Attachment;
  message: string;
}

export interface FileUploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

// ============================================================================
// Search Types
// ============================================================================

export interface SearchRequest {
  query: string;
  type?: 'tickets' | 'work_orders' | 'articles' | 'all';
  filters?: Record<string, any>;
  page?: number;
  page_size?: number;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: string;
  filters: Record<string, any>;
}

export interface SearchResult {
  id: string;
  type: 'ticket' | 'work_order' | 'article' | 'user';
  title: string;
  description: string;
  url: string;
  score: number;
  highlights: string[];
  metadata: Record<string, any>;
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
// WebSocket Types
// ============================================================================

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

export interface WebSocketEvent {
  event: string;
  data: any;
  room?: string;
}

export interface WebSocketConnection {
  isConnected: boolean;
  reconnectAttempts: number;
  lastError?: string;
}

// ============================================================================
// Export all types
// ============================================================================

export * from './index';
