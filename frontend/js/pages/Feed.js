import { api } from "../api.js";
import { state } from "../state.js";
import { createEl, showToast } from "../utils.js";
import { QuipCard } from "../components/QuipCard.js";
import { CreateQuip } from "../components/CreateQuip.js";

export class FeedPage {
  constructor() {
    this.quips = [];
    this.sort = "smart";
    this.page = 1;
    this.loading = true;
    this.hasMore = true;
    this.el = null;
  }

  async load(params = {}) {
    this.sort = params.sort || "smart";
    this.page = 1;
    this.quips = [];
    this.hasMore = true;
    this.loading = true;
    // Don't call update() here - element is already rendered
    // Just load data and then update
    await this.loadQuips();
  }

  async loadQuips() {

    try {
      const data = await api.getQuips(this.sort, this.page);
      const newQuips = Array.isArray(data) ? data : (data.quips || []);

      if (this.page === 1) {
        this.quips = newQuips;
      } else {
        this.quips = [...this.quips, ...newQuips];
      }

      this.hasMore = newQuips.length >= 20;
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      this.loading = false;
      this.update();
    }
  }

  render() {
    this.el = createEl("div", { className: "feed-page" }, [
      this.renderHeader(),
      createEl("div", { className: "feed-list" }, [
        state.isAuthenticated()
          ? new CreateQuip((quip) => this.handleQuipCreated(quip)).render()
          : null,
        ...this.quips.map((q) => new QuipCard(q).render()),
        this.loading ? this.renderLoading() : null,
        !this.loading && this.quips.length === 0 ? this.renderEmpty() : null,
        !this.loading && this.hasMore ? this.renderLoadMore() : null,
      ]),
    ]);

    return this.el;
  }

  renderHeader() {
    return createEl("header", { className: "feed-header" }, [
      createEl("h1", { className: "feed-title" }, ["Feed"]),
      createEl("div", { className: "feed-sort" }, [
        this.renderSortBtn("smart", "🔥 Smart"),
        this.renderSortBtn("new", "🕐 New"),
      ]),
    ]);
  }

  renderSortBtn(value, label) {
    return createEl(
      "button",
      {
        className: `feed-sort-btn ${this.sort === value ? "active" : ""}`,
        onClick: () => this.handleSortChange(value),
      },
      [label]
    );
  }

  renderLoading() {
    return createEl("div", { className: "loading-container" }, [
      createEl("div", { className: "spinner" }),
    ]);
  }

  renderEmpty() {
    return createEl("div", { className: "empty-state" }, [
      createEl("div", { className: "empty-state-icon" }, ["✨"]),
      createEl("div", { className: "empty-state-title" }, ["No quips yet"]),
      createEl("div", { className: "empty-state-text" }, [
        "Be the first to share something witty!",
      ]),
    ]);
  }

  renderLoadMore() {
    return createEl(
      "button",
      {
        className: "btn btn-secondary",
        style: "width: 100%; margin-top: var(--spacing-md)",
        onClick: () => this.handleLoadMore(),
      },
      ["Load more"]
    );
  }

  handleSortChange(sort) {
    if (sort === this.sort) return;
    this.sort = sort;
    this.page = 1;
    this.quips = [];
    this.loading = true;
    this.update();
    this.loadQuips();
  }

  handleLoadMore() {
    this.page++;
    this.loading = true;
    this.update();
    this.loadQuips();
  }

  handleQuipCreated(quip) {
    this.quips.unshift(quip);
    this.update();
  }

  update() {
    const oldEl = this.el;
    if (!oldEl) return;
    
    const parent = oldEl.parentNode;
    if (!parent) {
      console.warn("FeedPage.update() called but element not in DOM");
      return;
    }
    
    const newEl = this.render();
    parent.replaceChild(newEl, oldEl);
  }
}
