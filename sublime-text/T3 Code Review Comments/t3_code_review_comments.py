import html
import json
import os
import re
import subprocess
import uuid

import sublime
import sublime_plugin

T3 = os.path.expanduser("~/.t3/bin/t3")

_comments = {}  # view.id() -> [{"id": str, "text": str}]
_phantoms = {}  # view.id() -> PhantomSet
# Scope of the commented lines. Not a region.* scope: those cannot set the text color.
# Add a rule with "background" and "foreground" for it to the color scheme.
SCOPE = "markup.t3-code-review-comments"

# Same look as the Sublime LSP hover popup (LSP/popups.css and mdpopups default.css).
STYLE = """
<style>
  html, body { margin: 0; padding: 0; }
  .border { border: 1px solid color(var(--foreground) alpha(0.25)); border-radius: 0.25rem; }
  html.dark .box { background-color: color(var(--background) blend(white 95%)); }
  html.light .box { background-color: color(var(--background) blend(black 95%)); }
  body { font-family: system; font-size: 1rem; line-height: 1.1rem; color: var(--foreground); }
  a { color: var(--bluish); }
  .wrapper { padding: 0.5rem; }
  .actions { background-color: color(var(--foreground) alpha(0.1)); }
  .actions a { text-decoration: none; }
</style>
"""


def _html(*parts, border=False):
    """Return a popup or phantom body. Each part is (class, html) and shows as one LSP-style block.
    Popups get their border from the theme. Phantoms need border=True."""
    return ('<body id="t3-code-review-comments">' + STYLE
            + '<div class="box' + (' border' if border else '') + '">'
            + "".join('<div class="' + cls + '">' + content + "</div>" for cls, content in parts)
            + "</div></body>")


def _settings():
    return sublime.load_settings("T3 Code Review Comments.sublime-settings")


def _run(args, stdin=None):
    p = subprocess.run(args, input=stdin.encode() if stdin else None, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout).decode().strip()[:300])
    return p.stdout.decode()


def _plural(n, word):
    return "{} {}{}".format(n, word, "" if n == 1 else "s")


def _error(e):
    sublime.set_timeout(lambda: sublime.status_message("T3 Code error: {}".format(e)), 0)


def _query(sql):
    # The CLI is slow to start (Electron) and has no "project list" command,
    # so read T3 Code's local state directly (read-only).
    db = os.path.expanduser(_settings().get("state_db", "~/.t3/userdata/statev2.sqlite"))
    out = _run(["/usr/bin/sqlite3", "-readonly", "-json", db, sql])
    return json.loads(out) if out.strip() else []


def _projects():
    return _query("select project_id as id, title, workspace_root as root "
                  "from projection_projects where deleted_at is null order by updated_at desc")


def _project_for(path, projects):
    """Return the project with the longest workspace root that contains path."""
    if not path:
        return None
    path = os.path.realpath(path)
    best, best_len = None, -1
    for p in projects:
        root = os.path.realpath(p["root"]).rstrip(os.sep)
        if (path == root or path.startswith(root + os.sep)) and len(root) > best_len:
            best, best_len = p, len(root)
    return best


def _threads(project_id):
    """Active top-level threads, newest first. Same result as `t3 thread list` without
    settled and subagent threads."""
    if not re.fullmatch(r"[\w:-]+", project_id):
        return []
    return _query("""
        select thread_id as threadId, title, updated_at as updatedAt,
               json_extract(payload_json, '$.modelSelection.model') as model
        from orchestration_v2_projection_threads
        where project_id = '{}' and deleted_at is null and archived_at is null
          and json_extract(payload_json, '$.lineage.parentThreadId') is null
          and coalesce(json_extract(payload_json, '$.settledOverride'), '') != 'settled'
          and (json_extract(payload_json, '$.settledAt') is null
               or json_extract(payload_json, '$.settledOverride') = 'active')
        order by updated_at desc""".format(project_id))


def _key(cid):
    return "t3c_" + cid


def _add(view, cid, region):
    # The gutter icon takes the foreground color of the scope. SCOPE has a light foreground
    # for the text, so draw the icon with a second region that has no fill and no outline.
    view.add_regions(_key(cid), [region], SCOPE, "", sublime.DRAW_NO_OUTLINE)
    view.add_regions(_key(cid) + "_icon", [region], "region.bluish", "bookmark",
                     sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)


def _erase(view, cid):
    view.erase_regions(_key(cid))
    view.erase_regions(_key(cid) + "_icon")


def _region(view, cid):
    regions = view.get_regions(_key(cid))
    return regions[0] if regions else None


def _render(view):
    ps = _phantoms.setdefault(view.id(), sublime.PhantomSet(view, "t3_code_review_comments"))
    out = []
    for c in _comments.get(view.id(), []):
        r = _region(view, c["id"])
        if r is None:
            continue
        text = html.escape(c["text"]).replace("\n", "<br>")
        actions = " | ".join([
            '<a href="edit:' + c["id"] + '">Edit</a>',
            '<a href="del:' + c["id"] + '">Delete</a>',
        ])
        body = _html(("wrapper", text), ("wrapper actions", actions), border=True)
        anchor = sublime.Region(view.line(r.end()).b)
        out.append(sublime.Phantom(anchor, body, sublime.LAYOUT_BLOCK,
                                   lambda href, v=view: _navigate(v, href)))
    ps.update(out)


