# GitHub Copilot Instructions for Helpdesk Platform

This file contains instructions for GitHub Copilot to help understand and work with the Helpdesk Platform codebase.

## Project Overview

The Helpdesk Platform is a comprehensive, enterprise-grade multi-tenant helpdesk and field service management (FSM) system built with a hybrid architecture:

- **Backend**: Django 4.2 with Django REST Framework
- **Frontend**: React 18 with TypeScript, Vite, and Tailwind CSS
- **AI Service**: FastAPI-based microservice for AI features
- **Real-time Service**: Node.js with Socket.io for WebSocket functionality
- **Database**: PostgreSQL 15+ with PostGIS extension
- **Cache & Message Broker**: Redis 7+
- **Task Queue**: Celery with Redis backend

## Architecture

### Hybrid Architecture
- **Django Monolith**: Core business logic, multi-tenancy, authentication, REST APIs
- **AI Microservice**: Separate FastAPI service for AI/ML operations
- **Real-time Service**: Node.js service for WebSocket connections and live updates
- **Celery Workers**: Background task processing (emails, notifications, reports)

### Multi-Tenancy
- Organization-based isolation (not schema-based)
- Shared database with `organization` foreign keys
- Row-level security through Django ORM filters
- Middleware ensures all queries are scoped to the current organization

## Code Standards

### Python/Django Code

#### Style Guidelines
- Follow **PEP 8** style guide
- Use **Black** formatter (line length: 88)
- Use **isort** for import sorting
- Use **flake8** for linting
- Maximum line length: 88 characters

#### Django Patterns
- Use **class-based views** for complex views, function-based views for simple endpoints
- Use **ViewSets** with Django REST Framework for CRUD operations
- Use **serializers** for all API responses
- Use **permissions** classes for access control
- Use **signals** sparingly (only for cross-app communication)
- Use **managers** and **querysets** for complex database queries
- Use **F() and Q()** objects for database-level operations
- Always use `select_related()` and `prefetch_related()` to avoid N+1 queries

#### Naming Conventions
- Models: PascalCase, singular (e.g., `Ticket`, `WorkOrder`)
- Views: PascalCase for classes, snake_case for functions
- URLs: kebab-case with trailing slashes (e.g., `/api/v1/tickets/`)
- Variables: snake_case
- Constants: UPPER_SNAKE_CASE

#### Django Model Best Practices
- Always include `created_at` and `updated_at` timestamps
- Use `UUIDField` as primary keys for better security and distributed systems
- Add `organization` foreign key to all tenant-specific models
- Include proper `__str__` methods
- Add `Meta` class with `ordering` and `verbose_name`
- Use `related_name` for all foreign keys

Example:
```python
class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'created_at']),
        ]

    def __str__(self):
        return f"{self.subject} - {self.get_status_display()}"
```

#### API Serializers
- Use `ModelSerializer` for model-based APIs
- Always validate input data
- Use nested serializers for related objects
- Include `read_only_fields` in Meta
- Use `SerializerMethodField` for computed fields

Example:
```python
class TicketSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id', 'subject', 'description', 'status', 'priority', 
                  'assigned_to', 'assigned_to_name', 'comment_count', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_comment_count(self, obj):
        return obj.comments.count()

    def validate_priority(self, value):
        if value not in ['low', 'medium', 'high', 'urgent']:
            raise serializers.ValidationError("Invalid priority level")
        return value
```

#### ViewSet Patterns
```python
class TicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tickets with multi-tenancy support.
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category']
    search_fields = ['subject', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority']

    def get_queryset(self):
        # Always filter by organization from request
        return super().get_queryset().filter(
            organization=self.request.user.organization
        ).select_related('assigned_to', 'created_by').prefetch_related('comments')

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign ticket to an agent."""
        ticket = self.get_object()
        agent_id = request.data.get('agent_id')
        # Implementation
        return Response({'status': 'assigned'})
```

