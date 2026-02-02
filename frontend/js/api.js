const API_BASE = "https://api.quiply.yan-toples.ru/api/v1";

class ApiClient {
  constructor() {
    this.token = localStorage.getItem("token");
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem("token", token);
    } else {
      localStorage.removeItem("token");
    }
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      this.setToken(null);
      window.dispatchEvent(new CustomEvent("auth:logout"));
    }

    const data = await response.json();

    if (!response.ok) {
      throw new ApiError(data.error || "Request failed", response.status, data);
    }

    return data;
  }

  async register(username, email, password) {
    return this.request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, email, password }),
    });
  }

  async login(username, password) {
    const data = await this.request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    this.setToken(data.token);
    return data;
  }

  async getMe() {
    return this.request("/auth/me");
  }

  logout() {
    this.setToken(null);
    window.dispatchEvent(new CustomEvent("auth:logout"));
  }

  async getQuips(sort = "smart", page = 1) {
    return this.request(`/quips?sort=${sort}&page=${page}`);
  }

  async getQuip(id) {
    return this.request(`/quips/${id}`);
  }

  async deleteQuip(id) {
    return this.request(`/quips/${id}`, { method: "DELETE" });
  }

  async createQuip(content, definition = null, usageExamples = null) {
    return this.request("/quips", {
      method: "POST",
      body: JSON.stringify({
        content,
        definition,
        usage_examples: usageExamples,
      }),
    });
  }

  async upQuip(id) {
    return this.request(`/quips/${id}/up`, { method: "POST" });
  }

  async removeUpQuip(id) {
    return this.request(`/quips/${id}/up`, { method: "DELETE" });
  }

  async repostQuip(id) {
    return this.request(`/quips/${id}/repost`, { method: "POST" });
  }

  async removeRepostQuip(id) {
    return this.request(`/quips/${id}/repost`, { method: "DELETE" });
  }

  async getComments(quipId) {
    return this.request(`/quips/${quipId}/comments`);
  }

  async createComment(quipId, content, parentId = null) {
    return this.request(`/quips/${quipId}/comments`, {
      method: "POST",
      body: JSON.stringify({ content, parent_id: parentId }),
    });
  }

  async upComment(commentId) {
    return this.request(`/quips/comments/${commentId}/up`, { method: "POST" });
  }

  async removeUpComment(commentId) {
    return this.request(`/quips/comments/${commentId}/up`, { method: "DELETE" });
  }

  async getUser(username) {
    return this.request(`/users/${username}`);
  }

  async getUserQuips(username) {
    return this.request(`/users/${username}/quips`);
  }

  async getUserReposts(username) {
    return this.request(`/users/${username}/reposts`);
  }
}

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

export const api = new ApiClient();
export { ApiError };
