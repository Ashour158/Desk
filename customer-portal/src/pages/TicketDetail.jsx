import React, { useState, useEffect, memo, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import PropTypes from 'prop-types';
import Logger from '../utils/logger';

/**
 * Ticket detail page component
 * @param {Object} props - Component props
 */
const TicketDetail = ({ user }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState(null);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTicketDetails();
  }, [id]);

  /**
   * Fetch ticket details and comments
   */
  const fetchTicketDetails = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      Logger.apiRequest('GET', `/api/v1/tickets/${id}/`);
      
      const response = await fetch(`/api/v1/tickets/${id}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      Logger.apiResponse('GET', `/api/v1/tickets/${id}/`, response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setTicket(data);
      setComments(data.comments || []);
      
      Logger.info('Ticket details loaded successfully', {
        ticketId: data.id,
        status: data.status
      });
      
    } catch (error) {
      Logger.error('Failed to load ticket details:', error, {
        ticketId: id,
        status: error?.response?.status
      });
      setError('Failed to load ticket details');
    } finally {
      setLoading(false);
    }
  }, [id]);

  /**
   * Handle adding a new comment
   */
  const handleAddComment = useCallback(async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      setSubmitting(true);
      
      Logger.apiRequest('POST', `/api/v1/tickets/${id}/comments/`, { body: 'Present' });
      
      const response = await fetch(`/api/v1/tickets/${id}/comments/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
          content: newComment,
          is_internal: false
        })
      });

      Logger.apiResponse('POST', `/api/v1/tickets/${id}/comments/`, response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setComments(prev => [...prev, data]);
      setNewComment('');
      
      Logger.info('Comment added successfully', {
        ticketId: id,
        commentId: data.id
      });
      
      Logger.userAction('comment_added', {
        ticketId: id,
        commentId: data.id
      });
      
    } catch (error) {
      Logger.error('Failed to add comment:', error, {
        ticketId: id,
        status: error?.response?.status
      });
      setError('Failed to add comment');
    } finally {
      setSubmitting(false);
    }
  }, [id, newComment]);

  /**
   * Get status badge - memoized for performance
   */
  const getStatusBadge = useCallback((status) => {
    const statusConfig = {
      'open': { class: 'bg-yellow-100 text-yellow-800', text: 'Open' },
      'in_progress': { class: 'bg-blue-100 text-blue-800', text: 'In Progress' },
      'pending': { class: 'bg-gray-100 text-gray-800', text: 'Pending' },
      'resolved': { class: 'bg-green-100 text-green-800', text: 'Resolved' },
      'closed': { class: 'bg-red-100 text-red-800', text: 'Closed' }
    };

    const config = statusConfig[status] || { class: 'bg-gray-100 text-gray-800', text: status };
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.class}`}>
        {config.text}
      </span>
    );
  }, []);

  /**
   * Get priority badge - memoized for performance
   */
  const getPriorityBadge = useCallback((priority) => {
    const priorityConfig = {
      'low': { class: 'bg-green-100 text-green-800', text: 'Low' },
      'medium': { class: 'bg-yellow-100 text-yellow-800', text: 'Medium' },
      'high': { class: 'bg-orange-100 text-orange-800', text: 'High' },
      'urgent': { class: 'bg-red-100 text-red-800', text: 'Urgent' }
    };

    const config = priorityConfig[priority] || { class: 'bg-gray-100 text-gray-800', text: priority };
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.class}`}>
        {config.text}
      </span>
    );
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !ticket) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">
          <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Ticket</h3>
        <p className="text-gray-500 mb-4">{error || 'Ticket not found'}</p>
        <button
          onClick={() => navigate('/tickets')}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Back to Tickets
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Ticket Header */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {ticket.subject}
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                Ticket #{ticket.ticket_number} • Created {format(new Date(ticket.created_at), 'MMM dd, yyyy')}
              </p>
            </div>
            <div className="flex space-x-3">
              {getStatusBadge(ticket.status)}
              {getPriorityBadge(ticket.priority)}
            </div>
          </div>
        </div>
      </div>

      {/* Ticket Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Description</h3>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">{ticket.description}</p>
              </div>
            </div>
          </div>

          {/* Comments Section */}
          <div className="bg-white shadow rounded-lg mt-6">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Comments</h3>
              
              {/* Comments List */}
              <div className="space-y-4 mb-6">
                {comments.map((comment) => (
                  <div key={comment.id} className="border-l-4 border-blue-200 pl-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-900">
                          {comment.author?.first_name} {comment.author?.last_name}
                        </span>
                        <span className="text-xs text-gray-500">
                          {format(new Date(comment.created_at), 'MMM dd, yyyy HH:mm')}
                        </span>
                        {comment.is_internal && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                            Internal
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="mt-2">
                      <p className="text-gray-700 whitespace-pre-wrap">{comment.content}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Add Comment Form */}
              <form onSubmit={handleAddComment} className="border-t pt-4">
                <div>
                  <label htmlFor="newComment" className="block text-sm font-medium text-gray-700 mb-2">
                    Add a comment
                  </label>
                  <textarea
                    id="newComment"
                    rows={4}
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    placeholder="Type your comment here..."
                    required
                  />
                </div>
                <div className="mt-4 flex justify-end">
                  <button
                    type="submit"
                    disabled={submitting || !newComment.trim()}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {submitting ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Adding...
                      </>
                    ) : (
                      'Add Comment'
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Ticket Info */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Ticket Information</h3>
              <dl className="space-y-3">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Status</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {getStatusBadge(ticket.status)}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Priority</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {getPriorityBadge(ticket.priority)}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Category</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {ticket.category || 'Not specified'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Assigned To</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {ticket.assigned_agent ? 
                      `${ticket.assigned_agent.first_name} ${ticket.assigned_agent.last_name}` : 
                      'Unassigned'
                    }
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Created</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {format(new Date(ticket.created_at), 'MMM dd, yyyy HH:mm')}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {format(new Date(ticket.updated_at), 'MMM dd, yyyy HH:mm')}
                  </dd>
                </div>
              </dl>
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Actions</h3>
              <div className="space-y-3">
                <button className="w-full inline-flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                  <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                  </svg>
                  Download Ticket
                </button>
                <button className="w-full inline-flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                  <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                  </svg>
                  Share Ticket
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

TicketDetail.propTypes = {
  user: PropTypes.shape({
    id: PropTypes.number,
    first_name: PropTypes.string,
    last_name: PropTypes.string,
    email: PropTypes.string,
  }),
};

TicketDetail.defaultProps = {
  user: null,
};

TicketDetail.displayName = 'TicketDetail';

export default memo(TicketDetail);
