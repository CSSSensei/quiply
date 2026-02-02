class Router {
  constructor() {
    this.routes = new Map();
    this.currentRoute = null;
    this.beforeHooks = [];

    window.addEventListener("hashchange", () => this.handleRoute());
    window.addEventListener("load", () => this.handleRoute());
  }

  addRoute(path, handler) {
    this.routes.set(path, handler);
    return this;
  }

  beforeEach(hook) {
    this.beforeHooks.push(hook);
    return this;
  }

  navigate(path) {
    window.location.hash = path;
  }

  parseHash() {
    const hash = window.location.hash.slice(1) || "/";
    const [path, queryString] = hash.split("?");
    const params = {};

    if (queryString) {
      queryString.split("&").forEach((pair) => {
        const [key, value] = pair.split("=");
        params[key] = decodeURIComponent(value || "");
      });
    }

    return { path, params };
  }

  matchRoute(path) {
    if (this.routes.has(path)) {
      return { handler: this.routes.get(path), params: {} };
    }

    for (const [pattern, handler] of this.routes) {
      const patternParts = pattern.split("/");
      const pathParts = path.split("/");

      if (patternParts.length !== pathParts.length) continue;

      const params = {};
      let match = true;

      for (let i = 0; i < patternParts.length; i++) {
        if (patternParts[i].startsWith(":")) {
          params[patternParts[i].slice(1)] = pathParts[i];
        } else if (patternParts[i] !== pathParts[i]) {
          match = false;
          break;
        }
      }

      if (match) {
        return { handler, params };
      }
    }

    return null;
  }

  async handleRoute() {
    const { path, params: queryParams } = this.parseHash();
    const match = this.matchRoute(path);

    if (!match) {
      this.navigate("/");
      return;
    }

    const { handler, params: routeParams } = match;
    const context = {
      path,
      params: { ...routeParams, ...queryParams },
      router: this,
    };

    for (const hook of this.beforeHooks) {
      const result = await hook(context);
      if (result === false) return;
    }

    this.currentRoute = path;
    await handler(context);
  }
}

export const router = new Router();
