import { state } from "../state.js";
import { router } from "../router.js";
import { api } from "../api.js";
import { getInitials, createEl } from "../utils.js";

class Navbar {
  constructor() {
    this.el = null;
    this.dropdownOpen = false;
  }

  render() {
    const user = state.user;

    this.el = createEl("nav", { className: "navbar" }, [
      createEl("div", { className: "navbar-content" }, [
        createEl("a", { className: "navbar-logo", href: "#/" }, ["Quiply"]),
        createEl("div", { className: "navbar-actions" }, [
          this.renderThemeToggle(),
          user ? this.renderUserMenu(user) : this.renderAuthButtons(),
        ]),
      ]),
    ]);

    return this.el;
  }

  renderThemeToggle() {
    const isDark = document.documentElement.dataset.theme !== "light";

    return createEl(
      "button",
      {
        className: "theme-toggle",
        onClick: () => this.toggleTheme(),
        title: "Toggle theme",
      },
      [isDark ? "☀️" : "🌙"]
    );
  }

  toggleTheme() {
    const html = document.documentElement;
    const isDark = html.dataset.theme !== "light";
    html.dataset.theme = isDark ? "light" : "dark";
    localStorage.setItem("theme", html.dataset.theme);
    this.update();
  }

  renderAuthButtons() {
    return createEl("div", { className: "flex gap-sm" }, [
      createEl(
        "a",
        {
          className: "btn btn-ghost btn-sm",
          href: "#/login",
        },
        ["Log in"]
      ),
      createEl(
        "a",
        {
          className: "btn btn-primary btn-sm",
          href: "#/register",
        },
        ["Sign up"]
      ),
    ]);
  }

  renderUserMenu(user) {
    const dropdown = createEl(
      "div",
      { className: `dropdown ${this.dropdownOpen ? "open" : ""}` },
      [
        createEl(
          "div",
          {
            className: "navbar-user",
            onClick: (e) => {
              e.stopPropagation();
              this.toggleDropdown();
            },
          },
          [
            createEl("div", { className: "navbar-avatar" }, [
              getInitials(user.username),
            ]),
            createEl("span", { className: "navbar-username" }, [user.username]),
          ]
        ),
        createEl("div", { className: "dropdown-menu" }, [
          createEl(
            "button",
            {
              className: "dropdown-item",
              onClick: () => {
                router.navigate(`/users/${user.username}`);
                this.closeDropdown();
              },
            },
            ["👤 Profile"]
          ),
          createEl("div", { className: "dropdown-divider" }),
          createEl(
            "button",
            {
              className: "dropdown-item danger",
              onClick: () => this.handleLogout(),
            },
            ["🚪 Log out"]
          ),
        ]),
      ]
    );

    document.addEventListener("click", () => this.closeDropdown(), {
      once: true,
    });

    return dropdown;
  }

  toggleDropdown() {
    this.dropdownOpen = !this.dropdownOpen;
    this.update();
  }

  closeDropdown() {
    if (this.dropdownOpen) {
      this.dropdownOpen = false;
      this.update();
    }
  }

  handleLogout() {
    api.logout();
    state.setUser(null);
    router.navigate("/");
    this.closeDropdown();
  }

  update() {
    const oldEl = this.el;
    if (!oldEl) return;
    
    const parent = oldEl.parentNode;
    if (!parent) return;
    
    const newEl = this.render();
    parent.replaceChild(newEl, oldEl);
  }
}

export const navbar = new Navbar();
