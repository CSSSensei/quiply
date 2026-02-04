import { api } from "../api.js";
import { state } from "../state.js";
import { createEl, getInitials, showToast } from "../utils.js";
import { QuipCard } from "../components/QuipCard.js";

export class ProfilePage {
  constructor() {
    this.user = null;
    this.quips = [];
    this.reposts = [];
    this.activeTab = "quips";
    this.loading = true;
    this.el = null;
  }

  async load(params) {
    this.loading = true;
    this.update();

    try {
      const [userResponse, quipsResponse, repostsResponse] = await Promise.all([
        api.getUser(params.username),
        api.getUserQuips(params.username),
        api.getUserReposts(params.username),
      ]);

      this.user = userResponse.data;
      this.quips = Array.isArray(quipsResponse) ? quipsResponse : (quipsResponse.data || []);
      this.reposts = Array.isArray(repostsResponse) ? repostsResponse : (repostsResponse.data || []);
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      this.loading = false;
      this.update();
    }
  }

  render() {
    this.el = createEl("div", { className: "profile-page" }, [
      this.loading
        ? this.renderLoading()
        : this.user
        ? this.renderProfile()
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
      createEl("div", { className: "empty-state-icon" }, ["👤"]),
      createEl("div", { className: "empty-state-title" }, ["User not found"]),
      createEl("div", { className: "empty-state-text" }, [
        "This user doesn't exist.",
      ]),
    ]);
  }

  renderProfile() {
    return createEl("div", {}, [
      this.renderHeader(),
      this.renderTabs(),
      this.renderContent(),
    ]);
  }

  renderHeader() {
    const { user } = this;

    return createEl("header", { className: "profile-header" }, [
      createEl("div", { className: "profile-avatar" }, [
        getInitials(user.username),
      ]),
      createEl("h1", { className: "profile-username" }, [`@${user.username}`]),
      user.bio
        ? createEl("p", { className: "profile-bio" }, [user.bio])
        : null,
      createEl("div", { className: "profile-stats" }, [
        this.renderStat(user.stats?.total_quips || 0, "Quips"),
        this.renderStat(user.stats?.total_quip_ups || 0, "Ups"),
        this.renderStat(user.stats?.total_reposts || 0, "Re-quipped"),
      ]),
    ]);
  }

  renderStat(value, label) {
    return createEl("div", { className: "profile-stat" }, [
      createEl("div", { className: "profile-stat-value" }, [String(value)]),
      createEl("div", { className: "profile-stat-label" }, [label]),
    ]);
  }

  renderTabs() {
    return createEl("div", { className: "profile-tabs" }, [
      this.renderTab("quips", `Quips (${this.quips.length})`),
      this.renderTab("reposts", `Reposts (${this.reposts.length})`),
    ]);
  }

  renderTab(id, label) {
    return createEl(
      "button",
      {
        className: `profile-tab ${this.activeTab === id ? "active" : ""}`,
        onClick: () => {
          this.activeTab = id;
          this.update();
        },
      },
      [label]
    );
  }

  renderContent() {
    const items = this.activeTab === "quips" ? this.quips : this.reposts;

    if (items.length === 0) {
      return createEl("div", { className: "empty-state" }, [
        createEl("div", { className: "empty-state-icon" }, ["📝"]),
        createEl("div", { className: "empty-state-title" }, [
          this.activeTab === "quips" ? "No quips yet" : "No reposts yet",
        ]),
      ]);
    }

    return createEl(
      "div",
      { className: "feed-list" },
      items.map((q) => new QuipCard(q).render())
    );
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
