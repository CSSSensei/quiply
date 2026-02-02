import { api } from "../api.js";
import { state } from "../state.js";
import { router } from "../router.js";
import { formatTime, getInitials, escapeHtml, createEl, showToast } from "../utils.js";

export class QuipCard {
  constructor(quip, options = {}) {
    this.quip = quip;
    this.options = options;
    this.el = null;
  }

  render() {
    const { quip } = this;

    this.el = createEl("article", { className: "quip-card animate-fade-in" }, [
      this.renderHeader(),
      this.renderContent(),
      quip.definition ? this.renderDefinition() : null,
      quip.usage_examples ? this.renderExamples() : null,
      this.renderActions(),
    ]);

    return this.el;
  }

  getUsername() {
    return this.quip.username || this.quip.author?.username || "Unknown";
  }

  isOwner() {
    return state.isAuthenticated() && state.user?.id === this.quip.user_id;
  }

  renderHeader() {
    const { quip } = this;
    const username = this.getUsername();

    return createEl("header", { className: "quip-header" }, [
      createEl("div", { className: "quip-avatar" }, [
        getInitials(username),
      ]),
      createEl("div", { className: "quip-meta" }, [
        createEl(
          "a",
          {
            className: "quip-author",
            href: `#/users/${username}`,
          },
          [username]
        ),
        createEl("div", { className: "quip-time" }, [formatTime(quip.created_at)]),
      ]),
      this.isOwner()
        ? createEl(
            "button",
            {
              className: "quip-delete-btn",
              title: "Delete quip",
              onClick: (e) => {
                e.stopPropagation();
                this.handleDelete();
              },
            },
            ["🗑️"]
          )
        : null,
    ]);
  }

  renderContent() {
    const content = createEl("div", { className: "quip-content" });
    content.innerHTML = escapeHtml(this.quip.content);
    return content;
  }

  renderDefinition() {
    return createEl("div", { className: "quip-definition" }, [
      createEl("div", { className: "quip-definition-label" }, ["Definition"]),
      createEl("div", { className: "quip-definition-text" }, [
        this.quip.definition,
      ]),
    ]);
  }

  renderExamples() {
    return createEl("div", { className: "quip-examples" }, [
      createEl("div", { className: "quip-examples-label" }, ["Usage"]),
      createEl("div", { className: "quip-examples-text" }, [
        this.quip.usage_examples,
      ]),
    ]);
  }

  getUpsCount() {
    return this.quip.quip_ups_count ?? this.quip.ups_count ?? 0;
  }

  renderActions() {
    const { quip } = this;
    const upsCount = this.getUpsCount();

    return createEl("footer", { className: "quip-actions" }, [
      this.renderAction(
        quip.is_upped ? "❤️" : "🤍",
        upsCount,
        () => this.handleUp(),
        quip.is_upped
      ),
      this.renderAction("💬", quip.comments_count || 0, () =>
        router.navigate(`/quips/${quip.id}`)
      ),
      this.renderAction(
        quip.is_reposted ? "✅" : "🔄",
        quip.reposts_count || 0,
        () => this.handleRepost(),
        quip.is_reposted
      ),
    ]);
  }

  renderAction(icon, count, onClick, active = false) {
    return createEl(
      "button",
      {
        className: `quip-action ${active ? "active" : ""}`,
        onClick,
      },
      [
        createEl("span", { className: "quip-action-icon" }, [icon]),
        count > 0 ? createEl("span", {}, [String(count)]) : null,
      ]
    );
  }

  async handleUp() {
    if (!state.isAuthenticated()) {
      router.navigate("/login");
      return;
    }

    try {
      if (this.quip.is_upped) {
        await api.removeUpQuip(this.quip.id);
        this.quip.is_upped = false;
        const count = this.getUpsCount();
        this.quip.quip_ups_count = Math.max(0, count - 1);
      } else {
        await api.upQuip(this.quip.id);
        this.quip.is_upped = true;
        const count = this.getUpsCount();
        this.quip.quip_ups_count = count + 1;
      }
      this.update();
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async handleRepost() {
    if (!state.isAuthenticated()) {
      router.navigate("/login");
      return;
    }

    try {
      if (this.quip.is_reposted) {
        await api.removeRepostQuip(this.quip.id);
        this.quip.is_reposted = false;
        this.quip.reposts_count = Math.max(0, (this.quip.reposts_count || 1) - 1);
        showToast("Repost removed", "success");
      } else {
        await api.repostQuip(this.quip.id);
        this.quip.is_reposted = true;
        this.quip.reposts_count = (this.quip.reposts_count || 0) + 1;
        showToast("Reposted!", "success");
      }
      this.update();
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async handleDelete() {
    if (!confirm("Are you sure you want to delete this quip?")) {
      return;
    }

    try {
      await api.deleteQuip(this.quip.id);
      showToast("Quip deleted", "success");
      if (this.el && this.el.parentNode) {
        this.el.parentNode.removeChild(this.el);
      }
      if (this.options.onDelete) {
        this.options.onDelete(this.quip.id);
      }
    } catch (err) {
      showToast(err.message, "error");
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
