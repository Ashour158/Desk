# Complete API Endpoint Inventory

## Overview
This document provides a comprehensive inventory of all API endpoints in the helpdesk platform, organized by feature and functionality.

---

## Authentication Endpoints

### Base Path: `/api/v1/users/`

| Method | Endpoint | Description | Auth Required | Permissions | Request Body | Response Schema | Status Codes |
|--------|----------|-------------|---------------|-------------|--------------|-----------------|--------------|
| POST | `/login/` | Obtain JWT tokens | No | None | `{email, password}` | `{access, refresh}` | 200, 400, 401 |
| POST | `/refresh/` | Refresh access token | No | None | `{refresh}` | `{access}` | 200, 400, 401 |
| POST | `/verify/` | Verify token validity | No | None | `{token}` | `{valid}` | 200, 400, 401 |
| POST | `/register/` | User registration | No | None | `{email, username, password, first_name, last_name, phone, organization_slug}` | `{message, user}` | 201, 400, 409 |
| GET | `/profile/` | Get user profile | Yes | Authenticated | None | `{id, email, username, full_name, role, phone, avatar, timezone, language, is_verified, last_active_at, is_agent, is_customer, is_technician, created_at, updated_at}` | 200, 401 |
| PUT | `/profile/` | Update user profile | Yes | Authenticated | `{first_name, last_name, phone, timezone, language}` | `{id, email, username, full_name, role, phone, avatar, timezone, language, is_verified, last_active_at, is_agent, is_customer, is_technician, created_at, updated_at}` | 200, 400, 401 |
| POST | `/change-password/` | Change password | Yes | Authenticated | `{old_password, new_password}` | `{message}` | 200, 400, 401 |
| POST | `/password-reset/` | Request password reset | No | None | `{email}` | `{message}` | 200, 400 |
| POST | `/password-reset-confirm/` | Confirm password reset | No | None | `{token, new_password}` | `{message}` | 200, 400, 401 |
| POST | `/2fa/setup/` | Setup 2FA | Yes | Authenticated | `{device_name}` | `{qr_code, secret_key, backup_codes}` | 200, 400, 401 |
| POST | `/2fa/verify/` | Verify 2FA | Yes | Authenticated | `{token}` | `{valid}` | 200, 400, 401 |
| POST | `/2fa/disable/` | Disable 2FA | Yes | Authenticated | `{password}` | `{message}` | 200, 400, 401 |

---

## Organization Management

### Base Path: `/api/v1/organizations/`

| Method | Endpoint | Description | Auth Required | Permissions | Request Body | Response Schema | Status Codes |
|--------|----------|-------------|---------------|-------------|--------------|-----------------|--------------|
| GET | `/` | List organizations | Yes | Authenticated | None | `{count, next, previous, results: [{id, name, slug, domain, subscription_tier, settings, is_active, created_at, updated_at}]}` | 200, 401 |
| POST | `/` | Create organization | Yes | Admin | `{name, domain, subscription_tier, settings}` | `{id, name, slug, domain, subscription_tier, settings, is_active, created_at, updated_at}` | 201, 400, 401, 403 |
| GET | `/{id}/` | Get organization | Yes | Authenticated | None | `{id, name, slug, domain, subscription_tier, settings, is_active, created_at, updated_at}` | 200, 401, 404 |
| PUT | `/{id}/` | Update organization | Yes | Admin | `{name, domain, subscription_tier, settings}` | `{id, name, slug, domain, subscription_tier, settings, is_active, created_at, updated_at}` | 200, 400, 401, 403, 404 |
| DELETE | `/{id}/` | Delete organization | Yes | Admin | None | `{message}` | 204, 401, 403, 404 |

---

## Ticket Management

### Base Path: `/api/v1/tickets/`

