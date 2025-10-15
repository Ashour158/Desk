import { useQuery, useMutation, useQueryClient } from 'react-query';
import Logger from '../utils/logger';

/**
 * React Query hooks for advanced data caching and synchronization
 */

/**
 * Hook for fetching tickets with advanced caching
 * @param {Object} filters - Filter parameters
 * @param {Object} options - Query options
 * @returns {Object} Query result
 */
export const useTicketsQuery = (filters = {}, options = {}) => {
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

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      staleTime: 2 * 60 * 1000, // 2 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
      refetchOnMount: true,
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
      ...options
    }
  );
};

/**
 * Hook for fetching single ticket with caching
 * @param {string|number} ticketId - Ticket ID
 * @param {Object} options - Query options
 * @returns {Object} Query result
 */
export const useTicketQuery = (ticketId, options = {}) => {
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

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      enabled: !!ticketId,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 30 * 60 * 1000, // 30 minutes
      refetchOnWindowFocus: false,
      retry: 3,
      ...options
    }
  );
};

/**
 * Hook for fetching knowledge base articles with caching
 * @param {Object} filters - Filter parameters
 * @param {Object} options - Query options
 * @returns {Object} Query result
 */
export const useKnowledgeBaseQuery = (filters = {}, options = {}) => {
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

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      staleTime: 10 * 60 * 1000, // 10 minutes
      cacheTime: 60 * 60 * 1000, // 1 hour
      refetchOnWindowFocus: false,
      retry: 3,
      ...options
    }
  );
};

/**
 * Hook for fetching dashboard statistics with caching
 * @param {Object} options - Query options
 * @returns {Object} Query result
 */
export const useDashboardStatsQuery = (options = {}) => {
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

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 15 * 60 * 1000, // 15 minutes
      refetchOnWindowFocus: false,
      retry: 3,
      ...options
    }
  );
};

/**
 * Hook for creating tickets with optimistic updates
 * @param {Object} options - Mutation options
 * @returns {Object} Mutation result
 */
export const useCreateTicketMutation = (options = {}) => {
  const queryClient = useQueryClient();
  
  return useMutation(
    async (ticketData) => {
      Logger.apiRequest('POST', '/api/v1/tickets/', { body: 'Present' });
      
      const response = await fetch('/api/v1/tickets/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify(ticketData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      onMutate: async (newTicket) => {
        // Cancel outgoing refetches
        await queryClient.cancelQueries('tickets');
        
        // Snapshot previous value
        const previousTickets = queryClient.getQueryData('tickets');
        
        // Optimistically update
        queryClient.setQueryData('tickets', (old) => ({
          ...old,
          results: [newTicket, ...(old?.results || [])]
        }));
        
        return { previousTickets };
      },
      onError: (err, newTicket, context) => {
        // Rollback on error
        queryClient.setQueryData('tickets', context.previousTickets);
      },
      onSettled: () => {
        // Refetch after error or success
        queryClient.invalidateQueries('tickets');
      },
      ...options
    }
  );
};

/**
 * Hook for updating tickets with optimistic updates
 * @param {Object} options - Mutation options
 * @returns {Object} Mutation result
 */
