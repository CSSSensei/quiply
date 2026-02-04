import { api } from "../api.js";
import { state } from "../state.js";
import { getInitials, createEl, showToast } from "../utils.js";

const MAX_CONTENT_LENGTH = 1000;
const MAX_DEFINITION_LENGTH = 500;
const MAX_EXAMPLES_LENGTH = 1000;

export class CreateQuip {
  constructor(onCreated) {
    this.onCreated = onCreated;
    this.content = "";
    this.definition = "";
    this.examples = "";
    this.showExtras = false;
    this.loading = false;
    this.el = null;
  }

  render() {
    if (!state.isAuthenticated()) {
      return createEl("div");
    }

    const user = state.user;
    const remaining = MAX_CONTENT_LENGTH - this.content.length;

    this.el = createEl("div", { className: "create-quip" }, [
      createEl("div", { className: "create-quip-header" }, [
        createEl("div", { className: "create-quip-avatar" }, [
          getInitials(user.username),
        ]),
        createEl("span", { className: "text-secondary" }, [
          `What's your quip, ${user.username}?`,
        ]),
      ]),
      createEl("textarea", {
        className: "create-quip-input form-textarea",
        placeholder: "Share a witty phrase, idiom, or quip...",
        value: this.content,
        maxLength: MAX_CONTENT_LENGTH,
        onInput: (e) => {
          this.content = e.target.value;
          this.updateCounter();
        },
      }),
      this.renderExtras(),
      createEl("div", { className: "create-quip-footer" }, [
        createEl(
          "span",
          {
            className: `create-quip-counter ${
              remaining < 20 ? (remaining < 0 ? "error" : "warning") : ""
            }`,
          },
          [`${remaining}`]
        ),
        createEl(
          "button",
          {
            className: "btn btn-primary",
            disabled: this.loading || !this.content.trim() || remaining < 0,
            onClick: () => this.handleSubmit(),
          },
          [this.loading ? "Posting..." : "Quip it!"]
        ),
      ]),
    ]);

    return this.el;
  }

  renderExtras() {
    return createEl("div", { className: "create-quip-extras" }, [
      createEl(
        "label",
        {
          className: "create-quip-toggle",
          onClick: () => {
            this.showExtras = !this.showExtras;
            this.update();
          },
        },
        [
          createEl("span", {}, [this.showExtras ? "▼" : "▶"]),
          createEl("span", {}, ["Add definition & examples"]),
        ]
      ),
      this.showExtras
        ? createEl("div", { className: "flex flex-col gap-md" }, [
            createEl("div", { className: "flex flex-col gap-sm" }, [
              createEl("input", {
                className: "form-input",
                type: "text",
                placeholder: "Definition (optional)",
                value: this.definition,
                maxLength: MAX_DEFINITION_LENGTH,
                onInput: (e) => (this.definition = e.target.value),
              }),
              createEl("div", { className: "text-secondary text-sm" }, [
                `${MAX_DEFINITION_LENGTH - this.definition.length} characters remaining`
              ]),
            ]),
            createEl("div", { className: "flex flex-col gap-sm" }, [
              createEl("input", {
                className: "form-input",
                type: "text",
                placeholder: "Usage example (optional)",
                value: this.examples,
                maxLength: MAX_EXAMPLES_LENGTH,
                onInput: (e) => (this.examples = e.target.value),
              }),
              createEl("div", { className: "text-secondary text-sm" }, [
                `${MAX_EXAMPLES_LENGTH - this.examples.length} characters remaining`
              ]),
            ]),
          ])
        : null,
    ]);
  }

  updateCounter() {
    const remaining = MAX_CONTENT_LENGTH - this.content.length;
    
    const counter = this.el?.querySelector(".create-quip-counter");
    if (counter) {
      counter.textContent = remaining;
      counter.className = `create-quip-counter ${
        remaining < 20 ? (remaining < 0 ? "error" : "warning") : ""
      }`;
    }
    
    const btn = this.el?.querySelector(".btn-primary");
    if (btn) {
      btn.disabled = this.loading || !this.content.trim() || remaining < 0;
    }
  }

  async handleSubmit() {
    if (!this.content.trim() || this.loading) return;

    this.loading = true;
    this.update();

    try {
      const quip = await api.createQuip(
        this.content.trim(),
        this.definition.trim() || null,
        this.examples.trim() || null
      );

      this.content = "";
      this.definition = "";
      this.examples = "";
      this.showExtras = false;

      showToast("Quip posted!", "success");

      if (this.onCreated) {
        this.onCreated(quip);
      }
    } catch (err) {
      showToast(err.message, "error");
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