| Method | Endpoint | Description | Auth Required | Permissions | Request Body | Response Schema | Status Codes |
|--------|----------|-------------|---------------|-------------|--------------|-----------------|--------------|
| GET | `/` | List tickets | Yes | Authenticated | None | `{count, next, previous, results: [{id, ticket_number, subject, description, status, priority, customer, assigned_agent, organization, tags, attachments, comments, created_at, updated_at}]}` | 200, 401 |
| POST | `/` | Create ticket | Yes | Authenticated | `{subject, description, priority, tags, attachments}` | `{id, ticket_number, subject, description, status, priority, customer, assigned_agent, organization, tags, attachments, comments, created_at, updated_at}` | 201, 400, 401 |
| GET | `/{id}/` | Get ticket | Yes | Authenticated | None | `{id, ticket_number, subject, description, status, priority, customer, assigned_agent, organization, tags, attachments, comments, created_at, updated_at}` | 200, 401, 404 |
| PUT | `/{id}/` | Update ticket | Yes | Agent/Admin | `{subject, description, status, priority, assigned_agent, tags}` | `{id, ticket_number, subject, description, status, priority, customer, assigned_agent, organization, tags, attachments, comments, created_at, updated_at}` | 200, 400, 401, 403, 404 |
| DELETE | `/{id}/` | Delete ticket | Yes | Admin | None | `{message}` | 204, 401, 403, 404 |
| GET | `/{id}/comments/` | Get ticket comments | Yes | Authenticated | None | `{count, next, previous, results: [{id, content, author, is_internal, created_at}]}` | 200, 401, 404 |
| POST | `/{id}/comments/` | Add comment | Yes | Authenticated | `{content, is_internal}` | `{id, content, author, is_internal, created_at}` | 201, 400, 401, 404 |
| GET | `/statistics/` | Get ticket statistics | Yes | Agent/Admin | None | `{total_tickets, open_tickets, pending_tickets, resolved_tickets, closed_tickets, average_resolution_time, sla_compliance, priority_distribution, status_distribution}` | 200, 401, 403 |

---

## Knowledge Base

### Base Path: `/api/v1/knowledge-base/`

| Method | Endpoint | Description | Auth Required | Permissions | Request Body | Response Schema | Status Codes |
|--------|----------|-------------|---------------|-------------|--------------|-----------------|--------------|
| GET | `/articles/` | List articles | Yes | Authenticated | None | `{count, next, previous, results: [{id, title, content, category, author, tags, status, views, helpful_votes, not_helpful_votes, created_at, updated_at}]}` | 200, 401 |
| POST | `/articles/` | Create article | Yes | Agent/Admin | `{title, content, category, tags, status}` | `{id, title, content, category, author, tags, status, views, helpful_votes, not_helpful_votes, created_at, updated_at}` | 201, 400, 401, 403 |
| GET | `/articles/{id}/` | Get article | Yes | Authenticated | None | `{id, title, content, category, author, tags, status, views, helpful_votes, not_helpful_votes, created_at, updated_at}` | 200, 401, 404 |
| PUT | `/articles/{id}/` | Update article | Yes | Agent/Admin | `{title, content, category, tags, status}` | `{id, title, content, category, author, tags, status, views, helpful_votes, not_helpful_votes, created_at, updated_at}` | 200, 400, 401, 403, 404 |
| DELETE | `/articles/{id}/` | Delete article | Yes | Admin | None | `{message}` | 204, 401, 403, 404 |
| GET | `/categories/` | List categories | Yes | Authenticated | None | `{count, next, previous, results: [{id, name, description, parent_category, subcategories, article_count, created_at, updated_at}]}` | 200, 401 |
| POST | `/categories/` | Create category | Yes | Agent/Admin | `{name, description, parent_category}` | `{id, name, description, parent_category, subcategories, article_count, created_at, updated_at}` | 201, 400, 401, 403 |

---

## Field Service Management

### Base Path: `/api/v1/work-orders/`

