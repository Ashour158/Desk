import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import PropTypes from 'prop-types';
import { memo } from 'react';

/**
 * Virtualized Ticket List Component
 * Efficiently renders large lists of tickets with virtual scrolling
 */
const VirtualizedTicketList = memo(({ 
  tickets = [], 
  onTicketClick, 
  onTicketUpdate,
  height = 600,
  itemHeight = 80,
  overscan = 5,
  className = '',
  ...props 
}) => {
  const [scrollTop, setScrollTop] = useState(0);
  const [containerHeight, setContainerHeight] = useState(height);
  const containerRef = useRef(null);
  const scrollElementRef = useRef(null);

  // Calculate visible range
  const visibleRange = useMemo(() => {
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      tickets.length - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );
    
    return { startIndex, endIndex };
  }, [scrollTop, containerHeight, itemHeight, overscan, tickets.length]);

  // Get visible items
  const visibleItems = useMemo(() => {
    const { startIndex, endIndex } = visibleRange;
    return tickets.slice(startIndex, endIndex + 1).map((ticket, index) => ({
      ...ticket,
      index: startIndex + index,
      top: (startIndex + index) * itemHeight
    }));
  }, [tickets, visibleRange, itemHeight]);

  // Calculate total height
  const totalHeight = tickets.length * itemHeight;

  // Handle scroll
  const handleScroll = useCallback((event) => {
    const newScrollTop = event.target.scrollTop;
    setScrollTop(newScrollTop);
  }, []);

  // Handle resize
  const handleResize = useCallback(() => {
    if (containerRef.current) {
      setContainerHeight(containerRef.current.clientHeight);
    }
  }, []);

  // Handle ticket click
  const handleTicketClick = useCallback((ticket) => {
    if (onTicketClick) {
      onTicketClick(ticket);
    }
  }, [onTicketClick]);

  // Handle ticket update
  const handleTicketUpdate = useCallback((ticketId, updates) => {
    if (onTicketUpdate) {
      onTicketUpdate(ticketId, updates);
    }
  }, [onTicketUpdate]);

  // Set up resize observer
  useEffect(() => {
    if (containerRef.current) {
      setContainerHeight(containerRef.current.clientHeight);
      
      const resizeObserver = new ResizeObserver(handleResize);
      resizeObserver.observe(containerRef.current);
      
      return () => resizeObserver.disconnect();
    }
  }, [handleResize]);

  // Scroll to specific ticket
  const scrollToTicket = useCallback((ticketId) => {
    const ticketIndex = tickets.findIndex(ticket => ticket.id === ticketId);
    if (ticketIndex !== -1 && scrollElementRef.current) {
      const targetScrollTop = ticketIndex * itemHeight;
      scrollElementRef.current.scrollTop = targetScrollTop;
    }
  }, [tickets, itemHeight]);

  // Scroll to top
  const scrollToTop = useCallback(() => {
    if (scrollElementRef.current) {
      scrollElementRef.current.scrollTop = 0;
    }
  }, []);

  // Scroll to bottom
  const scrollToBottom = useCallback(() => {
    if (scrollElementRef.current) {
      scrollElementRef.current.scrollTop = totalHeight;
    }
  }, [totalHeight]);

  return (
    <div 
      ref={containerRef}
      className={`virtualized-ticket-list ${className}`}
      style={{ height: `${height}px`, position: 'relative', overflow: 'hidden' }}
      {...props}
    >
      {/* Scrollable container */}
      <div
        ref={scrollElementRef}
        className="virtualized-scroll-container"
        style={{
          height: '100%',
          overflow: 'auto',
          position: 'relative'
        }}
        onScroll={handleScroll}
      >
        {/* Virtual spacer for total height */}
        <div style={{ height: `${totalHeight}px`, position: 'relative' }}>
          {/* Visible items */}
          <div
            className="virtualized-items"
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              transform: `translateY(${visibleRange.startIndex * itemHeight}px)`
            }}
          >
            {visibleItems.map((ticket) => (
              <VirtualizedTicketItem
                key={ticket.id}
                ticket={ticket}
                height={itemHeight}
                onClick={() => handleTicketClick(ticket)}
                onUpdate={(updates) => handleTicketUpdate(ticket.id, updates)}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Scroll indicators */}
      {scrollTop > 100 && (
        <button
          className="scroll-to-top-btn"
          onClick={scrollToTop}
          style={{
            position: 'absolute',
            top: '10px',
            right: '10px',
            zIndex: 10,
            background: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '50%',
            width: '40px',
            height: '40px',
            cursor: 'pointer',
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
          }}
          title="Scroll to top"
        >
          ↑
        </button>
      )}

      {scrollTop < totalHeight - containerHeight - 100 && (
        <button
          className="scroll-to-bottom-btn"
          onClick={scrollToBottom}
          style={{
            position: 'absolute',
            bottom: '10px',
            right: '10px',
            zIndex: 10,
            background: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '50%',
            width: '40px',
            height: '40px',
            cursor: 'pointer',
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
          }}
          title="Scroll to bottom"
        >
          ↓
        </button>
      )}

      {/* Loading indicator for large datasets */}
      {tickets.length > 1000 && (
        <div
          className="virtualized-loading-indicator"
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            background: 'rgba(255, 255, 255, 0.9)',
            padding: '1rem',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            fontSize: '0.9rem',
            color: '#666'
          }}
        >
          Virtualizing {tickets.length} tickets...
        </div>
      )}
    </div>
  );
});

