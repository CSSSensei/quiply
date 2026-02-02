class State {
  constructor() {
    this.user = null;
    this.listeners = new Map();
  }

  setUser(user) {
    this.user = user;
    this.emit("user", user);
  }

  isAuthenticated() {
    return this.user !== null;
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);
    return () => this.off(event, callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback);
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      for (const callback of this.listeners.get(event)) {
        callback(data);
      }
    }
  }
}

export const state = new State();
