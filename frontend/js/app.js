import { api } from "./api.js";
import { router } from "./router.js";
import { state } from "./state.js";
import { navbar } from "./components/Navbar.js";
import { FeedPage } from "./pages/Feed.js";
import { QuipDetailPage } from "./pages/QuipDetail.js";
import { ProfilePage } from "./pages/Profile.js";
import { LoginPage } from "./pages/Login.js";
import { RegisterPage } from "./pages/Register.js";

class App {
  constructor() {
    this.mainContent = null;
    this.currentPage = null;
  }

  async init() {
    this.initTheme();
    await this.initAuth();
    this.initRouter();
    this.render();
    this.setupEventListeners();
    router.start();
  }

  initTheme() {
    const savedTheme = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    document.documentElement.dataset.theme = savedTheme || (prefersDark ? "dark" : "light");
  }

  async initAuth() {
    if (api.token) {
      try {
        const userData = await api.getMe();
        state.setUser(userData);
      } catch {
        api.setToken(null);
      }
    }
  }

  initRouter() {
    router
      .addRoute("/", async (ctx) => {
        const page = new FeedPage();
        await this.showPage(page, ctx.params);
      })
      .addRoute("/login", async () => {
        if (state.isAuthenticated()) {
          router.navigate("/");
          return;
        }
        const page = new LoginPage();
        this.showPage(page);
      })
      .addRoute("/register", async () => {
        if (state.isAuthenticated()) {
          router.navigate("/");
          return;
        }
        const page = new RegisterPage();
        this.showPage(page);
      })
      .addRoute("/quips/:id", async (ctx) => {
        const page = new QuipDetailPage();
        await this.showPage(page, ctx.params);
      })
      .addRoute("/users/:username", async (ctx) => {
        const page = new ProfilePage();
        await this.showPage(page, ctx.params);
      });
  }

  render() {
    const app = document.getElementById("app");
    app.innerHTML = "";
    app.className = "app-container";

    app.appendChild(navbar.render());

    this.mainContent = document.createElement("main");
    this.mainContent.className = "main-content";
    app.appendChild(this.mainContent);
  }

  async showPage(page, params = {}) {
    this.currentPage = page;
    this.mainContent.innerHTML = "";

    const el = page.render();
    this.mainContent.appendChild(el);

    if (page.load) {
      await page.load(params);
    }
  }

  setupEventListeners() {
    state.on("user", () => {
      navbar.update();
    });

    window.addEventListener("auth:logout", () => {
      state.setUser(null);
      router.navigate("/");
    });
  }
}

const app = new App();
app.init();
