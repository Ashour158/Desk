import React, { useState, useEffect, memo, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import PropTypes from 'prop-types';
import Logger from '../utils/logger';

/**
 * TicketList component for displaying and filtering tickets
 * @param {Object} props - Component props
 * @param {Function} props.onTicketSelect - Callback when ticket is selected
 * @param {Object} props.initialFilters - Initial filter values
 */
const TicketList = memo(({ onTicketSelect, initialFilters = {} }) => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [filters, setFilters] = useState({
    status: '',
    priority: '',
    search: '',
    ...initialFilters
  });

  useEffect(() => {
    fetchTickets();
  }, [fetchTickets]);

  /**
   * Fetch tickets from API with comprehensive error handling
   */
  const fetchTickets = useCallback(async () => {
    const startTime = performance.now();
    
    try {
      setLoading(true);
      setError(null);
      
      Logger.apiRequest('GET', '/api/v1/tickets/');
      
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.priority) params.append('priority', filters.priority);
      if (filters.search) params.append('search', filters.search);

      const response = await fetch(`/api/v1/tickets/?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        }
      });

      Logger.apiResponse('GET', '/api/v1/tickets/', response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setTickets(data.results || []);
      setRetryCount(0); // Reset retry count on success
      
      Logger.info('Tickets fetched successfully', {
        count: data.results?.length || 0,
        filters
      });
      
    } catch (error) {
      Logger.error('Error fetching tickets:', error, {
        filters,
        retryCount,
        status: error?.response?.status
      });
      
      setError({
        message: 'Failed to load tickets. Please try again.',
        type: 'fetch_error',
        retryable: true
      });
      
      // Auto-retry logic
      if (retryCount < 3) {
        setTimeout(() => {
          setRetryCount(prev => prev + 1);
          fetchTickets();
        }, Math.pow(2, retryCount) * 1000); // Exponential backoff
      }
    } finally {
      setLoading(false);
      
      const duration = performance.now() - startTime;
      Logger.performance('fetchTickets', duration, {
        ticketCount: tickets.length,
        filters
      });
    }
  }, [filters, tickets.length, getCsrfToken]);

  /**
   * Get CSRF token from cookies
   * @returns {string} CSRF token
   */
  const getCsrfToken = useCallback(() => {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'csrftoken') {
        return value;
      }
    }
    return '';
  }, []);

  const getStatusBadge = useCallback((status) => {
    const statusConfig = {
      'open': { class: 'bg-primary', text: 'Open' },
      'in_progress': { class: 'bg-warning', text: 'In Progress' },
      'pending': { class: 'bg-info', text: 'Pending' },
      'resolved': { class: 'bg-success', text: 'Resolved' },
      'closed': { class: 'bg-secondary', text: 'Closed' }
    };
    
    const config = statusConfig[status] || { class: 'bg-secondary', text: status };
    return (
      <span className={`badge ${config.class}`}>
        {config.text}
      </span>
    );
  }, []);

  const getPriorityBadge = useCallback((priority) => {
    const priorityConfig = {
      'low': { class: 'bg-success', text: 'Low' },
      'medium': { class: 'bg-warning', text: 'Medium' },
      'high': { class: 'bg-danger', text: 'High' },
      'urgent': { class: 'bg-dark', text: 'Urgent' }
    };
    
    const config = priorityConfig[priority] || { class: 'bg-secondary', text: priority };
    return (
      <span className={`badge ${config.class}`}>
        {config.text}
      </span>
    );
  }, []);

  const handleFilterChange = useCallback((field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  }, []);

  /**
   * Handle retry action
   */
  const handleRetry = useCallback(() => {
    setRetryCount(0);
    setError(null);
    fetchTickets();
  }, [fetchTickets]);

  /**
   * Handle ticket selection
   * @param {Object} ticket - Selected ticket
   */
  const handleTicketSelect = useCallback((ticket) => {
    if (onTicketSelect) {
      onTicketSelect(ticket);
    }
    Logger.userAction('ticket_selected', { ticketId: ticket.id });
  }, [onTicketSelect]);

  // Loading state
  if (loading) {
    return (
      <div className="text-center py-4">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p className="mt-2 text-muted">Loading tickets...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="text-center py-4">
        <div className="alert alert-danger">
          <i className="fas fa-exclamation-triangle me-2"></i>
          {error.message}
        </div>
        {error.retryable && (
          <button 
            className="btn btn-primary"
            onClick={handleRetry}
            disabled={retryCount >= 3}
          >
            <i className="fas fa-redo me-1"></i>
            Try Again
            {retryCount > 0 && ` (${retryCount}/3)`}
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="container-fluid">
      <div className="row">
        <div className="col-12">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2>My Tickets</h2>
            <Link to="/tickets/create" className="btn btn-primary">
              <i className="fas fa-plus me-2"></i>
              New Ticket
            </Link>
          </div>

          {/* Filters */}
          <div className="card mb-4">
            <div className="card-body">
              <div className="row g-3">
                <div className="col-md-3">
                  <label className="form-label">Status</label>
                  <select 
                    className="form-select"
                    value={filters.status}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                  >
                    <option value="">All Statuses</option>
                    <option value="open">Open</option>
                    <option value="in_progress">In Progress</option>
                    <option value="pending">Pending</option>
                    <option value="resolved">Resolved</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>
                <div className="col-md-3">
                  <label className="form-label">Priority</label>
                  <select 
                    className="form-select"
                    value={filters.priority}
                    onChange={(e) => handleFilterChange('priority', e.target.value)}
                  >
                    <option value="">All Priorities</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
                <div className="col-md-6">
                  <label className="form-label">Search</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Search tickets..."
                    value={filters.search}
                    onChange={(e) => handleFilterChange('search', e.target.value)}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Tickets List */}
          <div className="card">
            <div className="card-body">
              {tickets.length === 0 ? (
                <div className="text-center py-5">
                  <i className="fas fa-ticket-alt fa-3x text-muted mb-3"></i>
                  <h5 className="text-muted">No tickets found</h5>
                  <p className="text-muted">Create your first ticket to get started.</p>
                  <Link to="/tickets/create" className="btn btn-primary">
                    Create Ticket
                  </Link>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead>
                      <tr>
                        <th>Ticket #</th>
                        <th>Subject</th>
                        <th>Status</th>
                        <th>Priority</th>
                        <th>Assigned To</th>
                        <th>Created</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tickets.map(ticket => (
                        <tr key={ticket.id}>
                          <td>
                            <strong>{ticket.ticket_number}</strong>
                          </td>
                          <td>
                            <div>
                              <div className="fw-bold">{ticket.subject}</div>
                              <small className="text-muted">
                                {ticket.description?.substring(0, 100)}
                                {ticket.description?.length > 100 && '...'}
                              </small>
                            </div>
                          </td>
                          <td>
                            {getStatusBadge(ticket.status)}
                          </td>
                          <td>
                            {getPriorityBadge(ticket.priority)}
                          </td>
                          <td>
                            {ticket.assigned_agent ? (
                              <span className="text-muted">
                                {ticket.assigned_agent.full_name}
                              </span>
                            ) : (
                              <span className="text-muted">Unassigned</span>
                            )}
                          </td>
                          <td>
                            <small className="text-muted">
                              {format(new Date(ticket.created_at), 'MMM dd, yyyy')}
                            </small>
                          </td>
                          <td>
                            <Link 
                              to={`/tickets/${ticket.id}`}
                              className="btn btn-sm btn-outline-primary"
                              onClick={() => handleTicketSelect(ticket)}
                            >
                              View
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});

// PropTypes for component validation
TicketList.propTypes = {
  onTicketSelect: PropTypes.func,
  initialFilters: PropTypes.shape({
    status: PropTypes.string,
    priority: PropTypes.string,
    search: PropTypes.string
  })
};

TicketList.defaultProps = {
  onTicketSelect: null,
  initialFilters: {}
};

export default TicketList;