| Method | Endpoint | Description | Auth Required | Permissions | Request Body | Response Schema | Status Codes |
|--------|----------|-------------|---------------|-------------|--------------|-----------------|--------------|
| GET | `/` | List work orders | Yes | Authenticated | None | `{count, next, previous, results: [{id, work_order_number, title, description, status, priority, customer, technician, scheduled_date, completed_date, location, created_at, updated_at}]}` | 200, 401 |
| POST | `/` | Create work order | Yes | Agent/Admin | `{title, description, customer, technician, scheduled_date, priority, location}` | `{id, work_order_number, title, description, status, priority, customer, technician, scheduled_date, completed_date, location, created_at, updated_at}` | 201, 400, 401, 403 |
| GET | `/{id}/` | Get work order | Yes | Authenticated | None | `{id, work_order_number, title, description, status, priority, customer, technician, scheduled_date, completed_date, location, created_at, updated_at}` | 200, 401, 404 |
| PUT | `/{id}/` | Update work order | Yes | Agent/Admin | `{title, description, status, priority, technician, scheduled_date, location}` | `{id, work_order_number, title, description, status, priority, customer, technician, scheduled_date, completed_date, location, created_at, updated_at}` | 200, 400, 401, 403, 404 |
| DELETE | `/{id}/` | Delete work order | Yes | Admin | None | `{message}` | 204, 401, 403, 404 |

### Base Path: `/api/v1/technicians/`

| Method | Endpoint | Description | Auth Required | Permissions | Request Body | Response Schema | Status Codes |
|--------|----------|-------------|---------------|-------------|--------------|-----------------|--------------|
| GET | `/` | List technicians | Yes | Authenticated | None | `{count, next, previous, results: [{id, user, specializations, certifications, availability, is_active, created_at, updated_at}]}` | 200, 401 |
| POST | `/` | Create technician | Yes | Admin | `{user, specializations, certifications, availability}` | `{id, user, specializations, certifications, availability, is_active, created_at, updated_at}` | 201, 400, 401, 403 |
| GET | `/{id}/` | Get technician | Yes | Authenticated | None | `{id, user, specializations, certifications, availability, is_active, created_at, updated_at}` | 200, 401, 404 |
| PUT | `/{id}/` | Update technician | Yes | Admin | `{specializations, certifications, availability, is_active}` | `{id, user, specializations, certifications, availability, is_active, created_at, updated_at}` | 200, 400, 401, 403, 404 |
| DELETE | `/{id}/` | Delete technician | Yes | Admin | None | `{message}` | 204, 401, 403, 404 |

---

## AI/ML Features

### Base Path: `/api/v1/ai-ml/`

| Method | Endpoint | Description | Auth Required | Permissions | Request Body | Response Schema | Status Codes |
|--------|----------|-------------|---------------|-------------|--------------|-----------------|--------------|
| POST | `/categorize-ticket/` | Categorize ticket | Yes | Authenticated | `{ticket_id, subject, description}` | `{category, confidence, suggested_tags, priority_suggestion}` | 200, 400, 401 |
| POST | `/analyze-sentiment/` | Analyze sentiment | Yes | Authenticated | `{text}` | `{sentiment, confidence, emotions}` | 200, 400, 401 |
| POST | `/suggest-solution/` | Suggest solution | Yes | Authenticated | `{ticket_id, description}` | `{suggestions: [{solution, confidence, source}]}` | 200, 400, 401 |
| POST | `/auto-assign/` | Auto-assign ticket | Yes | Agent/Admin | `{ticket_id}` | `{assigned_agent, confidence, reason}` | 200, 400, 401, 403 |
| GET | `/models/` | List AI models | Yes | Admin | None | `{count, next, previous, results: [{id, name, type, accuracy, status, created_at, updated_at}]}` | 200, 401, 403 |
| POST | `/models/` | Create AI model | Yes | Admin | `{name, type, configuration, training_data}` | `{id, name, type, accuracy, status, created_at, updated_at}` | 201, 400, 401, 403 |

---

## Advanced Analytics

### Base Path: `/api/v1/advanced-analytics/`