def _navigate(view, href):
    action, _, cid = href.partition(":")
    items = _comments.get(view.id(), [])
    if action == "del":
        _erase(view, cid)
        _comments[view.id()] = [c for c in items if c["id"] != cid]
        _render(view)
    elif action == "edit":
        item = next((c for c in items if c["id"] == cid), None)
        if item:
            def done(text):
                item["text"] = text
                _render(view)
            view.window().show_input_panel("Edit comment:", item["text"], done, None, None)


def _line_range(view, sel):
    end = sel.end()
    # A gutter drag ends at column 0 of the next line; do not include that line.
    if not sel.empty() and view.rowcol(end)[1] == 0:
        end -= 1
    return sublime.Region(view.line(sel.begin()).a, view.line(end).b)


class T3CodeReviewCommentsAddCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        region = _line_range(self.view, self.view.sel()[0])
        a = self.view.rowcol(region.a)[0] + 1
        b = self.view.rowcol(region.b)[0] + 1

        def done(text):
            if not text.strip():
                return
            cid = uuid.uuid4().hex[:8]
            _add(self.view, cid, region)
            _comments.setdefault(self.view.id(), []).append({"id": cid, "text": text})
            _render(self.view)

        label = "Comment on line {}:".format(a) if a == b else "Comment on lines {}-{}:".format(a, b)
        self.view.window().show_input_panel(label, "", done, None, None)


def _snapshot(window):
    """Main thread. Copy the comments of all files in the window, with their current
    line ranges and code. The active file comes first."""
    active = window.active_view()
    views = sorted(window.views(), key=lambda v: v != active)
    snap = []
    for view in views:
        for c in _comments.get(view.id(), []):
            r = _region(view, c["id"])
            if r is not None:
                snap.append({"id": c["id"], "view": view, "text": c["text"],
                             "path": os.path.realpath(view.file_name() or "untitled"),
                             "code": view.substr(r),
                             "a": view.rowcol(r.a)[0] + 1, "b": view.rowcol(r.b)[0] + 1})
    return snap


