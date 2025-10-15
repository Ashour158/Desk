# 🤝 **Contributing to Helpdesk Platform**

Thank you for your interest in contributing to the Helpdesk Platform! This document provides guidelines and information for contributors.

---

## 📋 **Table of Contents**

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Community Guidelines](#community-guidelines)

---

## 📜 **Code of Conduct**

### **Our Pledge**

We are committed to providing a welcoming and inspiring community for all. Please read and follow our Code of Conduct:

- **Be Respectful**: Treat everyone with respect and kindness
- **Be Inclusive**: Welcome newcomers and help them learn
- **Be Constructive**: Provide helpful feedback and suggestions
- **Be Professional**: Maintain a professional tone in all interactions

### **Unacceptable Behavior**

- Harassment, discrimination, or offensive comments
- Trolling, insulting, or derogatory remarks
- Personal attacks or political discussions
- Spam or off-topic discussions

---

## 🚀 **Getting Started**

### **Prerequisites**

Before contributing, ensure you have:

- **Python 3.11+** installed
- **Node.js 18+** installed
- **Docker & Docker Compose** installed
- **Git** installed
- **Basic knowledge** of Django, React, and REST APIs

### **Fork and Clone**

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/helpdesk-platform.git
   cd helpdesk-platform
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-username/helpdesk-platform.git
   ```

### **Environment Setup**

1. **Validate your environment**:
   ```bash
   # Linux/macOS
   ./scripts/validate-setup.sh
   
   # Windows PowerShell
   .\scripts\validate-setup.ps1
   ```

2. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start development environment**:
   ```bash
   docker-compose up -d
   ```

4. **Run migrations**:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create superuser**:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

---

## 🔄 **Development Workflow**

### **Branch Strategy**

We use **Git Flow** for our branching strategy:

- **`main`**: Production-ready code
- **`develop`**: Integration branch for features
- **`feature/*`**: Feature development branches
- **`bugfix/*`**: Bug fix branches
- **`hotfix/*`**: Critical bug fixes

### **Creating a Feature Branch**

```bash
# Start from develop branch
git checkout develop
git pull upstream develop

# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes
git add .
git commit -m "feat: add your feature description"
```

### **Branch Naming Convention**

- **Features**: `feature/description` (e.g., `feature/user-authentication`)
- **Bug Fixes**: `bugfix/description` (e.g., `bugfix/login-error`)
- **Hotfixes**: `hotfix/description` (e.g., `hotfix/security-patch`)
- **Documentation**: `docs/description` (e.g., `docs/api-documentation`)

---

## 📝 **Code Standards**

### **Python/Django Code**

#### **Style Guidelines**
- Follow **PEP 8** style guide
- Use **Black** for code formatting
- Use **isort** for import sorting
- Use **flake8** for linting

#### **Code Formatting**
```bash
# Format Python code
black core/
isort core/

# Check linting
flake8 core/
```

#### **Django Best Practices**
- Use **class-based views** when appropriate
- Use **serializers** for API responses
- Use **permissions** for access control
- Use **signals** for business logic
- Use **managers** for complex queries

#### **Example Code Structure**
```python
# apps/tickets/views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

class TicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tickets.
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority', 'category']
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign ticket to agent."""
        ticket = self.get_object()
        # Implementation here
        return Response({'status': 'assigned'})
```

### **JavaScript/React Code**

#### **Style Guidelines**
- Use **ESLint** for linting
- Use **Prettier** for formatting
- Follow **Airbnb** style guide
- Use **TypeScript** for type safety

#### **Code Formatting**
```bash
# Format JavaScript/TypeScript code
npm run lint:fix
npm run format
```

#### **React Best Practices**
- Use **functional components** with hooks
- Use **TypeScript** for type safety
- Use **custom hooks** for reusable logic
- Use **context** for state management
- Use **lazy loading** for performance

#### **Example Component Structure**
```typescript
// src/components/TicketList.tsx
import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Ticket } from '../types';

interface TicketListProps {
  organizationId: string;
  onTicketSelect: (ticket: Ticket) => void;
}

export const TicketList: React.FC<TicketListProps> = ({
  organizationId,
  onTicketSelect,
}) => {
  const [filters, setFilters] = useState({});
  
  const { data: tickets, isLoading, error } = useQuery({
    queryKey: ['tickets', organizationId, filters],
    queryFn: () => fetchTickets(organizationId, filters),
  });
  
  if (isLoading) return <div>Loading...</div>;
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

---

## 🧪 **Testing Guidelines**

### **Test Coverage Requirements**
- **Minimum Coverage**: 80% for new code
- **Critical Paths**: 100% coverage for authentication, payments, data processing
- **API Endpoints**: All endpoints must have tests
- **Frontend Components**: All components must have tests

### **Backend Testing**

#### **Unit Tests**
```python
# tests/test_tickets.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.tickets.models import Ticket
from apps.tickets.serializers import TicketSerializer

class TicketTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.ticket = Ticket.objects.create(
            subject='Test Ticket',
            description='Test Description',
            user=self.user
        )
    
    def test_ticket_creation(self):
        """Test ticket creation."""
        self.assertEqual(self.ticket.subject, 'Test Ticket')
        self.assertEqual(self.ticket.user, self.user)
    
    def test_ticket_serializer(self):
        """Test ticket serializer."""
        serializer = TicketSerializer(self.ticket)
        self.assertIn('subject', serializer.data)
        self.assertIn('description', serializer.data)
```

#### **Integration Tests**
```python
# tests/test_api.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

class TicketAPITestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_ticket(self):
        """Test ticket creation via API."""
        data = {
            'subject': 'Test Ticket',
            'description': 'Test Description',
            'priority': 'medium'
        }
        response = self.client.post('/api/v1/tickets/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 1)
```

### **Frontend Testing**

#### **Component Tests**
```typescript
// src/components/__tests__/TicketList.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TicketList } from '../TicketList';

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

describe('TicketList', () => {
  it('renders ticket list', () => {
    const queryClient = createTestQueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <TicketList organizationId="test-org" onTicketSelect={jest.fn()} />
      </QueryClientProvider>
    );
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
  
  it('calls onTicketSelect when ticket is clicked', () => {
    const onTicketSelect = jest.fn();
    const queryClient = createTestQueryClient();
    
    render(
      <QueryClientProvider client={queryClient}>
        <TicketList organizationId="test-org" onTicketSelect={onTicketSelect} />
      </QueryClientProvider>
    );
    
    // Test implementation
  });
});
```

#### **API Tests**
```typescript
// src/api/__tests__/tickets.test.ts
import { fetchTickets, createTicket } from '../tickets';

describe('Tickets API', () => {
  it('fetches tickets successfully', async () => {
    const mockTickets = [
      { id: '1', subject: 'Test Ticket 1' },
      { id: '2', subject: 'Test Ticket 2' },
    ];
    
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockTickets),
    });
    
    const tickets = await fetchTickets('org-1');
    expect(tickets).toEqual(mockTickets);
  });
});
```

### **Running Tests**

#### **Backend Tests**
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.tickets

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

#### **Frontend Tests**
```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

#### **End-to-End Tests**
```bash
# Run E2E tests
npm run test:e2e

# Run E2E tests in headless mode
npm run test:e2e:headless
```

---

## 📚 **Documentation**

### **Code Documentation**

#### **Python/Django**
```python
def create_ticket(user, subject, description, priority='medium'):
    """
    Create a new ticket for a user.
    
    Args:
        user (User): The user creating the ticket
        subject (str): The ticket subject
        description (str): The ticket description
        priority (str): The ticket priority (low, medium, high, urgent)
    
    Returns:
        Ticket: The created ticket instance
    
    Raises:
        ValidationError: If the ticket data is invalid
        PermissionError: If the user doesn't have permission to create tickets
    
    Example:
        >>> user = User.objects.get(email='user@example.com')
        >>> ticket = create_ticket(user, 'Login Issue', 'Cannot login')
        >>> print(ticket.subject)
        Login Issue
    """
    # Implementation here
    pass
```

#### **TypeScript/React**
```typescript
/**
 * Custom hook for managing ticket data.
 * 
 * @param organizationId - The organization ID to fetch tickets for
 * @param filters - Optional filters to apply to the tickets
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
  // Implementation here
};
```

### **API Documentation**

#### **Endpoint Documentation**
```python
class TicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tickets.
    
    This ViewSet provides CRUD operations for tickets including:
    - List all tickets for the authenticated user's organization
    - Create new tickets
    - Retrieve, update, and delete specific tickets
    - Assign tickets to agents
    - Add comments to tickets
    
    Authentication:
        Requires JWT token authentication
    
    Permissions:
        - List/Retrieve: Authenticated users
        - Create: Authenticated users
        - Update/Delete: Ticket owner or organization admin
    
    Filters:
        - status: Filter by ticket status
        - priority: Filter by ticket priority
        - category: Filter by ticket category
        - assigned_to: Filter by assigned agent
    """
    # Implementation here
```

### **README Updates**

When adding new features, update the README.md:

```markdown
## 🚀 New Features

### Feature Name
- **Description**: Brief description of the feature
- **Usage**: How to use the feature
- **API**: Relevant API endpoints
- **Examples**: Code examples
```

---

## 🔄 **Pull Request Process**

### **Before Submitting**

1. **Run Tests**: Ensure all tests pass
   ```bash
   # Backend tests
   python manage.py test
   
   # Frontend tests
   npm test
   
   # Linting
   flake8 core/
   npm run lint
   ```

2. **Update Documentation**: Update relevant documentation
3. **Check Coverage**: Ensure test coverage meets requirements
4. **Rebase**: Rebase your branch on the latest develop

### **Pull Request Template**

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Test coverage meets requirements

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or documented if necessary)

## Screenshots (if applicable)
Add screenshots to help explain your changes

## Additional Notes
Any additional information about the changes
```

### **Review Process**

1. **Automated Checks**: CI/CD pipeline runs automatically
2. **Code Review**: At least 2 reviewers required
3. **Testing**: All tests must pass
4. **Documentation**: Documentation must be updated
5. **Approval**: Maintainer approval required

### **After Approval**

1. **Squash Commits**: Squash commits into logical units
2. **Merge**: Merge into develop branch
3. **Delete Branch**: Delete feature branch
4. **Update**: Update local branches

---

## 🐛 **Issue Reporting**

### **Bug Reports**

When reporting bugs, include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, Python version, Node version, etc.
6. **Screenshots**: Screenshots if applicable
7. **Logs**: Relevant error logs

### **Feature Requests**

When requesting features, include:

1. **Description**: Clear description of the feature
2. **Use Case**: Why this feature is needed
3. **Proposed Solution**: How you think it should work
4. **Alternatives**: Other solutions you've considered
5. **Additional Context**: Any other relevant information

### **Issue Labels**

- **bug**: Something isn't working
- **enhancement**: New feature or request
- **documentation**: Improvements or additions to documentation
- **good first issue**: Good for newcomers
- **help wanted**: Extra attention is needed
- **priority: high**: High priority issue
- **priority: low**: Low priority issue

---

## 👥 **Community Guidelines**

### **Getting Help**

1. **Documentation**: Check existing documentation first
2. **Issues**: Search existing issues before creating new ones
3. **Discussions**: Use GitHub Discussions for questions
4. **Discord**: Join our Discord server for real-time help

### **Contributing Guidelines**

1. **Start Small**: Begin with small, well-defined tasks
2. **Ask Questions**: Don't hesitate to ask for clarification
3. **Be Patient**: Maintainers are volunteers
4. **Be Respectful**: Follow our Code of Conduct

### **Recognition**

Contributors are recognized in:

- **CONTRIBUTORS.md**: List of all contributors
- **Release Notes**: Mentioned in release notes
- **GitHub**: Contributor badges and statistics
- **Community**: Special recognition in community channels

---

## 🛠️ **Development Tools**

### **Recommended Tools**

#### **Code Editors**
- **VS Code**: With Python, Django, React extensions
- **PyCharm**: Professional Python IDE
- **WebStorm**: Professional JavaScript IDE

#### **Browser Extensions**
- **React Developer Tools**: For React debugging
- **Redux DevTools**: For state management
- **Django Debug Toolbar**: For Django debugging

#### **API Testing**
- **Postman**: API testing and development
- **Insomnia**: API development
- **curl**: Command-line API testing

### **Development Scripts**

```bash
# Start development environment
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run tests
docker-compose exec web python manage.py test
docker-compose exec customer-portal npm test

# Format code
docker-compose exec web black core/
docker-compose exec customer-portal npm run format

# Lint code
docker-compose exec web flake8 core/
docker-compose exec customer-portal npm run lint
```

---

## 📞 **Contact and Support**

### **Getting Help**

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and discussions
- **Discord Server**: For real-time community support
- **Email**: For private or sensitive issues

### **Maintainers**

- **Lead Maintainer**: [Name] - [email]
- **Backend Maintainer**: [Name] - [email]
- **Frontend Maintainer**: [Name] - [email]
- **DevOps Maintainer**: [Name] - [email]

---

## 📄 **License**

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

**Thank you for contributing to the Helpdesk Platform!** 🎉

---

**Last Updated**: October 13, 2025  
**Next Review**: November 13, 2025  
**Maintained By**: Development Team
