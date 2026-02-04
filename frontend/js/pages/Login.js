import { api } from "../api.js";
import { state } from "../state.js";
import { router } from "../router.js";
import { createEl, showToast } from "../utils.js";

export class LoginPage {
  constructor() {
    this.username = "";
    this.password = "";
    this.loading = false;
    this.error = null;
    this.el = null;
  }

  render() {
    this.el = createEl("div", { className: "auth-container" }, [
      createEl("div", { className: "auth-card animate-fade-in" }, [
        createEl("div", { className: "auth-header" }, [
          createEl("h1", { className: "auth-title" }, ["Welcome back"]),
          createEl("p", { className: "auth-subtitle" }, [
            "Log in to share your wit",
          ]),
        ]),
        this.renderForm(),
        createEl("div", { className: "auth-footer" }, [
          "Don't have an account? ",
          createEl("a", { href: "#/register" }, ["Sign up"]),
        ]),
      ]),
    ]);

    return this.el;
  }

  renderForm() {
    return createEl(
      "form",
      {
        className: "auth-form",
        onSubmit: (e) => {
          e.preventDefault();
          this.handleSubmit();
        },
      },
      [
        this.error
          ? createEl("div", { className: "form-error mb-md" }, [this.error])
          : null,
        createEl("div", { className: "form-group" }, [
          createEl("label", { className: "form-label", for: "username" }, [
            "Username",
          ]),
          createEl("input", {
            className: "form-input",
            type: "text",
            id: "username",
            placeholder: "Enter your username",
            value: this.username,
            onInput: (e) => (this.username = e.target.value),
            required: true,
          }),
        ]),
        createEl("div", { className: "form-group" }, [
          createEl("label", { className: "form-label", for: "password" }, [
            "Password",
          ]),
          createEl("input", {
            className: "form-input",
            type: "password",
            id: "password",
            placeholder: "Enter your password",
            value: this.password,
            onInput: (e) => (this.password = e.target.value),
            required: true,
          }),
        ]),
        createEl(
          "button",
          {
            className: "btn btn-primary btn-lg",
            style: "width: 100%",
            type: "submit",
            disabled: this.loading,
          },
          [this.loading ? "Logging in..." : "Log in"]
        ),
      ]
    );
  }

  async handleSubmit() {
    if (!this.username || !this.password) return;

    this.loading = true;
    this.error = null;
    this.update();

    try {
      await api.login(this.username, this.password);
      const response = await api.getMe();
      state.setUser(response.data);
      showToast("Welcome back!", "success");
      router.navigate("/");
    } catch (err) {
      this.error = err.message;
      this.update();
    } finally {
      this.loading = false;
      this.update();
    }
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
