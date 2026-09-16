class WebSocketClient {
  constructor() {
    this.ws = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectInterval = 2000;
    this.isConnected = false;
  }

  connect() {
    // Prevent duplicate concurrent connections
    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    const wsUrl = `ws://${window.location.hostname || '127.0.0.1'}:8000/ws`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.emit('connection_status', { connected: true });
        console.log('WebSocket connected to FinResolve Predict engine');
      };

      this.ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type) {
            this.emit(payload.type, payload.data);
          }
        } catch (e) {
          console.error('Error parsing WebSocket message:', e);
        }
      };

      this.ws.onclose = () => {
        const wasConnected = this.isConnected;
        this.isConnected = false;
        if (wasConnected) {
          this.emit('connection_status', { connected: false });
        }
        if (!this.explicitDisconnect) {
          this.scheduleReconnect();
        }
      };

      this.ws.onerror = (err) => {
        console.warn('WebSocket encountered error:', err);
      };
    } catch (e) {
      console.error('WebSocket connection error:', e);
      this.scheduleReconnect();
    }
  }

  disconnect() {
    this.explicitDisconnect = true;
    if (this.ws) {
      try {
        this.ws.close();
      } catch (e) {
        // ignore
      }
      this.ws = null;
    }
    this.isConnected = false;
  }

  scheduleReconnect() {
    if (this.explicitDisconnect) return;
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(this.reconnectInterval * Math.pow(1.5, this.reconnectAttempts - 1), 10000);
      setTimeout(() => {
        if (!this.explicitDisconnect) {
          this.connect();
        }
      }, delay);
    }
  }

  on(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType).add(callback);
    return () => this.off(eventType, callback);
  }

  off(eventType, callback) {
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).delete(callback);
    }
  }

  emit(eventType, data) {
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).forEach(cb => {
        try {
          cb(data);
        } catch (e) {
          console.error(`Error in WebSocket listener for ${eventType}:`, e);
        }
      });
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(typeof data === 'string' ? data : JSON.stringify(data));
    }
  }
}

export const wsClient = new WebSocketClient();
