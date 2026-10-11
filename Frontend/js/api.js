// API Client for Pluraal BI

const API = {
  baseUrl: "/api",

  getToken() {
    return localStorage.getItem("pluraal_bi_token");
  },

  setToken(token) {
    if (token) {
      localStorage.setItem("pluraal_bi_token", token);
    } else {
      localStorage.removeItem("pluraal_bi_token");
    }
  },

  getUser() {
    try {
      const u = localStorage.getItem("pluraal_bi_user");
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  },

  setUser(user) {
    if (user) {
      localStorage.setItem("pluraal_bi_user", JSON.stringify(user));
    } else {
      localStorage.removeItem("pluraal_bi_user");
    }
  },

  clearSession() {
    localStorage.removeItem("pluraal_bi_token");
    localStorage.removeItem("pluraal_bi_user");
  },

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        if (response.status === 401 && !endpoint.includes("/login")) {
          // Token expired or invalid
          this.clearSession();
          window.location.reload();
          return;
        }

        const err = new Error(data.message || "Erro na requisição.");
        err.status = response.status;
        err.code = data.error;
        err.data = data;
        throw err;
      }

      return data;
    } catch (err) {
      throw err;
    }
  },

  get(endpoint) {
    return this.request(endpoint, { method: "GET" });
  },

  post(endpoint, body) {
    return this.request(endpoint, {
      method: "POST",
      body: JSON.stringify(body)
    });
  },

  put(endpoint, body) {
    return this.request(endpoint, {
      method: "PUT",
      body: JSON.stringify(body)
    });
  },

  delete(endpoint) {
    return this.request(endpoint, { method: "DELETE" });
  }
};
