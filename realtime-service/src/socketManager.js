/**
 * WebSocket Connection Manager with Memory Leak Prevention
 * Handles connection tracking, cleanup, and stale connection management
 */

const logger = require('winston').createLogger({
    level: 'info',
    format: require('winston').format.combine(
        require('winston').format.timestamp(),
        require('winston').format.json()
    ),
    transports: [
        new require('winston').transports.Console({
            format: require('winston').format.simple()
        })
    ]
});

class SocketManager {
    constructor() {
        this.connections = new Map();
        this.rooms = new Map();
        
        // Clean up stale connections every 5 minutes
        this.cleanupInterval = setInterval(
            () => this.cleanupStaleConnections(),
            5 * 60 * 1000
        );
        
        // Track memory usage every minute
        this.memoryCheckInterval = setInterval(
            () => this.checkMemoryUsage(),
            60 * 1000
        );
    }
    
    /**
     * Add a new connection
     * @param {string} socketId - Socket ID
     * @param {Object} socket - Socket instance
     * @param {Object} user - User data
     */
    addConnection(socketId, socket, user) {
        this.connections.set(socketId, {
            socket,
            user,
            lastActivity: Date.now(),
            rooms: new Set(),
            connectedAt: Date.now()
        });
        
        logger.info(`Connection added: ${socketId}, User: ${user.email || user.id}`);
    }
    
    /**
     * Remove a connection
     * @param {string} socketId - Socket ID
     */
    removeConnection(socketId) {
        const conn = this.connections.get(socketId);
        if (conn) {
            // Remove from all rooms
            conn.rooms.forEach(room => this.leaveRoom(socketId, room));
            
            // Delete connection
            this.connections.delete(socketId);
            
            logger.info(`Connection removed: ${socketId}`);
        }
    }
    
    /**
     * Update last activity timestamp
     * @param {string} socketId - Socket ID
     */
    updateActivity(socketId) {
        const conn = this.connections.get(socketId);
        if (conn) {
            conn.lastActivity = Date.now();
        }
    }
    
    /**
     * Add socket to a room
     * @param {string} socketId - Socket ID
     * @param {string} room - Room name
     */
    joinRoom(socketId, room) {
        const conn = this.connections.get(socketId);
        if (conn) {
            conn.rooms.add(room);
            
            // Track room membership
            if (!this.rooms.has(room)) {
                this.rooms.set(room, new Set());
            }
            this.rooms.get(room).add(socketId);
            
            logger.debug(`Socket ${socketId} joined room ${room}`);
        }
    }
    
    /**
     * Remove socket from a room
     * @param {string} socketId - Socket ID
     * @param {string} room - Room name
     */
    leaveRoom(socketId, room) {
        const conn = this.connections.get(socketId);
        if (conn) {
            conn.rooms.delete(room);
        }
        
        // Remove from room tracking
        if (this.rooms.has(room)) {
            this.rooms.get(room).delete(socketId);
            
            // Clean up empty rooms
            if (this.rooms.get(room).size === 0) {
                this.rooms.delete(room);
                logger.debug(`Room ${room} removed (empty)`);
            }
        }
    }
    
    /**
     * Get all sockets in a room
     * @param {string} room - Room name
     * @returns {Set} Set of socket IDs
     */
    getRoomMembers(room) {
        return this.rooms.get(room) || new Set();
    }
    
    /**
     * Clean up stale connections
     * Removes connections that have been inactive for too long
     */
    cleanupStaleConnections() {
        const now = Date.now();
        const timeout = 30 * 60 * 1000; // 30 minutes
        const staleConnections = [];
        
        for (const [socketId, conn] of this.connections) {
            if (now - conn.lastActivity > timeout) {
                staleConnections.push(socketId);
            }
        }
        
        if (staleConnections.length > 0) {
            logger.info(`Cleaning up ${staleConnections.length} stale connections`);
            
            staleConnections.forEach(socketId => {
                const conn = this.connections.get(socketId);
                if (conn && conn.socket) {
                    try {
                        conn.socket.disconnect(true);
                    } catch (error) {
                        logger.error(`Error disconnecting stale socket ${socketId}:`, error);
                    }
                }
                this.removeConnection(socketId);
            });
        }
    }
    
    /**
     * Check memory usage and log warnings
     */
    checkMemoryUsage() {
        const used = process.memoryUsage();
        const connectionCount = this.connections.size;
        const roomCount = this.rooms.size;
        
        // Convert bytes to MB
        const heapUsedMB = (used.heapUsed / 1024 / 1024).toFixed(2);
        const heapTotalMB = (used.heapTotal / 1024 / 1024).toFixed(2);
        
        logger.info(`Memory: ${heapUsedMB}MB / ${heapTotalMB}MB, Connections: ${connectionCount}, Rooms: ${roomCount}`);
        
        // Warn if heap usage is high
        const heapUsagePercent = (used.heapUsed / used.heapTotal) * 100;
        if (heapUsagePercent > 80) {
            logger.warn(`High memory usage: ${heapUsagePercent.toFixed(2)}%`);
        }
        
        // Warn if connection count is very high
        if (connectionCount > 10000) {
            logger.warn(`High connection count: ${connectionCount}`);
        }
    }
    
    /**
     * Get connection statistics
     * @returns {Object} Statistics object
     */
    getStats() {
        const now = Date.now();
        let activeConnections = 0;
        let idleConnections = 0;
        
        for (const [, conn] of this.connections) {
            const idleTime = now - conn.lastActivity;
            if (idleTime < 5 * 60 * 1000) { // 5 minutes
                activeConnections++;
            } else {
                idleConnections++;
            }
        }
        
        return {
            totalConnections: this.connections.size,
            activeConnections,
            idleConnections,
            totalRooms: this.rooms.size,
            timestamp: new Date().toISOString()
        };
    }
    
    /**
     * Shutdown and cleanup
     */
    shutdown() {
        clearInterval(this.cleanupInterval);
        clearInterval(this.memoryCheckInterval);
        
        logger.info('SocketManager shutting down, disconnecting all clients');
        
        // Disconnect all clients
        for (const [socketId, conn] of this.connections) {
            try {
                if (conn.socket) {
                    conn.socket.disconnect(true);
                }
            } catch (error) {
                logger.error(`Error disconnecting socket ${socketId}:`, error);
            }
        }
        
        this.connections.clear();
        this.rooms.clear();
    }
}

// Export singleton instance
module.exports = new SocketManager();
