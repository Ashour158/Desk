# Database Model Relationship Diagram

## Core Entity Relationships

```mermaid
erDiagram
    Organization ||--o{ User : "has users"
    Organization ||--o{ Ticket : "has tickets"
    Organization ||--o{ Department : "has departments"
    Organization ||--o{ Customer : "has customers"
    Organization ||--o{ WorkOrder : "has work orders"
    Organization ||--o{ KBArticle : "has articles"
    Organization ||--o{ AutomationRule : "has rules"
    Organization ||--o{ SLAPolicy : "has policies"

    User ||--o{ Ticket : "customer_tickets"
    User ||--o{ Ticket : "assigned_tickets"
    User ||--o{ Ticket : "created_tickets"
    User ||--o{ TicketComment : "ticket_comments"
    User ||--o{ TicketAttachment : "ticket_attachments"
    User ||--o{ UserSession : "has sessions"
    User ||--o{ UserPermission : "has permissions"
    User ||--o{ WorkOrder : "assigned work orders"
    User ||--o{ Technician : "is technician"

    Ticket ||--o{ TicketComment : "has comments"
    Ticket ||--o{ TicketAttachment : "has attachments"
    Ticket ||--o{ TicketHistory : "has history"
    Ticket }o--|| SLAPolicy : "follows SLA"

    TicketComment ||--o{ TicketAttachment : "has attachments"

    Department ||--o{ User : "has manager"
    Department ||--o{ User : "has members"

    WorkOrder ||--o{ JobAssignment : "has assignments"
    Technician ||--o{ JobAssignment : "assigned to"

    KBArticle }o--|| KBCategory : "belongs to category"
    KBArticle ||--o{ KBArticleView : "has views"

    Organization {
        int id PK
        string name
        string slug UK
        string domain
        string subscription_tier
        json settings
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    User {
        int id PK
        int organization_id FK
        string email UK
        string username UK
        string first_name
        string last_name
        string role
        string customer_tier
        string phone
        string timezone
        string language
        boolean two_factor_enabled
        json skills
        json certifications
        int max_concurrent_tickets
        string availability_status
        boolean email_notifications
        boolean sms_notifications
        boolean push_notifications
        datetime created_at
        datetime updated_at
    }

    Ticket {
        int id PK
        int organization_id FK
        string ticket_number UK
        string subject
        text description
        string status
        string priority
        string channel
        string source
        int customer_id FK
        int assigned_agent_id FK
        int created_by_id FK
        int sla_policy_id FK
        datetime first_response_due
        datetime resolution_due
        datetime first_response_at
        datetime resolved_at
        boolean sla_breach
        string category
        string subcategory
        json tags
        json custom_fields
        datetime created_at
        datetime updated_at
        datetime closed_at
        interval time_to_first_response
        interval time_to_resolution
        int customer_satisfaction_score
    }

    TicketComment {
        int id PK
        int ticket_id FK
        int author_id FK
        text content
        string comment_type
        boolean has_attachments
        datetime created_at
        datetime updated_at
    }

    TicketAttachment {
        int id PK
        int ticket_id FK
        int comment_id FK
        int uploaded_by_id FK
        string file_name
        bigint file_size
        string file_type
        string file_path
        string file_url
        boolean is_public
        int download_count
        datetime uploaded_at
    }

    TicketHistory {
        int id PK
        int ticket_id FK
        int user_id FK
        string field_name
        text old_value
        text new_value
        string change_type
        json changes
        string ip_address
        text user_agent
        datetime created_at
    }

    Department {
        int id PK
        int organization_id FK
        string name
        text description
        int manager_id FK
        boolean is_active
        datetime created_at
    }

    Customer {
        int id PK
        int user_id FK
        int organization_id FK
        string company
        string phone
        decimal lifetime_value
        json tags
        datetime created_at
        datetime updated_at
    }

    WorkOrder {
        int id PK
        int organization_id FK
        string work_order_number UK
        string title
        text description
        string status
        string priority
        int technician_id FK
        int customer_id FK
        int created_by_id FK
        datetime scheduled_at
        datetime completed_at
        json location
        json custom_fields
        datetime created_at
        datetime updated_at
    }

    Technician {
        int id PK
        int organization_id FK
        int user_id FK
        string employee_id
        json skills
        json certifications
        string availability_status
        int max_jobs_per_day
        int current_jobs_count
        json service_areas
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    JobAssignment {
        int id PK
        int work_order_id FK
        int technician_id FK
        string status
        datetime assigned_at
        datetime started_at
        datetime completed_at
        text notes
        datetime created_at
        datetime updated_at
    }

    KBCategory {
        int id PK
        int organization_id FK
        string name
        text description
        int parent_id FK
        int sort_order
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    KBArticle {
        int id PK
        int organization_id FK
        int category_id FK
        string title
        text content
        string status
        json tags
        boolean is_published
        int view_count
        int helpful_count
        int not_helpful_count
        datetime published_at
        datetime created_at
        datetime updated_at
    }

    KBArticleView {
        int id PK
        int article_id FK
        int user_id FK
        string ip_address
        text user_agent
        datetime created_at
    }

    AutomationRule {
        int id PK
        int organization_id FK
        string name
        text description
        string trigger_type
        json trigger_conditions
        json actions
        int execution_order
        boolean is_active
        boolean stop_on_match
        int execution_count
        int success_count
        int failure_count
        float average_execution_time
        datetime created_at
        datetime updated_at
    }

    SLAPolicy {
        int id PK
        int organization_id FK
        string name
        text description
        int first_response_hours
        int resolution_hours
        json escalation_rules
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    UserSession {
        int id PK
        int user_id FK
        string session_key UK
        string ip_address
        text user_agent
        datetime created_at
        datetime last_activity
        boolean is_active
    }

    UserPermission {
        int id PK
        int user_id FK
        string permission
        int granted_by_id FK
        datetime granted_at
        datetime expires_at
        boolean is_active
    }
```