def _attr(value):
    return (value.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _review_block(file_path, s):
    """One comment in T3 Code's <review_comment> text format, with the same fields as a
    comment from T3 Code's file browser. The T3 Code UI shows it as a chip."""
    a, b = s["a"], s["b"]
    longest = max([len(m) for m in re.findall(r"`+", s["code"])] or [0])
    fence = "`" * max(3, longest + 1)
    lang = os.path.splitext(file_path)[1].lstrip(".").lower() or "text"
    attrs = " ".join('{}="{}"'.format(k, _attr(str(v))) for k, v in [
        ("sectionId", "file:" + file_path),
        ("sectionTitle", "File comment"),
        ("filePath", file_path),
        ("rangeLabel", "L{}".format(a) if a == b else "L{} to L{}".format(a, b)),
        ("startIndex", a - 1),
        ("endIndex", b - 1),
    ])
    return "<review_comment {}>\n{}\n\n{}{}\n{}\n{}\n</review_comment>".format(
        attrs, s["text"], fence, lang, s["code"].rstrip(), fence)


def _format(snap, project):
    root = os.path.realpath(project["root"]).rstrip(os.sep) + os.sep
    parts = []
    for s in snap:
        path = s["path"]
        file_path = os.path.relpath(path, root) if path.startswith(root) else path
        # A markdown link to "path:line" is a file chip that opens T3 Code's file browser.
        # The review comment chip only shows a details card when clicked.
        href = "<{}>".format(path) if re.search(r"[\s()<>]", path) else path
        parts.append("[{}:{}]({}:{})\n{}".format(os.path.basename(path), s["a"], href, s["a"],
                                                 _review_block(file_path, s)))
    # T3 Code folds messages from the CLI and shows their first line as plain text.
    # Without a prefix, the first line is plain text, not a markdown link.
    prefix = _settings().get("prompt_prefix", "").strip() or "Review comments"
    return "\n\n".join([prefix] + parts)


def _clear(snap):
    for view in {s["view"].id(): s["view"] for s in snap}.values():
        ids = {s["id"] for s in snap if s["view"] == view}
        for cid in ids:
            _erase(view, cid)
        _comments[view.id()] = [c for c in _comments.get(view.id(), []) if c["id"] not in ids]
        _render(view)


def _pick_project(window, projects, snap):
    """Main thread. Show all T3 Code projects."""
    if not projects:
        return sublime.status_message("T3 Code: no projects")
    items = [sublime.QuickPanelItem(p["title"], annotation=p["root"].replace(os.path.expanduser("~"), "~"))
             for p in projects]

    def on_select(i):
        if i >= 0:
            sublime.set_timeout_async(lambda: _pick_thread(window, projects[i], projects, snap), 0)

    window.show_quick_panel(items, on_select, placeholder="T3 Code project")


def _pick_thread(window, project, projects, snap):
    """Worker thread. Load the project's threads, then show them with "new" and "other project"."""
    try:
        threads = _threads(project["id"])
    except Exception as e:
        return _error(e)

    items = [sublime.QuickPanelItem("+ New thread", annotation=project["title"])]
    items += [sublime.QuickPanelItem(t["title"], annotation=(t["updatedAt"] or "")[:10],
                                     details=t["model"] or "") for t in threads]
    items.append(sublime.QuickPanelItem("Other project…"))

    last = window.settings().get("t3_code_review_comments_thread_id")
    selected = next((i + 1 for i, t in enumerate(threads) if t["threadId"] == last), 0)

    def on_select(i):
        if i < 0:
            return
        if i == 0:
            sublime.set_timeout_async(lambda: _deliver(window, snap, project), 0)
        elif i == len(items) - 1:
            _pick_project(window, projects, snap)
        else:
            tid = threads[i - 1]["threadId"]
            sublime.set_timeout_async(lambda: _deliver(window, snap, project, thread_id=tid), 0)

    files = len({s["path"] for s in snap})
    placeholder = "T3 Code thread in {} ({} in {})".format(
        project["title"], _plural(len(snap), "comment"), _plural(files, "file"))
    sublime.set_timeout(lambda: window.show_quick_panel(
        items, on_select, selected_index=selected, placeholder=placeholder), 0)


def _deliver(window, snap, project, thread_id=None):
    """Worker thread. Send to an existing thread, or start a new one in project."""
    msg = _format(snap, project)
    try:
        if thread_id:
            _run([T3, "thread", "send", thread_id, "-"], msg)
        else:
            names = list(dict.fromkeys(os.path.basename(s["path"]) for s in snap))
            title = "Review: " + (", ".join(names) if len(names) <= 3 else "{} files".format(len(names)))
            out = _run([T3, "thread", "start", project["id"], "-", "--json", "--title", title], msg)
            thread_id = json.loads(out).get("threadId")
    except Exception as e:
        return _error(e)

    def done():
        if thread_id:
            window.settings().set("t3_code_review_comments_thread_id", thread_id)
        _clear(snap)
        sublime.status_message("T3 Code: sent " + _plural(len(snap), "comment"))

    sublime.set_timeout(done, 0)


def _has_comments(window):
    return any(_comments.get(v.id()) for v in window.views())


class T3CodeReviewCommentsSendCommand(sublime_plugin.WindowCommand):
    """Send the comments of all files in the window as one message."""

    def is_enabled(self):
        return _has_comments(self.window)

    def run(self):
        window = self.window
        active = window.active_view() and window.active_view().file_name()
        snap = _snapshot(window)
        if not snap:
            return sublime.status_message("T3 Code: no comments")

        def load():
            try:
                projects = _projects()
            except Exception as e:
                return _error(e)
            # Use the project of the active file. If it has none, use the first file that has one.
            paths = [active] + [s["path"] for s in snap]
            project = next((p for p in (_project_for(f, projects) for f in paths) if p), None)
            if project:
                _pick_thread(window, project, projects, snap)
            else:
                sublime.set_timeout(lambda: _pick_project(window, projects, snap), 0)

        sublime.set_timeout_async(load, 0)


class T3CodeReviewCommentsListener(sublime_plugin.EventListener):
    def on_hover(self, view, point, hover_zone):
        if hover_zone != sublime.HOVER_GUTTER:
            return

        def nav(_):
            view.hide_popup()
            line = view.line(point)
            if not any(s.contains(line) for s in view.sel()):
                view.sel().clear()
                view.sel().add(line)
            view.run_command("t3_code_review_comments_add")

        def show():
            # Other plugins (SublimeLinter, LSP) can show a popup for the same hover. A view shows only one popup,
            # so do not replace theirs: their information is more important than this action.
            if view.is_popup_visible():
                return
            # &nbsp;: minihtml does not make a normal space in a link clickable.
            view.show_popup(_html(("wrapper actions", '<a href="add">Add&nbsp;comment</a>')),
                            sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, on_navigate=nav)

        # Wait so that the other hover listeners can show their popup first.
        sublime.set_timeout(show, 100)

    def on_query_context(self, view, key, operator, operand, match_all):
        """Key binding context: true if a file in the window has comments that are not sent."""
        if key != "t3_code_review_comments_unsent":
            return None
        window = view.window()
        value = bool(window) and _has_comments(window)
        if operator == sublime.OP_EQUAL:
            return value == bool(operand)
        if operator == sublime.OP_NOT_EQUAL:
            return value != bool(operand)
        return None

    def on_close(self, view):
        _comments.pop(view.id(), None)
        _phantoms.pop(view.id(), None)