| Method | Endpoint | Description | Auth Required | Permissions | Request Body | Response Schema | Status Codes |
|--------|----------|-------------|---------------|-------------|--------------|-----------------|--------------|
| GET | `/realtime/` | Get real-time analytics | Yes | Authenticated | None | `{ticket_metrics, performance_metrics, user_activity}` | 200, 401 |
| GET | `/reports/` | List reports | Yes | Authenticated | None | `{count, next, previous, results: [{id, name, description, filters, metrics, data, created_at, updated_at}]}` | 200, 401 |
| POST | `/reports/` | Create report | Yes | Agent/Admin | `{name, description, filters, metrics}` | `{id, name, description, filters, metrics, data, created_at, updated_at}` | 201, 400, 401, 403 |
| GET | `/reports/{id}/` | Get report | Yes | Authenticated | None | `{id, name, description, filters, metrics, data, created_at, updated_at}` | 200, 401, 404 |
| PUT | `/reports/{id}/` | Update report | Yes | Agent/Admin | `{name, description, filters, metrics}` | `{id, name, description, filters, metrics, data, created_at, updated_at}` | 200, 400, 401, 403, 404 |
| DELETE | `/reports/{id}/` | Delete report | Yes | Admin | None | `{message}` | 204, 401, 403, 404 |
| GET | `/dashboards/` | List dashboards | Yes | Authenticated | None | `{count, next, previous, results: [{id, name, description, widgets, layout, created_at, updated_at}]}` | 200, 401 |
| POST | `/dashboards/` | Create dashboard | Yes | Agent/Admin | `{name, description, widgets, layout}` | `{id, name, description, widgets, layout, created_at, updated_at}` | 201, 400, 401, 403 |

---

## Mobile & IoT

### Base Path: `/api/v1/mobile-iot/`

| Method | Endpoint | Description | Auth Required | Permissions | Request Body | Response Schema | Status Codes |
|--------|----------|-------------|---------------|-------------|--------------|-----------------|--------------|
| GET | `/mobile-apps/` | List mobile apps | Yes | Authenticated | None | `{count, next, previous, results: [{id, name, platform_type, app_configuration, offline_capabilities, push_notifications, total_users, active_users, app_downloads, is_active, created_at, updated_at}]}` | 200, 401 |
| POST | `/mobile-apps/` | Create mobile app | Yes | Admin | `{name, platform_type, app_configuration, offline_capabilities}` | `{id, name, platform_type, app_configuration, offline_capabilities, push_notifications, total_users, active_users, app_downloads, is_active, created_at, updated_at}` | 201, 400, 401, 403 |
| GET | `/mobile-apps/{id}/` | Get mobile app | Yes | Authenticated | None | `{id, name, platform_type, app_configuration, offline_capabilities, push_notifications, total_users, active_users, app_downloads, is_active, created_at, updated_at}` | 200, 401, 404 |
| PUT | `/mobile-apps/{id}/` | Update mobile app | Yes | Admin | `{name, platform_type, app_configuration, offline_capabilities}` | `{id, name, platform_type, app_configuration, offline_capabilities, push_notifications, total_users, active_users, app_downloads, is_active, created_at, updated_at}` | 200, 400, 401, 403, 404 |
| DELETE | `/mobile-apps/{id}/` | Delete mobile app | Yes | Admin | None | `{message}` | 204, 401, 403, 404 |
| GET | `/iot-devices/` | List IoT devices | Yes | Authenticated | None | `{count, next, previous, results: [{id, name, device_type, model, serial_number, location, configuration, status, last_seen, is_active, created_at, updated_at}]}` | 200, 401 |
| POST | `/iot-devices/` | Create IoT device | Yes | Admin | `{name, device_type, model, serial_number, location, configuration}` | `{id, name, device_type, model, serial_number, location, configuration, status, last_seen, is_active, created_at, updated_at}` | 201, 400, 401, 403 |
| GET | `/iot-devices/{id}/` | Get IoT device | Yes | Authenticated | None | `{id, name, device_type, model, serial_number, location, configuration, status, last_seen, is_active, created_at, updated_at}` | 200, 401, 404 |
| PUT | `/iot-devices/{id}/` | Update IoT device | Yes | Admin | `{name, device_type, model, serial_number, location, configuration}` | `{id, name, device_type, model, serial_number, location, configuration, status, last_seen, is_active, created_at, updated_at}` | 200, 400, 401, 403, 404 |
| DELETE | `/iot-devices/{id}/` | Delete IoT device | Yes | Admin | None | `{message}` | 204, 401, 403, 404 |

