import { useQuery, useMutation, useQueryClient } from 'react-query';
import Logger from '../utils/logger';

/**
 * Optimized React Query hooks for data fetching with caching and error handling
 */

/**
 * Hook for fetching dashboard statistics with caching
 */
export const useDashboardStats = () => {
  return useQuery(
    'dashboard-stats',
    async () => {
      Logger.apiRequest('GET', '/api/v1/dashboard/');
      
      const response = await fetch('/api/v1/dashboard/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      Logger.apiResponse('GET', '/api/v1/dashboard/', response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
      retry: (failureCount, error) => {
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 3;
      },
      onError: (error) => {
        Logger.error('Dashboard stats query error:', error);
      }
    }
  );
};

/**
 * Hook for fetching tickets with caching and filtering
 */
export const useTickets = (filters = {}) => {
  return useQuery(
    ['tickets', filters],
    async () => {
      Logger.apiRequest('GET', '/api/v1/tickets/');
      
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.priority) params.append('priority', filters.priority);
      if (filters.search) params.append('search', filters.search);
      if (filters.page) params.append('page', filters.page);

      const response = await fetch(`/api/v1/tickets/?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      Logger.apiResponse('GET', '/api/v1/tickets/', response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      staleTime: 2 * 60 * 1000, // 2 minutes
      cacheTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
      retry: (failureCount, error) => {
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 3;
      },
      onError: (error) => {
        Logger.error('Tickets query error:', error);
      }
    }
  );
};

/**
 * Hook for fetching single ticket with caching
 */
export const useTicket = (ticketId) => {
  return useQuery(
    ['ticket', ticketId],
    async () => {
      Logger.apiRequest('GET', `/api/v1/tickets/${ticketId}/`);
      
      const response = await fetch(`/api/v1/tickets/${ticketId}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      Logger.apiResponse('GET', `/api/v1/tickets/${ticketId}/`, response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      enabled: !!ticketId,
      staleTime: 1 * 60 * 1000, // 1 minute
      cacheTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
      retry: (failureCount, error) => {
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 3;
      },
      onError: (error) => {
        Logger.error('Ticket query error:', error);
      }
    }
  );
};

/**
 * Hook for fetching ticket comments with caching
 */
export const useTicketComments = (ticketId) => {
  return useQuery(
    ['ticket-comments', ticketId],
    async () => {
      Logger.apiRequest('GET', `/api/v1/tickets/${ticketId}/comments/`);
      
      const response = await fetch(`/api/v1/tickets/${ticketId}/comments/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      Logger.apiResponse('GET', `/api/v1/tickets/${ticketId}/comments/`, response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      enabled: !!ticketId,
      staleTime: 30 * 1000, // 30 seconds
      cacheTime: 2 * 60 * 1000, // 2 minutes
      refetchOnWindowFocus: false,
      retry: (failureCount, error) => {
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 3;
      },
      onError: (error) => {
        Logger.error('Ticket comments query error:', error);
      }
    }
  );
};

/**
 * Hook for fetching knowledge base articles with caching
 */
export const useKnowledgeBase = (filters = {}) => {
  return useQuery(
    ['knowledge-base', filters],
    async () => {
      Logger.apiRequest('GET', '/api/v1/knowledge-base/');
      
      const params = new URLSearchParams();
      if (filters.category) params.append('category', filters.category);
      if (filters.search) params.append('search', filters.search);
      if (filters.page) params.append('page', filters.page);

      const response = await fetch(`/api/v1/knowledge-base/?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      Logger.apiResponse('GET', '/api/v1/knowledge-base/', response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      staleTime: 10 * 60 * 1000, // 10 minutes
      cacheTime: 30 * 60 * 1000, // 30 minutes
      refetchOnWindowFocus: false,
      retry: (failureCount, error) => {
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 3;
      },
      onError: (error) => {
        Logger.error('Knowledge base query error:', error);
      }
    }
  );
};

/**
 * Hook for fetching user profile with caching
 */
export const useProfile = () => {
  return useQuery(
    'profile',
    async () => {
      Logger.apiRequest('GET', '/api/v1/profile/');
      
      const response = await fetch('/api/v1/profile/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      Logger.apiResponse('GET', '/api/v1/profile/', response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 15 * 60 * 1000, // 15 minutes
      refetchOnWindowFocus: false,
      retry: (failureCount, error) => {
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 3;
      },
      onError: (error) => {
        Logger.error('Profile query error:', error);
      }
    }
  );
};

/**
 * Hook for creating tickets with optimistic updates
 */
export const useCreateTicket = () => {
  const queryClient = useQueryClient();

  return useMutation(
    async (ticketData) => {
      Logger.apiRequest('POST', '/api/v1/tickets/');
      
      const response = await fetch('/api/v1/tickets/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify(ticketData)
      });

      Logger.apiResponse('POST', '/api/v1/tickets/', response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      onSuccess: (data) => {
        Logger.info('Ticket created successfully:', data);
        
        // Invalidate and refetch tickets list
        queryClient.invalidateQueries('tickets');
        queryClient.invalidateQueries('dashboard-stats');
      },
      onError: (error) => {
        Logger.error('Ticket creation failed:', error);
      }
    }
  );
};

/**
 * Hook for updating tickets with optimistic updates
 */
export const useUpdateTicket = () => {
  const queryClient = useQueryClient();

  return useMutation(
    async ({ ticketId, updates }) => {
      Logger.apiRequest('PATCH', `/api/v1/tickets/${ticketId}/`);
      
      const response = await fetch(`/api/v1/tickets/${ticketId}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify(updates)
      });

      Logger.apiResponse('PATCH', `/api/v1/tickets/${ticketId}/`, response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      onSuccess: (data, variables) => {
        Logger.info('Ticket updated successfully:', data);
        
        // Update specific ticket in cache
        queryClient.setQueryData(['ticket', variables.ticketId], data);
        
        // Invalidate related queries
        queryClient.invalidateQueries('tickets');
        queryClient.invalidateQueries('dashboard-stats');
      },
      onError: (error) => {
        Logger.error('Ticket update failed:', error);
      }
    }
  );
};

/**
 * Hook for adding ticket comments with optimistic updates
 */
export const useAddTicketComment = () => {
  const queryClient = useQueryClient();

  return useMutation(
    async ({ ticketId, comment }) => {
      Logger.apiRequest('POST', `/api/v1/tickets/${ticketId}/comments/`);
      
      const response = await fetch(`/api/v1/tickets/${ticketId}/comments/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({ content: comment })
      });

      Logger.apiResponse('POST', `/api/v1/tickets/${ticketId}/comments/`, response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      onSuccess: (data, variables) => {
        Logger.info('Comment added successfully:', data);
        
        // Invalidate ticket comments
        queryClient.invalidateQueries(['ticket-comments', variables.ticketId]);
        
        // Update ticket in cache
        queryClient.invalidateQueries(['ticket', variables.ticketId]);
      },
      onError: (error) => {
        Logger.error('Comment addition failed:', error);
      }
    }
  );
};

/**
 * Hook for updating user profile with optimistic updates
 */
export const useUpdateProfile = () => {
  const queryClient = useQueryClient();

  return useMutation(
    async (profileData) => {
      Logger.apiRequest('PUT', '/api/v1/profile/');
      
      const response = await fetch('/api/v1/profile/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify(profileData)
      });

      Logger.apiResponse('PUT', '/api/v1/profile/', response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      onSuccess: (data) => {
        Logger.info('Profile updated successfully:', data);
        
        // Update profile in cache
        queryClient.setQueryData('profile', data);
      },
      onError: (error) => {
        Logger.error('Profile update failed:', error);
      }
    }
  );
};
