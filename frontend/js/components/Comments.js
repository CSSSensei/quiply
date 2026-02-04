import { api } from "../api.js";
import { state } from "../state.js";
import { router } from "../router.js";
import { formatTime, getInitials, escapeHtml, createEl, showToast } from "../utils.js";

const MAX_COMMENT_LENGTH = 1000;

export class Comments {
  constructor(quipId) {
    this.quipId = quipId;
    this.comments = [];
    this.loading = true;
    this.replyTo = null;
    this.newComment = "";
    this.el = null;
  }

  async load() {
    try {
      const response = await api.getComments(this.quipId);
      this.comments = Array.isArray(response) ? response : (response.data || []);
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      this.loading = false;
      this.update();
    }
  }

  render() {
    this.el = createEl("div", { className: "comments-section" }, [
      createEl("h3", { className: "comments-header" }, [
        `Comments (${this.comments.length})`,
      ]),
      this.loading
        ? this.renderLoading()
        : this.comments.length > 0
        ? this.renderComments()
        : this.renderEmpty(),
      this.renderForm(),
    ]);

    return this.el;
  }

  renderLoading() {
    return createEl("div", { className: "loading-container" }, [
      createEl("div", { className: "spinner" }),
    ]);
  }

  renderEmpty() {
    return createEl("div", { className: "empty-state" }, [
      createEl("div", { className: "empty-state-icon" }, ["💬"]),
      createEl("div", { className: "empty-state-title" }, ["No comments yet"]),
      createEl("div", { className: "empty-state-text" }, [
        "Be the first to comment!",
      ]),
    ]);
  }

  renderComments() {
    return createEl(
      "div",
      { className: "comments-list" },
      this.buildCommentTree(this.comments).map((c) => this.renderComment(c))
    );
  }

  buildCommentTree(comments) {
    if (comments.length > 0 && comments[0].replies !== undefined) {
      return comments;
    }
    
    // Fallback: build tree from flat list using parent_comment_id
    const map = new Map();
    const roots = [];

    comments.forEach((c) => {
      map.set(c.id, { ...c, replies: [] });
    });

    comments.forEach((c) => {
      const comment = map.get(c.id);
      const parentId = c.parent_comment_id || c.parent_id;
      if (parentId && map.has(parentId)) {
        map.get(parentId).replies.push(comment);
      } else {
        roots.push(comment);
      }
    });

    return roots;
  }

  renderComment(comment, depth = 0) {
    const username = comment.username || comment.author?.username || "Unknown";
    const upsCount = comment.comment_ups_count ?? comment.ups_count ?? 0;
    
    return createEl("div", { className: "comment" }, [
      createEl("div", { className: "comment-avatar" }, [
        getInitials(username),
      ]),
      createEl("div", { className: "comment-body" }, [
        createEl("div", { className: "comment-header" }, [
          createEl("span", { className: "comment-author" }, [
            username,
          ]),
          createEl("span", { className: "comment-time" }, [
            formatTime(comment.created_at),
          ]),
        ]),
        createEl("div", { className: "comment-content" }, [
          escapeHtml(comment.content),
        ]),
        createEl("div", { className: "comment-actions" }, [
          createEl(
            "button",
            {
              className: "comment-action",
              onClick: () => this.handleUpComment(comment),
            },
            [comment.is_upped ? "❤️" : "🤍", ` ${upsCount}`]
          ),
          depth < 3
            ? createEl(
                "button",
                {
                  className: "comment-action",
                  onClick: () => {
                    this.replyTo = comment.id;
                    this.update();
                  },
                },
                ["Reply"]
              )
            : null,
        ]),
        comment.replies?.length > 0
          ? createEl(
              "div",
              { className: "comment-replies" },
              comment.replies.map((r) => this.renderComment(r, depth + 1))
            )
          : null,
      ]),
    ]);
  }

  renderForm() {
    if (!state.isAuthenticated()) {
      return createEl("div", { className: "comment-form" }, [
        createEl("p", { className: "text-secondary text-center" }, [
          "Please ",
          createEl("a", { href: "#/login" }, ["log in"]),
          " to comment.",
        ]),
      ]);
    }

    return createEl("form", {
      className: "comment-form",
      onSubmit: (e) => {
        e.preventDefault();
        this.handleSubmit();
      },
    }, [
      createEl("div", { className: "comment-avatar" }, [
        getInitials(state.user.username),
      ]),
      createEl("div", { className: "flex-1 flex flex-col gap-sm" }, [
        this.replyTo
          ? createEl("div", { className: "text-secondary text-sm flex items-center gap-sm" }, [
              `Replying to comment`,
              createEl(
                "button",
                {
                  className: "btn btn-ghost btn-sm",
                  type: "button",
                  onClick: () => {
                    this.replyTo = null;
                    this.update();
                  },
                },
                ["✕"]
              ),
            ])
          : null,
        createEl("div", { className: "flex flex-col gap-sm" }, [
          createEl("textarea", {
            className: "comment-form-input",
            placeholder: "Write a comment...",
            rows: 2,
            value: this.newComment,
            maxLength: MAX_COMMENT_LENGTH,
            onInput: (e) => {
              this.newComment = e.target.value;
              this.updateCharacterCount();
              const btn = this.el?.querySelector('.btn-primary');
              if (btn) {
                btn.disabled = !this.newComment.trim();
              }
            },
          }),
          createEl("div", { className: "text-secondary text-sm text-right" }, [
            `${MAX_COMMENT_LENGTH - this.newComment.length} characters remaining`
          ]),
        ]),
      ]),
      createEl(
        "button",
        {
          className: "btn btn-primary btn-sm",
          type: "submit",
          disabled: !this.newComment.trim(),
        },
        ["Post"]
      ),
    ]);
  }

  async handleSubmit() {
    if (!this.newComment.trim()) return;

    try {
      const response = await api.createComment(
        this.quipId,
        this.newComment.trim(),
        this.replyTo
      );

      this.comments.push(response.data);
      this.newComment = "";
      this.replyTo = null;
      showToast("Comment posted!", "success");
      this.update();
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  updateCharacterCount() {
    const counter = this.el?.querySelector('.text-secondary.text-sm.text-right');
    if (counter) {
      counter.textContent = `${MAX_COMMENT_LENGTH - this.newComment.length} characters remaining`;
    }
  }

  async handleUpComment(comment) {
    if (!state.isAuthenticated()) {
      router.navigate("/login");
      return;
    }

    try {
      if (comment.is_upped) {
        await api.removeUpComment(comment.id);
        comment.is_upped = false;
        const count = comment.comment_ups_count ?? comment.ups_count ?? 1;
        comment.comment_ups_count = Math.max(0, count - 1);
      } else {
        await api.upComment(comment.id);
        comment.is_upped = true;
        const count = comment.comment_ups_count ?? comment.ups_count ?? 0;
        comment.comment_ups_count = count + 1;
      }
      this.update();
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
