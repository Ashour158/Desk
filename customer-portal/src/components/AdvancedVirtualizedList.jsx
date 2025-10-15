import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import PropTypes from 'prop-types';
import { memo } from 'react';

/**
 * Advanced Virtualized List Component
 * Optimized for very large datasets (1000+ items) with enhanced performance
 */
const AdvancedVirtualizedList = memo(({ 
  items = [], 
  itemHeight = 80,
  containerHeight = 600,
  overscan = 10,
  onItemClick,
  onItemUpdate,
  renderItem,
  className = '',
  enableInfiniteScroll = true,
  loadMoreThreshold = 100,
  onLoadMore,
  hasMore = false,
  loading = false,
  ...props 
}) => {
  const [scrollTop, setScrollTop] = useState(0);
  const [containerHeightState, setContainerHeightState] = useState(containerHeight);
  const [isScrolling, setIsScrolling] = useState(false);
  const [scrollDirection, setScrollDirection] = useState('down');
  const containerRef = useRef(null);
  const scrollElementRef = useRef(null);
  const lastScrollTop = useRef(0);
  const scrollTimeout = useRef(null);
  const intersectionObserver = useRef(null);

  // Calculate visible range with enhanced overscan
  const visibleRange = useMemo(() => {
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      items.length - 1,
      Math.ceil((scrollTop + containerHeightState) / itemHeight) + overscan
    );
    
    return { startIndex, endIndex };
  }, [scrollTop, containerHeightState, itemHeight, overscan, items.length]);

  // Get visible items with enhanced performance
  const visibleItems = useMemo(() => {
    const { startIndex, endIndex } = visibleRange;
    return items.slice(startIndex, endIndex + 1).map((item, index) => ({
      ...item,
      index: startIndex + index,
      top: (startIndex + index) * itemHeight,
      isVisible: true
    }));
  }, [items, visibleRange, itemHeight]);

  // Calculate total height
  const totalHeight = items.length * itemHeight;

  // Enhanced scroll handling with direction detection
  const handleScroll = useCallback((event) => {
    const newScrollTop = event.target.scrollTop;
    const direction = newScrollTop > lastScrollTop.current ? 'down' : 'up';
    
    setScrollTop(newScrollTop);
    setScrollDirection(direction);
    setIsScrolling(true);
    lastScrollTop.current = newScrollTop;

    // Clear existing timeout
    if (scrollTimeout.current) {
      clearTimeout(scrollTimeout.current);
    }

    // Set timeout to detect scroll end
    scrollTimeout.current = setTimeout(() => {
      setIsScrolling(false);
    }, 150);

    // Check for infinite scroll
    if (enableInfiniteScroll && hasMore && !loading) {
      const scrollPercentage = (newScrollTop + containerHeightState) / totalHeight;
      if (scrollPercentage > 0.8) {
        onLoadMore?.();
      }
    }
  }, [containerHeightState, totalHeight, enableInfiniteScroll, hasMore, loading, onLoadMore]);

  // Enhanced resize handling
  const handleResize = useCallback(() => {
    if (containerRef.current) {
      setContainerHeightState(containerRef.current.clientHeight);
    }
  }, []);

  // Set up intersection observer for performance monitoring
  useEffect(() => {
    if (containerRef.current) {
      intersectionObserver.current = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              // Item is visible, could trigger additional optimizations
            }
          });
        },
        {
          root: scrollElementRef.current,
          rootMargin: '50px',
          threshold: 0.1
        }
      );
    }

    return () => {
      if (intersectionObserver.current) {
        intersectionObserver.current.disconnect();
      }
    };
  }, []);

  // Set up resize observer
  useEffect(() => {
    if (containerRef.current) {
      const resizeObserver = new ResizeObserver(handleResize);
      resizeObserver.observe(containerRef.current);
      
      return () => resizeObserver.disconnect();
    }
  }, [handleResize]);

  // Scroll to specific item
  const scrollToItem = useCallback((index) => {
    if (scrollElementRef.current) {
      const targetScrollTop = index * itemHeight;
      scrollElementRef.current.scrollTop = targetScrollTop;
    }
  }, [itemHeight]);

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

  // Get scroll position info
  const getScrollInfo = useCallback(() => {
    const scrollPercentage = (scrollTop / (totalHeight - containerHeightState)) * 100;
    return {
      scrollTop,
      scrollPercentage: Math.min(100, Math.max(0, scrollPercentage)),
      isAtTop: scrollTop === 0,
      isAtBottom: scrollTop >= totalHeight - containerHeightState,
      direction: scrollDirection,
      isScrolling
    };
  }, [scrollTop, totalHeight, containerHeightState, scrollDirection, isScrolling]);

  return (
    <div 
      ref={containerRef}
      className={`advanced-virtualized-list ${className}`}
      style={{ height: `${containerHeight}px`, position: 'relative', overflow: 'hidden' }}
      {...props}
    >
      {/* Scrollable container */}
      <div
        ref={scrollElementRef}
        className="advanced-virtualized-scroll-container"
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
            className="advanced-virtualized-items"
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              transform: `translateY(${visibleRange.startIndex * itemHeight}px)`
            }}
          >
            {visibleItems.map((item) => (
              <VirtualizedItem
                key={item.id || item.index}
                item={item}
                height={itemHeight}
                onClick={() => onItemClick?.(item)}
                onUpdate={(updates) => onItemUpdate?.(item.id, updates)}
                renderItem={renderItem}
                isScrolling={isScrolling}
                scrollDirection={scrollDirection}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Enhanced scroll indicators */}
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
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
            transition: 'all 0.3s ease'
          }}
          title="Scroll to top"
        >
          ↑
        </button>
      )}

      {scrollTop < totalHeight - containerHeightState - 100 && (
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
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
            transition: 'all 0.3s ease'
          }}
          title="Scroll to bottom"
        >
          ↓
        </button>
      )}

      {/* Scroll progress indicator */}
      <div
        className="scroll-progress-indicator"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          background: 'rgba(0, 123, 255, 0.3)',
          zIndex: 5
        }}
      >
        <div
          style={{
            height: '100%',
            background: '#007bff',
            width: `${getScrollInfo().scrollPercentage}%`,
            transition: 'width 0.1s ease'
          }}
        />
      </div>

      {/* Loading indicator for infinite scroll */}
      {loading && (
        <div
          className="infinite-scroll-loading"
          style={{
            position: 'absolute',
            bottom: '20px',
            left: '50%',
            transform: 'translateX(-50%)',
            background: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            padding: '0.5rem 1rem',
            borderRadius: '20px',
            fontSize: '0.875rem',
            zIndex: 10
          }}
        >
          Loading more items...
        </div>
      )}

      {/* Performance indicator for large datasets */}
      {items.length > 1000 && (
        <div
          className="performance-indicator"
          style={{
            position: 'absolute',
            top: '10px',
            left: '10px',
            background: 'rgba(0, 0, 0, 0.7)',
            color: 'white',
            padding: '0.25rem 0.5rem',
            borderRadius: '4px',
            fontSize: '0.75rem',
            zIndex: 10
          }}
        >
          Virtualizing {items.length} items
        </div>
      )}
    </div>
  );
});

