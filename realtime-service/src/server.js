/**
 * Real-time service for helpdesk platform using Socket.io
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const redis = require('redis');
const axios = require('axios');
const cors = require('cors');
const winston = require('winston');

// Configure Winston logger
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json(),
    ),
    defaultMeta: { service: 'realtime-service' },
    transports: [
        new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
        new winston.transports.File({ filename: 'logs/combined.log' }),
        new winston.transports.Console({
            format: winston.format.simple(),
        }),
    ],
});

const app = express();
const server = http.createServer(app);

// CORS configuration
app.use(cors({
    origin: process.env.CORS_ORIGINS?.split(',') || '*',
    credentials: true,
}));

// Socket.io configuration
const io = socketIo(server, {
    cors: {
        origin: process.env.CORS_ORIGINS?.split(',') || '*',
        methods: ['GET', 'POST'],
        credentials: true,
    },
});

// Redis client
const redisClient = redis.createClient({
    url: process.env.REDIS_URL || 'redis://localhost:6379',
});

redisClient.on('error', (err) => logger.error('Redis Client Error', err));
redisClient.connect();

// Django API base URL
const DJANGO_API_URL = process.env.DJANGO_API_URL || 'http://localhost:8000';

// Store active connections
const activeConnections = new Map();

// Middleware for authentication
io.use(async(socket, next) => {
    try {
        const token = socket.handshake.auth.token;
        if (!token) {
            return next(new Error('Authentication required'));
        }

        // Verify token with Django API
        const response = await axios.get(`${DJANGO_API_URL}/api/v1/auth/verify/`, {
            headers: { Authorization: `Bearer ${token}` },
        });

        socket.user = response.data.user;
        socket.organization = response.data.organization;
        next();
    } catch (error) {
        logger.error('Token verification failed:', error);
        next(new Error('Invalid token'));
    }
});

// Connection handling
io.on('connection', (socket) => {
    logger.info(`User ${socket.user.email} connected`);
    
    // Store connection
    activeConnections.set(socket.user.id, socket);
    
    // Join organization room
    socket.join(`org_${socket.organization.id}`);
    
    // Join user-specific room
    socket.join(`user_${socket.user.id}`);

    // Ticket-related events
    socket.on('join-ticket', (ticketId) => {
        socket.join(`ticket_${ticketId}`);
        logger.info(`User ${socket.user.email} joined ticket ${ticketId}`);
    });

    socket.on('leave-ticket', (ticketId) => {
        socket.leave(`ticket_${ticketId}`);
        logger.info(`User ${socket.user.email} left ticket ${ticketId}`);
    });

    // Live chat events
    socket.on('join-chat', (chatId) => {
        socket.join(`chat_${chatId}`);
        logger.info(`User ${socket.user.email} joined chat ${chatId}`);
    });

    socket.on('chat-message', async(data) => {
        try {
            // Save message to Django API
            const response = await axios.post(
                `${DJANGO_API_URL}/api/v1/chat/messages/`,
                {
                    chat_id: data.chatId,
                    content: data.message,
                    user_id: socket.user.id,
                },
                {
                    headers: { Authorization: `Bearer ${socket.handshake.auth.token}` },
                },
            );

            // Broadcast to chat room
            io.to(`chat_${data.chatId}`).emit('new-message', {
                id: response.data.id,
                content: data.message,
                user: socket.user,
                timestamp: new Date().toISOString(),
            });
        } catch (error) {
            logger.error('Failed to send chat message:', error);
            socket.emit('error', { message: 'Failed to send message' });
        }
    });

    // Typing indicators
    socket.on('typing-start', (data) => {
        socket.to(`ticket_${data.ticketId}`).emit('user-typing', {
            userId: socket.user.id,
            userName: socket.user.email,
            ticketId: data.ticketId,
        });
    });

    socket.on('typing-stop', (data) => {
        socket.to(`ticket_${data.ticketId}`).emit('user-stopped-typing', {
            userId: socket.user.id,
            ticketId: data.ticketId,
        });
    });

    // GPS tracking for technicians
    socket.on('location-update', async(data) => {
        try {
            // Update location in Django API
            await axios.put(
                `${DJANGO_API_URL}/api/v1/technicians/${socket.user.id}/location/`,
                {
                    latitude: data.latitude,
                    longitude: data.longitude,
                    accuracy: data.accuracy,
                    timestamp: new Date().toISOString(),
                },
                {
                    headers: { Authorization: `Bearer ${socket.handshake.auth.token}` },
                },
            );

            // Broadcast to admin dashboard
            io.to(`org_${socket.organization.id}`).emit('technician-location', {
                technicianId: socket.user.id,
                technicianName: socket.user.email,
                location: {
                    latitude: data.latitude,
                    longitude: data.longitude,
                    accuracy: data.accuracy,
                },
                timestamp: new Date().toISOString(),
            });
        } catch (error) {
            logger.error('Location update failed:', error);
        }
    });

    // Notification events
    socket.on('subscribe-notifications', () => {
        socket.join(`notifications_${socket.user.id}`);
        logger.info(`User ${socket.user.email} subscribed to notifications`);
    });

    socket.on('unsubscribe-notifications', () => {
        socket.leave(`notifications_${socket.user.id}`);
        logger.info(`User ${socket.user.email} unsubscribed from notifications`);
    });

    // Ticket events
    socket.on('ticket-update', async(data) => {
        try {
            // Update ticket in Django API
            await axios.patch(
                `${DJANGO_API_URL}/api/v1/tickets/${data.ticketId}/`,
                data.updates,
                {
                    headers: { Authorization: `Bearer ${socket.handshake.auth.token}` },
                },
            );

            // Broadcast to ticket room
            io.to(`ticket_${data.ticketId}`).emit('ticket-updated', {
                ticketId: data.ticketId,
                updates: data.updates,
                updatedBy: socket.user,
                timestamp: new Date().toISOString(),
            });
        } catch (error) {
            logger.error('Failed to update ticket:', error);
            socket.emit('error', { message: 'Failed to update ticket' });
        }
    });

    // Disconnection handling
    socket.on('disconnect', () => {
        logger.info(`User ${socket.user.email} disconnected`);
        activeConnections.delete(socket.user.id);
        
        // Update user status
        socket.to(`org_${socket.organization.id}`).emit('user-offline', {
            userId: socket.user.id,
            timestamp: new Date().toISOString(),
        });
    });
});

// Health check endpoint
app.get('/health/', (req, res) => {
    res.json({ 
        status: 'healthy', 
        service: 'realtime-service',
        connections: activeConnections.size,
        timestamp: new Date().toISOString(),
    });
});

// Broadcast notification function
async function broadcastNotification(organizationId, userId, notification) {
    try {
        // Save notification to Redis
        await redisClient.lPush(
            `notifications:${organizationId}:${userId}`,
            JSON.stringify(notification),
        );

        // Set expiration (7 days)
        await redisClient.expire(
            `notifications:${organizationId}:${userId}`,
            604800,
        );

        // Broadcast to user
        io.to(`notifications_${userId}`).emit('notification', notification);
        
        // Broadcast to organization admin
        io.to(`org_${organizationId}`).emit('org-notification', {
            ...notification,
            userId,
        });
    } catch (error) {
        logger.error('Broadcast notification failed:', error);
    }
}

// Broadcast ticket update
async function broadcastTicketUpdate(ticketId, update) {
    try {
        io.to(`ticket_${ticketId}`).emit('ticket-updated', update);
    } catch (error) {
        logger.error('Broadcast ticket update failed:', error);
    }
}

// Broadcast system message
async function broadcastSystemMessage(organizationId, message) {
    try {
        io.to(`org_${organizationId}`).emit('system-message', {
            message,
            timestamp: new Date().toISOString(),
        });
    } catch (error) {
        logger.error('Broadcast system message failed:', error);
    }
}

// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    logger.info(`Real-time service running on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    logger.info('SIGTERM received, shutting down gracefully');
    server.close(() => {
        logger.info('Process terminated');
    });
});

module.exports = {
    io,
    broadcastNotification,
    broadcastTicketUpdate,
    broadcastSystemMessage,
};