import { api } from "../api.js";
import { createEl, showToast } from "../utils.js";
import { QuipCard } from "../components/QuipCard.js";
import { Comments } from "../components/Comments.js";

export class QuipDetailPage {
  constructor() {
    this.quip = null;
    this.loading = true;
    this.el = null;
    this.comments = null;
  }

  async load(params) {
    this.loading = true;
    this.update();

    try {
      const response = await api.getQuip(params.id);
      this.quip = response.data;
      this.comments = new Comments(params.id);
      this.comments.load();
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      this.loading = false;
      this.update();
    }
  }

  render() {
    this.el = createEl("div", { className: "quip-detail-page content-wrapper" }, [
      createEl("a", { href: "#/", className: "btn btn-ghost mb-lg" }, [
        "← Back to feed",
      ]),
      this.loading
        ? this.renderLoading()
        : this.quip
        ? this.renderQuip()
        : this.renderNotFound(),
    ]);

    return this.el;
  }

  renderLoading() {
    return createEl("div", { className: "loading-container" }, [
      createEl("div", { className: "spinner" }),
    ]);
  }

  renderNotFound() {
    return createEl("div", { className: "empty-state" }, [
      createEl("div", { className: "empty-state-icon" }, ["🔍"]),
      createEl("div", { className: "empty-state-title" }, ["Quip not found"]),
      createEl("div", { className: "empty-state-text" }, [
        "This quip may have been deleted.",
      ]),
    ]);
  }

  renderQuip() {
    return createEl("div", {}, [
      new QuipCard(this.quip).render(),
      createEl("div", { className: "card mt-lg" }, [
        this.comments ? this.comments.render() : null,
      ]),
    ]);
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