---

## Advanced Security

### Base Path: `/api/v1/advanced-security/`

| Method | Endpoint | Description | Auth Required | Permissions | Request Body | Response Schema | Status Codes |
|--------|----------|-------------|---------------|-------------|--------------|-----------------|--------------|
| GET | `/security-incidents/` | List security incidents | Yes | Security/Admin | None | `{count, next, previous, results: [{id, title, description, severity, incident_type, status, affected_systems, source_ip, user_agent, affected_users, assigned_to, resolved_at, created_at, updated_at}]}` | 200, 401, 403 |
| POST | `/security-incidents/` | Create security incident | Yes | Security/Admin | `{title, description, severity, incident_type, affected_systems, source_ip, user_agent, affected_users}` | `{id, title, description, severity, incident_type, status, affected_systems, source_ip, user_agent, affected_users, assigned_to, resolved_at, created_at, updated_at}` | 201, 400, 401, 403 |
| GET | `/security-incidents/{id}/` | Get security incident | Yes | Security/Admin | None | `{id, title, description, severity, incident_type, status, affected_systems, source_ip, user_agent, affected_users, assigned_to, resolved_at, created_at, updated_at}` | 200, 401, 403, 404 |
| PUT | `/security-incidents/{id}/` | Update security incident | Yes | Security/Admin | `{title, description, severity, status, assigned_to}` | `{id, title, description, severity, incident_type, status, affected_systems, source_ip, user_agent, affected_users, assigned_to, resolved_at, created_at, updated_at}` | 200, 400, 401, 403, 404 |
| GET | `/security-audits/` | List security audits | Yes | Security/Admin | None | `{count, next, previous, results: [{id, audit_type, scope, standards, start_date, end_date, auditor, status, findings, recommendations, created_at, updated_at}]}` | 200, 401, 403 |
| POST | `/security-audits/` | Create security audit | Yes | Security/Admin | `{audit_type, scope, standards, start_date, end_date, auditor}` | `{id, audit_type, scope, standards, start_date, end_date, auditor, status, findings, recommendations, created_at, updated_at}` | 201, 400, 401, 403 |
| GET | `/security-audits/{id}/` | Get security audit | Yes | Security/Admin | None | `{id, audit_type, scope, standards, start_date, end_date, auditor, status, findings, recommendations, created_at, updated_at}` | 200, 401, 403, 404 |
| PUT | `/security-audits/{id}/` | Update security audit | Yes | Security/Admin | `{audit_type, scope, standards, start_date, end_date, auditor, status, findings, recommendations}` | `{id, audit_type, scope, standards, start_date, end_date, auditor, status, findings, recommendations, created_at, updated_at}` | 200, 400, 401, 403, 404 |

---

## Advanced Workflow

### Base Path: `/api/v1/advanced-workflow/`

| Method | Endpoint | Description | Auth Required | Permissions | Request Body | Response Schema | Status Codes |
|--------|----------|-------------|---------------|-------------|--------------|-----------------|--------------|
| GET | `/automations/` | List workflow automations | Yes | Agent/Admin | None | `{count, next, previous, results: [{id, name, description, trigger, actions, is_active, execution_count, last_executed, created_at, updated_at}]}` | 200, 401 |
| POST | `/automations/` | Create workflow automation | Yes | Agent/Admin | `{name, description, trigger, actions, is_active}` | `{id, name, description, trigger, actions, is_active, execution_count, last_executed, created_at, updated_at}` | 201, 400, 401, 403 |
| GET | `/automations/{id}/` | Get workflow automation | Yes | Agent/Admin | None | `{id, name, description, trigger, actions, is_active, execution_count, last_executed, created_at, updated_at}` | 200, 401, 403, 404 |
| PUT | `/automations/{id}/` | Update workflow automation | Yes | Agent/Admin | `{name, description, trigger, actions, is_active}` | `{id, name, description, trigger, actions, is_active, execution_count, last_executed, created_at, updated_at}` | 200, 400, 401, 403, 404 |
| DELETE | `/automations/{id}/` | Delete workflow automation | Yes | Admin | None | `{message}` | 204, 401, 403, 404 |
| POST | `/automations/{id}/execute/` | Execute workflow automation | Yes | Agent/Admin | `{parameters}` | `{execution_id, status, result}` | 200, 400, 401, 403, 404 |