VirtualizedTicketList.displayName = 'VirtualizedTicketList';

VirtualizedTicketList.propTypes = {
  tickets: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    subject: PropTypes.string.isRequired,
    status: PropTypes.string.isRequired,
    priority: PropTypes.string.isRequired,
    created_at: PropTypes.string.isRequired,
    assigned_agent: PropTypes.string,
    customer: PropTypes.string
  })).isRequired,
  onTicketClick: PropTypes.func,
  onTicketUpdate: PropTypes.func,
  height: PropTypes.number,
  itemHeight: PropTypes.number,
  overscan: PropTypes.number,
  className: PropTypes.string
};

/**
 * Individual ticket item component
 */
const VirtualizedTicketItem = memo(({ ticket, height, onClick, onUpdate }) => {
  const [isHovered, setIsHovered] = useState(false);

  const handleClick = useCallback(() => {
    if (onClick) {
      onClick(ticket);
    }
  }, [onClick, ticket]);

  const handleStatusChange = useCallback((newStatus) => {
    if (onUpdate) {
      onUpdate({ status: newStatus });
    }
  }, [onUpdate]);

  const getStatusColor = (status) => {
    const colors = {
      open: '#28a745',
      in_progress: '#ffc107',
      pending: '#17a2b8',
      resolved: '#6c757d',
      closed: '#343a40'
    };
    return colors[status] || '#6c757d';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      urgent: '#dc3545',
      high: '#fd7e14',
      medium: '#ffc107',
      low: '#28a745'
    };
    return colors[priority] || '#6c757d';
  };

  return (
    <div
      className="virtualized-ticket-item"
      style={{
        height: `${height}px`,
        padding: '12px 16px',
        borderBottom: '1px solid #e9ecef',
        cursor: 'pointer',
        transition: 'background-color 0.2s ease',
        backgroundColor: isHovered ? '#f8f9fa' : 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleClick}
    >
      {/* Ticket info */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
          <span
            style={{
              fontSize: '0.9rem',
              fontWeight: '600',
              color: '#495057',
              marginRight: '8px'
            }}
          >
            #{ticket.ticket_number || ticket.id}
          </span>
          <span
            style={{
              fontSize: '0.8rem',
              padding: '2px 6px',
              borderRadius: '4px',
              backgroundColor: getStatusColor(ticket.status),
              color: 'white',
              textTransform: 'uppercase',
              fontWeight: '500'
            }}
          >
            {ticket.status}
          </span>
          <span
            style={{
              fontSize: '0.8rem',
              padding: '2px 6px',
              borderRadius: '4px',
              backgroundColor: getPriorityColor(ticket.priority),
              color: 'white',
              textTransform: 'uppercase',
              fontWeight: '500',
              marginLeft: '8px'
            }}
          >
            {ticket.priority}
          </span>
        </div>
        
        <div
          style={{
            fontSize: '0.9rem',
            fontWeight: '500',
            color: '#212529',
            marginBottom: '4px',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}
        >
          {ticket.subject}
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', fontSize: '0.8rem', color: '#6c757d' }}>
          <span>{ticket.customer}</span>
          {ticket.assigned_agent && (
            <>
              <span style={{ margin: '0 8px' }}>•</span>
              <span>Assigned to {ticket.assigned_agent}</span>
            </>
          )}
          <span style={{ margin: '0 8px' }}>•</span>
          <span>{new Date(ticket.created_at).toLocaleDateString()}</span>
        </div>
      </div>

      {/* Quick actions */}
      {isHovered && (
        <div style={{ display: 'flex', gap: '8px', marginLeft: '16px' }}>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleStatusChange('in_progress');
            }}
            style={{
              padding: '4px 8px',
              fontSize: '0.8rem',
              border: '1px solid #007bff',
              backgroundColor: 'transparent',
              color: '#007bff',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Start
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleStatusChange('resolved');
            }}
            style={{
              padding: '4px 8px',
              fontSize: '0.8rem',
              border: '1px solid #28a745',
              backgroundColor: 'transparent',
              color: '#28a745',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Resolve
          </button>
        </div>
      )}
    </div>
  );
});

VirtualizedTicketItem.displayName = 'VirtualizedTicketItem';

VirtualizedTicketItem.propTypes = {
  ticket: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    ticket_number: PropTypes.string,
    subject: PropTypes.string.isRequired,
    status: PropTypes.string.isRequired,
    priority: PropTypes.string.isRequired,
    created_at: PropTypes.string.isRequired,
    assigned_agent: PropTypes.string,
    customer: PropTypes.string.isRequired
  }).isRequired,
  height: PropTypes.number.isRequired,
  onClick: PropTypes.func,
  onUpdate: PropTypes.func
};

export default VirtualizedTicketList;