import { api } from "../api.js";
import { state } from "../state.js";
import { router } from "../router.js";
import { createEl, showToast } from "../utils.js";

export class RegisterPage {
  constructor() {
    this.username = "";
    this.email = "";
    this.password = "";
    this.loading = false;
    this.error = null;
    this.el = null;
  }

  render() {
    this.el = createEl("div", { className: "auth-container" }, [
      createEl("div", { className: "auth-card animate-fade-in" }, [
        createEl("div", { className: "auth-header" }, [
          createEl("h1", { className: "auth-title" }, ["Join Quiply"]),
          createEl("p", { className: "auth-subtitle" }, [
            "Share your wit with the world",
          ]),
        ]),
        this.renderForm(),
        createEl("div", { className: "auth-footer" }, [
          "Already have an account? ",
          createEl("a", { href: "#/login" }, ["Log in"]),
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
            placeholder: "Choose a username",
            value: this.username,
            onInput: (e) => (this.username = e.target.value),
            required: true,
            minLength: 5,
            maxLength: 20,
            pattern: "[a-z0-9_]+",
          }),
          createEl("div", { className: "form-hint" }, [
            "5-20 characters, lowercase letters, numbers, and underscores only",
          ]),
        ]),
        createEl("div", { className: "form-group" }, [
          createEl("label", { className: "form-label", for: "email" }, [
            "Email",
          ]),
          createEl("input", {
            className: "form-input",
            type: "email",
            id: "email",
            placeholder: "Enter your email",
            value: this.email,
            onInput: (e) => (this.email = e.target.value),
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
            placeholder: "Create a password",
            value: this.password,
            onInput: (e) => (this.password = e.target.value),
            required: true,
            minLength: 6,
          }),
          createEl("div", { className: "form-hint" }, [
            "At least 6 characters",
          ]),
        ]),
        createEl(
          "button",
          {
            className: "btn btn-primary btn-lg",
            style: "width: 100%",
            type: "submit",
            disabled: this.loading,
          },
          [this.loading ? "Creating account..." : "Sign up"]
        ),
      ]
    );
  }

  async handleSubmit() {
    if (!this.username || !this.email || !this.password) return;

    this.loading = true;
    this.error = null;
    this.update();

    try {
      await api.register(this.username, this.email, this.password);
      await api.login(this.username, this.password);
      const userData = await api.getMe();
      state.setUser(userData);
      showToast("Welcome to Quiply!", "success");
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