### JavaScript/TypeScript/React Code

#### Style Guidelines
- Use **TypeScript** for all new React components
- Use **ESLint** with React hooks plugin
- Use **Prettier** for code formatting
- Follow **Airbnb** style guide
- Use functional components with hooks (no class components)

#### Component Structure
```typescript
// src/components/tickets/TicketList.tsx
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Ticket } from '../../types/ticket';

interface TicketListProps {
  organizationId: string;
  status?: string;
  onTicketSelect: (ticket: Ticket) => void;
}

export const TicketList: React.FC<TicketListProps> = ({
  organizationId,
  status,
  onTicketSelect,
}) => {
  const [filters, setFilters] = useState({ status });

  const { data: tickets, isLoading, error } = useQuery({
    queryKey: ['tickets', organizationId, filters],
    queryFn: () => fetchTickets(organizationId, filters),
  });

  if (isLoading) return <div>Loading tickets...</div>;
  if (error) return <div>Error loading tickets</div>;

  return (
    <div className="ticket-list">
      {tickets?.map(ticket => (
        <TicketCard
          key={ticket.id}
          ticket={ticket}
          onClick={() => onTicketSelect(ticket)}
        />
      ))}
    </div>
  );
};
```

#### State Management
- Use **React Query** for server state (API data)
- Use **Context API** for global UI state (theme, user preferences)
- Use **useState** for local component state
- Use **useReducer** for complex local state
- Avoid prop drilling; use Context for data needed by many components

#### React Patterns
- Use custom hooks for reusable logic
- Memoize expensive computations with `useMemo`
- Memoize callbacks with `useCallback`
- Use `React.memo` for expensive components
- Lazy load routes and heavy components
- Use Suspense for loading states

#### TypeScript Types
```typescript
// src/types/ticket.ts
export interface Ticket {
  id: string;
  subject: string;
  description: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assignedTo?: User;
  createdAt: string;
  updatedAt: string;
}

export interface TicketFilters {
  status?: string;
  priority?: string;
  assignedTo?: string;
  search?: string;
}

export interface TicketCreateData {
  subject: string;
  description: string;
  priority: Ticket['priority'];
  category?: string;
}
```

#### Styling with Tailwind
- Use Tailwind utility classes for styling
- Create reusable component classes in Tailwind config for common patterns
- Use `clsx` or `cn` utility for conditional classes
- Follow mobile-first responsive design
- Use consistent spacing scale (4, 8, 12, 16, 24, 32, 48, 64)

```typescript
<div className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
  <h3 className="text-lg font-semibold text-gray-900">{ticket.subject}</h3>
  <span className={clsx(
    "px-3 py-1 rounded-full text-sm font-medium",
    ticket.priority === 'urgent' && "bg-red-100 text-red-800",
    ticket.priority === 'high' && "bg-orange-100 text-orange-800",
    ticket.priority === 'medium' && "bg-yellow-100 text-yellow-800",
    ticket.priority === 'low' && "bg-green-100 text-green-800",
  )}>
    {ticket.priority}
  </span>
</div>
```

## Testing Guidelines

### Backend Testing (Django)

#### Test Structure
- Place tests in `tests/` directory within each app
- Use `pytest` as the test runner
- Use `pytest-django` for Django-specific fixtures
- Use `factory_boy` for test data generation