export const useUpdateTicketMutation = (options = {}) => {
  const queryClient = useQueryClient();
  
  return useMutation(
    async ({ ticketId, ...updateData }) => {
      Logger.apiRequest('PATCH', `/api/v1/tickets/${ticketId}/`, { body: 'Present' });
      
      const response = await fetch(`/api/v1/tickets/${ticketId}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify(updateData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      onMutate: async ({ ticketId, ...updateData }) => {
        // Cancel outgoing refetches
        await queryClient.cancelQueries(['ticket', ticketId]);
        await queryClient.cancelQueries('tickets');
        
        // Snapshot previous values
        const previousTicket = queryClient.getQueryData(['ticket', ticketId]);
        const previousTickets = queryClient.getQueryData('tickets');
        
        // Optimistically update
        queryClient.setQueryData(['ticket', ticketId], (old) => ({
          ...old,
          ...updateData
        }));
        
        queryClient.setQueryData('tickets', (old) => ({
          ...old,
          results: old?.results?.map(ticket => 
            ticket.id === ticketId ? { ...ticket, ...updateData } : ticket
          )
        }));
        
        return { previousTicket, previousTickets };
      },
      onError: (err, variables, context) => {
        // Rollback on error
        if (context.previousTicket) {
          queryClient.setQueryData(['ticket', variables.ticketId], context.previousTicket);
        }
        if (context.previousTickets) {
          queryClient.setQueryData('tickets', context.previousTickets);
        }
      },
      onSettled: (data, error, variables) => {
        // Refetch after error or success
        queryClient.invalidateQueries(['ticket', variables.ticketId]);
        queryClient.invalidateQueries('tickets');
      },
      ...options
    }
  );
};

/**
 * Hook for adding comments with optimistic updates
 * @param {Object} options - Mutation options
 * @returns {Object} Mutation result
 */
export const useAddCommentMutation = (options = {}) => {
  const queryClient = useQueryClient();
  
  return useMutation(
    async ({ ticketId, content, isInternal = false }) => {
      Logger.apiRequest('POST', `/api/v1/tickets/${ticketId}/comments/`, { body: 'Present' });
      
      const response = await fetch(`/api/v1/tickets/${ticketId}/comments/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({ content, is_internal: isInternal })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    },
    {
      onMutate: async ({ ticketId, content, isInternal }) => {
        // Cancel outgoing refetches
        await queryClient.cancelQueries(['ticket', ticketId]);
        
        // Snapshot previous value
        const previousTicket = queryClient.getQueryData(['ticket', ticketId]);
        
        // Create optimistic comment
        const optimisticComment = {
          id: `temp-${Date.now()}`,
          content,
          is_internal: isInternal,
          created_at: new Date().toISOString(),
          author: {
            first_name: 'You',
            last_name: ''
          }
        };
        
        // Optimistically update
        queryClient.setQueryData(['ticket', ticketId], (old) => ({
          ...old,
          comments: [...(old?.comments || []), optimisticComment]
        }));
        
        return { previousTicket };
      },
      onError: (err, variables, context) => {
        // Rollback on error
        if (context.previousTicket) {
          queryClient.setQueryData(['ticket', variables.ticketId], context.previousTicket);
        }
      },
      onSettled: (data, error, variables) => {
        // Refetch after error or success
        queryClient.invalidateQueries(['ticket', variables.ticketId]);
      },
      ...options
    }
  );
};

/**
 * Hook for prefetching data
 * @param {string} queryKey - Query key
 * @param {Function} queryFn - Query function
 * @param {Object} options - Prefetch options
 */
export const usePrefetchQuery = (queryKey, queryFn, options = {}) => {
  const queryClient = useQueryClient();
  
  return (queryKey, queryFn, options) => {
    queryClient.prefetchQuery(queryKey, queryFn, {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      ...options
    });
  };
};

/**
 * Hook for invalidating queries
 * @param {string|Array} queryKey - Query key to invalidate
 */
export const useInvalidateQuery = (queryKey) => {
  const queryClient = useQueryClient();
  
  return () => {
    queryClient.invalidateQueries(queryKey);
  };
};

/**
 * Hook for clearing all queries
 */
export const useClearAllQueries = () => {
  const queryClient = useQueryClient();
  
  return () => {
    queryClient.clear();
  };
};

export default {
  useTicketsQuery,
  useTicketQuery,
  useKnowledgeBaseQuery,
  useDashboardStatsQuery,
  useCreateTicketMutation,
  useUpdateTicketMutation,
  useAddCommentMutation,
  usePrefetchQuery,
  useInvalidateQuery,
  useClearAllQueries
};