AdvancedVirtualizedList.displayName = 'AdvancedVirtualizedList';

AdvancedVirtualizedList.propTypes = {
  items: PropTypes.array.isRequired,
  itemHeight: PropTypes.number,
  containerHeight: PropTypes.number,
  overscan: PropTypes.number,
  onItemClick: PropTypes.func,
  onItemUpdate: PropTypes.func,
  renderItem: PropTypes.func,
  className: PropTypes.string,
  enableInfiniteScroll: PropTypes.bool,
  loadMoreThreshold: PropTypes.number,
  onLoadMore: PropTypes.func,
  hasMore: PropTypes.bool,
  loading: PropTypes.bool
};

/**
 * Individual virtualized item component with enhanced performance
 */
const VirtualizedItem = memo(({ 
  item, 
  height, 
  onClick, 
  onUpdate, 
  renderItem,
  isScrolling,
  scrollDirection 
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isSelected, setIsSelected] = useState(false);
  const itemRef = useRef(null);

  // Enhanced hover handling
  const handleMouseEnter = useCallback(() => {
    setIsHovered(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsHovered(false);
  }, []);

  // Enhanced click handling
  const handleClick = useCallback(() => {
    setIsSelected(!isSelected);
    onClick?.(item);
  }, [item, onClick, isSelected]);

  // Enhanced update handling
  const handleUpdate = useCallback((updates) => {
    onUpdate?.(item.id, updates);
  }, [item.id, onUpdate]);

  // Performance optimization: reduce re-renders during scrolling
  const itemStyle = useMemo(() => ({
    height: `${height}px`,
    padding: '12px 16px',
    borderBottom: '1px solid #e9ecef',
    cursor: 'pointer',
    transition: isScrolling ? 'none' : 'all 0.2s ease',
    backgroundColor: isHovered ? '#f8f9fa' : isSelected ? '#e3f2fd' : 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    opacity: isScrolling ? 0.9 : 1,
    transform: isScrolling ? `translateY(${scrollDirection === 'down' ? '2px' : '-2px'})` : 'translateY(0)'
  }), [height, isHovered, isSelected, isScrolling, scrollDirection]);

  return (
    <div
      ref={itemRef}
      className="advanced-virtualized-item"
      style={itemStyle}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={handleClick}
    >
      {renderItem ? renderItem(item, { isHovered, isSelected, isScrolling }) : (
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: '500', marginBottom: '4px' }}>
            {item.title || item.name || `Item ${item.index + 1}`}
          </div>
          <div style={{ fontSize: '0.875rem', color: '#6c757d' }}>
            {item.description || item.subtitle || 'No description'}
          </div>
        </div>
      )}
      
      {/* Enhanced quick actions */}
      {isHovered && (
        <div style={{ display: 'flex', gap: '8px', marginLeft: '16px' }}>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleUpdate({ status: 'active' });
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
            Activate
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleUpdate({ status: 'completed' });
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
            Complete
          </button>
        </div>
      )}
    </div>
  );
});

VirtualizedItem.displayName = 'VirtualizedItem';

VirtualizedItem.propTypes = {
  item: PropTypes.object.isRequired,
  height: PropTypes.number.isRequired,
  onClick: PropTypes.func,
  onUpdate: PropTypes.func,
  renderItem: PropTypes.func,
  isScrolling: PropTypes.bool,
  scrollDirection: PropTypes.string
};

export default AdvancedVirtualizedList;