#### Test Patterns
```python
# tests/test_tickets.py
import pytest
from django.contrib.auth import get_user_model
from apps.tickets.models import Ticket
from tests.factories import TicketFactory, UserFactory

User = get_user_model()

@pytest.mark.django_db
class TestTicketModel:
    def test_ticket_creation(self):
        """Test that tickets are created correctly."""
        ticket = TicketFactory(subject='Test Ticket')
        assert ticket.subject == 'Test Ticket'
        assert ticket.status == 'open'

    def test_ticket_organization_isolation(self, organization1, organization2):
        """Test that tickets are isolated by organization."""
        ticket1 = TicketFactory(organization=organization1)
        ticket2 = TicketFactory(organization=organization2)
        
        org1_tickets = Ticket.objects.filter(organization=organization1)
        assert ticket1 in org1_tickets
        assert ticket2 not in org1_tickets

@pytest.mark.django_db
class TestTicketAPI:
    def test_create_ticket(self, api_client, authenticated_user):
        """Test ticket creation via API."""
        data = {
            'subject': 'Test Ticket',
            'description': 'Test Description',
            'priority': 'medium'
        }
        response = api_client.post('/api/v1/tickets/', data)
        assert response.status_code == 201
        assert response.data['subject'] == 'Test Ticket'
```

### Frontend Testing (React)

#### Test Structure
- Place tests next to components: `ComponentName.test.tsx`
- Use `@testing-library/react` for component testing
- Use `vitest` as the test runner
- Mock API calls with `msw` or jest mocks

#### Test Patterns
```typescript
// src/components/tickets/__tests__/TicketList.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TicketList } from '../TicketList';

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

describe('TicketList', () => {
  it('renders loading state initially', () => {
    const queryClient = createTestQueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <TicketList organizationId="test-org" onTicketSelect={jest.fn()} />
      </QueryClientProvider>
    );
    
    expect(screen.getByText('Loading tickets...')).toBeInTheDocument();
  });

  it('renders tickets after loading', async () => {
    const queryClient = createTestQueryClient();
    // Mock API response
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ([
        { id: '1', subject: 'Test Ticket 1' },
        { id: '2', subject: 'Test Ticket 2' },
      ]),
    });

    render(
      <QueryClientProvider client={queryClient}>
        <TicketList organizationId="test-org" onTicketSelect={jest.fn()} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Test Ticket 1')).toBeInTheDocument();
      expect(screen.getByText('Test Ticket 2')).toBeInTheDocument();
    });
  });
});
```

## Common Patterns and Conventions

### API Endpoints
- Base URL: `/api/v1/`
- Always use trailing slashes
- Use plural nouns for resources: `/tickets/`, `/work-orders/`
- Use kebab-case for multi-word resources: `/work-orders/`
- Version the API: `/api/v1/`, `/api/v2/`

### Authentication
- JWT tokens stored in httpOnly cookies (backend) and localStorage (frontend)
- Refresh tokens for long-lived sessions
- Token format: `Authorization: Bearer <token>`

### Error Handling
- Use consistent error response format:
```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "field_errors": {
    "field_name": ["Error for this field"]
  }
}
```

### Permissions
- Check permissions in ViewSets using `permission_classes`
- Check object-level permissions in `get_object()`
- Always verify organization ownership

### File Structure

#### Backend (Django)
```
core/
├── apps/
│   ├── tickets/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── permissions.py
│   │   ├── filters.py
│   │   └── tests/
│   ├── users/
│   └── organizations/
├── config/
│   ├── settings/
│   ├── urls.py
│   └── wsgi.py
└── tests/
```

#### Frontend (React)
```
customer-portal/
├── src/
│   ├── components/      # Reusable components
│   ├── pages/          # Page-level components
│   ├── hooks/          # Custom React hooks
│   ├── utils/          # Utility functions
│   ├── types/          # TypeScript type definitions
│   ├── api/            # API client functions
│   ├── contexts/       # React contexts
│   └── assets/         # Images, fonts, etc.
├── public/
└── tests/
```

## Development Workflow

### Branch Naming
- Features: `feature/description` (e.g., `feature/ticket-assignment`)
- Bug fixes: `bugfix/description` (e.g., `bugfix/login-error`)
- Hotfixes: `hotfix/description`

### Commit Messages
Follow Conventional Commits:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring
- `test:` for test additions/changes
- `chore:` for maintenance tasks