## Multi-Tenant Architecture

```mermaid
graph TD
    A[Organization] --> B[TenantAwareModel]
    B --> C[Ticket]
    B --> D[WorkOrder]
    B --> E[KBArticle]
    B --> F[AutomationRule]
    B --> G[Technician]
    B --> H[SLAPolicy]
    
    I[User] --> J[Authentication]
    I --> K[Authorization]
    I --> L[Profile Management]
    
    M[Ticket] --> N[TicketComment]
    M --> O[TicketAttachment]
    M --> P[TicketHistory]
    
    Q[WorkOrder] --> R[JobAssignment]
    S[Technician] --> R
    
    T[KBArticle] --> U[KBCategory]
    T --> V[KBArticleView]
    
    W[Organization] --> X[Department]
    W --> Y[Customer]
    
    Z[User] --> AA[UserSession]
    Z --> BB[UserPermission]
```

## Model Inheritance Hierarchy

```mermaid
graph TD
    A[models.Model] --> B[TenantAwareModel]
    A --> C[TimestampedModel]
    A --> D[NamedModel]
    A --> E[StatusModel]
    A --> F[ActiveModel]
    
    B --> G[Ticket]
    B --> H[WorkOrder]
    B --> I[KBArticle]
    B --> J[AutomationRule]
    B --> K[Technician]
    B --> L[SLAPolicy]
    
    C --> M[User]
    C --> N[Organization]
    C --> O[Department]
    
    F --> P[Organization]
    F --> Q[Department]
    F --> R[Technician]
    
    S[AbstractUser] --> M
    T[BaseModel] --> U[Combines all base models]
```

## Data Flow Relationships

```mermaid
graph LR
    A[Organization] --> B[User]
    A --> C[Ticket]
    A --> D[WorkOrder]
    A --> E[KBArticle]
    
    B --> C
    B --> D
    B --> F[TicketComment]
    B --> G[TicketAttachment]
    B --> H[UserSession]
    B --> I[UserPermission]
    
    C --> F
    C --> G
    C --> J[TicketHistory]
    
    D --> K[JobAssignment]
    L[Technician] --> K
    
    E --> M[KBCategory]
    E --> N[KBArticleView]
    
    O[SLAPolicy] --> C
    P[AutomationRule] --> C
    P --> D
```

## Validation and Hooks Flow

```mermaid
graph TD
    A[Model Save] --> B[ModelValidationMixin.save]
    B --> C[full_clean]
    C --> D[DataIntegrityValidator]
    D --> E[validate_ticket_data]
    D --> F[validate_user_data]
    D --> G[validate_comment_data]
    
    H[TenantAwareModel.save] --> I[Auto-set organization]
    J[Ticket.save] --> K[Generate ticket number]
    
    L[Model Clean] --> M[ModelValidationMixin.clean]
    M --> N[DataIntegrityValidator]
    
    O[Business Logic] --> P[calculate_sla_metrics]
    O --> Q[update_last_active]
    O --> R[soft_delete]
    O --> S[restore]
```

## Soft Delete Implementation

```mermaid
graph TD
    A[ActiveModel] --> B[is_active field]
    C[StatusModel] --> D[status field]
    D --> E[STATUS_ACTIVE]
    D --> F[STATUS_INACTIVE]
    D --> G[STATUS_DELETED]
    
    H[Organization] --> I[soft_delete method]
    H --> J[restore method]
    
    K[User] --> L[soft_delete method]
    K --> M[restore method]
    
    N[DataRetentionPolicy] --> O[retention_period_days]
    N --> P[archive_before_delete]
    N --> Q[anonymize_personal_data]
```

## Security and Access Control

```mermaid
graph TD
    A[User Role] --> B[admin]
    A --> C[manager]
    A --> D[agent]
    A --> E[customer]
    
    F[limit_choices_to] --> G[role: customer]
    F --> H[role__in: admin, manager, agent]
    
    I[Organization] --> J[Multi-tenant isolation]
    K[User] --> L[Role-based access]
    M[Ticket] --> N[Customer can only see own tickets]
    M --> O[Agent can see assigned tickets]
    M --> P[Admin can see all tickets]
    
    Q[UserSession] --> R[Session management]
    S[UserPermission] --> T[Custom permissions]
    U[DataRetentionPolicy] --> V[Data lifecycle management]
```

This comprehensive model relationship diagram shows:

1. **Core Entity Relationships:** How all models connect
2. **Multi-Tenant Architecture:** Organization-based isolation
3. **Model Inheritance:** Base model hierarchy
4. **Data Flow:** How data flows between entities
5. **Validation and Hooks:** Model lifecycle management
6. **Soft Delete Implementation:** Data retention patterns
7. **Security and Access Control:** Role-based permissions

The database model architecture is well-designed with proper relationships, validation, and security controls! 🎉