---

## Advanced Communication

### Base Path: `/api/v1/advanced-communication/`

| Method | Endpoint | Description | Auth Required | Permissions | Request Body | Response Schema | Status Codes |
|--------|----------|-------------|---------------|-------------|--------------|-----------------|--------------|
| GET | `/communication-sessions/` | List communication sessions | Yes | Authenticated | None | `{count, next, previous, results: [{id, session_type, participants, scheduled_time, duration, meeting_room, agenda, status, meeting_link, recording_url, created_at, updated_at}]}` | 200, 401 |
| POST | `/communication-sessions/` | Create communication session | Yes | Authenticated | `{session_type, participants, scheduled_time, duration, meeting_room, agenda}` | `{id, session_type, participants, scheduled_time, duration, meeting_room, agenda, status, meeting_link, recording_url, created_at, updated_at}` | 201, 400, 401 |
| GET | `/communication-sessions/{id}/` | Get communication session | Yes | Authenticated | None | `{id, session_type, participants, scheduled_time, duration, meeting_room, agenda, status, meeting_link, recording_url, created_at, updated_at}` | 200, 401, 404 |
| PUT | `/communication-sessions/{id}/` | Update communication session | Yes | Authenticated | `{session_type, participants, scheduled_time, duration, meeting_room, agenda}` | `{id, session_type, participants, scheduled_time, duration, meeting_room, agenda, status, meeting_link, recording_url, created_at, updated_at}` | 200, 400, 401, 404 |
| DELETE | `/communication-sessions/{id}/` | Delete communication session | Yes | Authenticated | None | `{message}` | 204, 401, 404 |
| GET | `/communication-messages/` | List communication messages | Yes | Authenticated | None | `{count, next, previous, results: [{id, session, sender, content, message_type, timestamp, is_read}]}` | 200, 401 |
| POST | `/communication-messages/` | Send communication message | Yes | Authenticated | `{session, content, message_type}` | `{id, session, sender, content, message_type, timestamp, is_read}` | 201, 400, 401 |

---

## Integration Platform

### Base Path: `/api/v1/integration-platform/`