### Code Review Checklist
- [ ] Tests added/updated and passing
- [ ] Code follows style guidelines
- [ ] No console.log or debug statements
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Performance considered
- [ ] Multi-tenancy maintained
- [ ] Backwards compatible (or documented breaking changes)

## Environment Variables

### Required
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `DEBUG`: Set to `False` in production

### Optional (for features)
- `OPENAI_API_KEY`: For AI features
- `ANTHROPIC_API_KEY`: For Claude AI integration
- `GOOGLE_MAPS_API_KEY`: For location services
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`: For SMS
- `SENDGRID_API_KEY`: For email services

## Important Notes

1. **Multi-tenancy is critical**: Always filter by organization in queries
2. **Security first**: Never expose sensitive data, always validate input
3. **Performance matters**: Use select_related/prefetch_related, optimize queries
4. **Test coverage**: Maintain >80% test coverage for new code
5. **Documentation**: Update docs when adding features
6. **Backwards compatibility**: Don't break existing APIs without versioning
7. **Mobile responsive**: All UI must work on mobile devices
8. **Accessibility**: Follow WCAG 2.1 AA standards

## Getting Help

- Check `README.md` for setup instructions
- Check `CONTRIBUTING.md` for contribution guidelines
- Check `docs/` folder for detailed documentation
- Check `docs/DEVELOPER_ONBOARDING.md` for onboarding guide
- Check existing code for patterns and examples

## Common Tasks

### Adding a New Django Model
1. Create model in appropriate app's `models.py`
2. Add `organization` foreign key for multi-tenancy
3. Create migration: `python manage.py makemigrations`
4. Run migration: `python manage.py migrate`
5. Create serializer in `serializers.py`
6. Create ViewSet in `views.py`
7. Add URL route in `urls.py`
8. Add permissions in `permissions.py`
9. Write tests

### Adding a New React Component
1. Create component file in `src/components/`
2. Add TypeScript types for props
3. Implement component with hooks
4. Add Tailwind styling
5. Create test file
6. Export from index file if reusable

### Adding a New API Endpoint
1. Add method to ViewSet or create new view
2. Update serializer if needed
3. Update URL routing
4. Add permissions check
5. Write API tests
6. Update API documentation
7. Update frontend API client

## Documentation Requirements

### Python/Django
Use docstrings for all public functions, classes, and methods:
```python
def create_ticket(user, subject, description, priority='medium'):
    """
    Create a new ticket for a user.
    
    Args:
        user (User): The user creating the ticket
        subject (str): The ticket subject
        description (str): Detailed description of the issue
        priority (str): Priority level (low, medium, high, urgent)
    
    Returns:
        Ticket: The newly created ticket instance
    
    Raises:
        ValidationError: If the ticket data is invalid
        PermissionError: If the user lacks permission
    """
    pass
```

### TypeScript/React
Use JSDoc/TSDoc for complex functions:
```typescript
/**
 * Custom hook for managing ticket data with automatic refetching.
 * 
 * @param organizationId - The organization ID to fetch tickets for
 * @param filters - Optional filters to apply to the ticket query
 * @returns Object containing tickets data, loading state, and error state
 * 
 * @example
 * ```typescript
 * const { tickets, isLoading, error } = useTickets('org-123', {
 *   status: 'open',
 *   priority: 'high'
 * });
 * ```
 */
export const useTickets = (
  organizationId: string,
  filters?: TicketFilters
): UseTicketsReturn => {
  // Implementation
};
```

## Summary

This is a well-structured, production-grade Django + React application with multi-tenancy, comprehensive testing, and modern development practices. When working with this codebase:

1. Always maintain multi-tenancy (organization filtering)
2. Follow existing patterns and conventions
3. Write tests for all new code
4. Use TypeScript for frontend code
5. Optimize database queries
6. Keep security in mind
7. Update documentation
8. Follow code style guidelines

For more detailed information, refer to the project documentation in the `docs/` directory.