| Method | Endpoint | Description | Auth Required | Permissions | Request Body | Response Schema | Status Codes |
|--------|----------|-------------|---------------|-------------|--------------|-----------------|--------------|
| GET | `/api-integrations/` | List API integrations | Yes | Admin | None | `{count, next, previous, results: [{id, name, api_type, base_url, version, authentication_methods, rate_limits, api_documentation, total_requests, successful_requests, failed_requests, average_response_time, is_active, created_at, updated_at}]}` | 200, 401, 403 |
| POST | `/api-integrations/` | Create API integration | Yes | Admin | `{name, api_type, base_url, version, authentication_methods, rate_limits, api_documentation}` | `{id, name, api_type, base_url, version, authentication_methods, rate_limits, api_documentation, total_requests, successful_requests, failed_requests, average_response_time, is_active, created_at, updated_at}` | 201, 400, 401, 403 |
| GET | `/api-integrations/{id}/` | Get API integration | Yes | Admin | None | `{id, name, api_type, base_url, version, authentication_methods, rate_limits, api_documentation, total_requests, successful_requests, failed_requests, average_response_time, is_active, created_at, updated_at}` | 200, 401, 403, 404 |
| PUT | `/api-integrations/{id}/` | Update API integration | Yes | Admin | `{name, api_type, base_url, version, authentication_methods, rate_limits, api_documentation}` | `{id, name, api_type, base_url, version, authentication_methods, rate_limits, api_documentation, total_requests, successful_requests, failed_requests, average_response_time, is_active, created_at, updated_at}` | 200, 400, 401, 403, 404 |
| DELETE | `/api-integrations/{id}/` | Delete API integration | Yes | Admin | None | `{message}` | 204, 401, 403, 404 |
| GET | `/webhooks/` | List webhooks | Yes | Admin | None | `{count, next, previous, results: [{id, name, url, events, secret, is_active, delivery_count, success_count, failure_count, last_delivery, created_at, updated_at}]}` | 200, 401, 403 |
| POST | `/webhooks/` | Create webhook | Yes | Admin | `{name, url, events, secret, is_active}` | `{id, name, url, events, secret, is_active, delivery_count, success_count, failure_count, last_delivery, created_at, updated_at}` | 201, 400, 401, 403 |
| GET | `/webhooks/{id}/` | Get webhook | Yes | Admin | None | `{id, name, url, events, secret, is_active, delivery_count, success_count, failure_count, last_delivery, created_at, updated_at}` | 200, 401, 403, 404 |
| PUT | `/webhooks/{id}/` | Update webhook | Yes | Admin | `{name, url, events, secret, is_active}` | `{id, name, url, events, secret, is_active, delivery_count, success_count, failure_count, last_delivery, created_at, updated_at}` | 200, 400, 401, 403, 404 |
| DELETE | `/webhooks/{id}/` | Delete webhook | Yes | Admin | None | `{message}` | 204, 401, 403, 404 |

---

## Customer Experience

### Base Path: `/api/v1/customer-experience/`

| Method | Endpoint | Description | Auth Required | Permissions | Request Body | Response Schema | Status Codes |
|--------|----------|-------------|---------------|-------------|--------------|-----------------|--------------|
| GET | `/feedback/` | List customer feedback | Yes | Authenticated | None | `{count, next, previous, results: [{id, ticket, customer, rating, feedback, categories, is_public, created_at, updated_at}]}` | 200, 401 |
| POST | `/feedback/` | Create customer feedback | Yes | Authenticated | `{ticket_id, rating, feedback, categories, is_public}` | `{id, ticket, customer, rating, feedback, categories, is_public, created_at, updated_at}` | 201, 400, 401 |
| GET | `/feedback/{id}/` | Get customer feedback | Yes | Authenticated | None | `{id, ticket, customer, rating, feedback, categories, is_public, created_at, updated_at}` | 200, 401, 404 |
| GET | `/journey/{customer_id}/` | Get customer journey | Yes | Authenticated | None | `{customer_id, journey_stages, total_touchpoints, journey_duration, conversion_rate}` | 200, 401, 404 |
| GET | `/satisfaction/` | Get satisfaction metrics | Yes | Agent/Admin | None | `{overall_satisfaction, average_rating, rating_distribution, feedback_trends}` | 200, 401, 403 |

---

## System Status & Health

### Base Path: `/api/v1/`

| Method | Endpoint | Description | Auth Required | Permissions | Request Body | Response Schema | Status Codes |
|--------|----------|-------------|---------------|-------------|--------------|-----------------|--------------|
| GET | `/health/` | Health check | No | None | None | `{status, services, timestamp}` | 200, 503 |
| GET | `/status/` | System status | No | None | None | `{status, version, uptime, services}` | 200, 503 |
| GET | `/system/status/` | Detailed system status | Yes | Admin | None | `{status, version, uptime, services, performance, database, cache, queue}` | 200, 401, 403 |
| GET | `/features/status/` | Feature status | Yes | Authenticated | None | `{features: [{name, status, version, last_updated}]}` | 200, 401 |
| GET | `/features/connections/` | Feature connections | Yes | Authenticated | None | `{connections: [{feature, status, latency, last_check}]}` | 200, 401 |
| GET | `/realtime/capabilities/` | Real-time capabilities | Yes | Authenticated | None | `{websocket_url, supported_events, authentication}` | 200, 401 |

---

## API Services

### Base Path: `/api/v1/`

| Method | Endpoint | Description | Auth Required | Permissions | Request Body | Response Schema | Status Codes |
|--------|----------|-------------|---------------|-------------|--------------|-----------------|--------------|
| GET | `/services/` | List API services | Yes | Admin | None | `{count, next, previous, results: [{id, name, service_type, base_url, status, health_check_url, last_health_check, created_at, updated_at}]}` | 200, 401, 403 |
| POST | `/services/` | Create API service | Yes | Admin | `{name, service_type, base_url, health_check_url}` | `{id, name, service_type, base_url, status, health_check_url, last_health_check, created_at, updated_at}` | 201, 400, 401, 403 |
| GET | `/services/{id}/` | Get API service | Yes | Admin | None | `{id, name, service_type, base_url, status, health_check_url, last_health_check, created_at, updated_at}` | 200, 401, 403, 404 |
| PUT | `/services/{id}/` | Update API service | Yes | Admin | `{name, service_type, base_url, health_check_url}` | `{id, name, service_type, base_url, status, health_check_url, last_health_check, created_at, updated_at}` | 200, 400, 401, 403, 404 |
| DELETE | `/services/{id}/` | Delete API service | Yes | Admin | None | `{message}` | 204, 401, 403, 404 |
| GET | `/services/health-check/` | Check all services health | Yes | Admin | None | `{status, services: [{name, status, response_time, error}]}` | 200, 401, 403 |
| GET | `/integration-logs/` | List integration logs | Yes | Admin | None | `{count, next, previous, results: [{id, service, action, status, request_data, response_data, error_message, timestamp}]}` | 200, 401, 403 |
| POST | `/realtime/webhook/` | Real-time webhook | No | Webhook | `{event, data, timestamp}` | `{status, message}` | 200, 400, 401 |
| GET | `/docs/` | API documentation | No | None | None | HTML page | 200 |

---

## Summary

### Total Endpoints by Category

| Category | Endpoints | Methods |
|----------|-----------|---------|
| Authentication | 12 | POST, GET, PUT |
| Organization Management | 5 | GET, POST, PUT, DELETE |
| Ticket Management | 7 | GET, POST, PUT, DELETE |
| Knowledge Base | 7 | GET, POST, PUT, DELETE |
| Field Service | 10 | GET, POST, PUT, DELETE |
| AI/ML Features | 6 | POST, GET |
| Advanced Analytics | 8 | GET, POST, PUT, DELETE |
| Mobile & IoT | 8 | GET, POST, PUT, DELETE |
| Advanced Security | 8 | GET, POST, PUT |
| Advanced Workflow | 6 | GET, POST, PUT, DELETE |
| Advanced Communication | 7 | GET, POST, PUT, DELETE |
| Integration Platform | 8 | GET, POST, PUT, DELETE |
| Customer Experience | 5 | GET, POST |
| System Status | 6 | GET |
| API Services | 8 | GET, POST, PUT, DELETE |

### Total API Endpoints: **107 endpoints**

### Authentication Methods
- **JWT Token**: Primary authentication method
- **API Key**: For service-to-service communication
- **Session**: For web interface
- **OAuth2**: For third-party integrations
- **2FA**: Two-factor authentication support

### Permission Levels
- **Public**: No authentication required
- **Authenticated**: Valid JWT token required
- **Agent**: Agent role or higher required
- **Admin**: Administrator role required
- **Security**: Security team role required

### Response Formats
- **JSON**: All API responses in JSON format
- **Pagination**: List endpoints support pagination
- **Filtering**: Most list endpoints support filtering
- **Search**: Text search capabilities
- **Sorting**: Ordering by various fields

---

*This inventory is automatically generated and updated with each API release.*
