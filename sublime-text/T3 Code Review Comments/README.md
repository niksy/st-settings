# T3 Code Review Comments

![AI assisted development](https://img.shields.io/badge/ai%20assisted%20development-purple)

Add review comments to lines of code then send them to a T3 Code thread.

## Features

- Hover the gutter and click **Add comment** or select lines and run **T3 Code: Add review comment** from the Command Palette.
- Comments show below the lines with **Edit** and **Delete** links. The popup looks like the Sublime LSP hover popup.
- Run **T3 Code: Send review comments** from the Command Palette to send the comments of all files in the window as one message. The command is available only when there are comments that are not sent.
- The thread picker shows the active threads of the project that contains the file, a **+ New thread** item and an **Other project…** item.
- In T3 Code each comment shows as a file chip and a review comment chip. The file chip opens the file browser at the line. The review comment chip shows the comment and the code.

## Key bindings

You can add these key bindings in **Preferences → Key Bindings**:

```json
{ "keys": ["super+alt+c"], "command": "t3_code_review_comments_add" },
{ "keys": ["super+alt+enter"], "command": "t3_code_review_comments_send" }
```

To make a key binding active only when a file in the window has comments that are not sent, add the `t3_code_review_comments_unsent` context:

```json
{
    "keys": ["super+enter"],
    "command": "t3_code_review_comments_send",
    "context": [{ "key": "t3_code_review_comments_unsent", "operator": "equal", "operand": true }]
}
```

## Color scheme

The commented lines use the `markup.t3-code-review-comments` scope. Add a rule for it to your color scheme in **Preferences → Customize Color Scheme**. If you do not add the rule, the lines can show no fill:

```json
{
    "rules": [
        {
            "scope": "markup.t3-code-review-comments",
            "background": "#3f7ca3",
            "foreground": "#ffffff"
        }
    ]
}
```

The scope does not start with `region.` because Sublime Text does not use `foreground` for `region.*` scopes.

## Settings

- `prompt_prefix`: first line of each message before the comments. T3 Code shows the first line as the header of the folded message. Default: empty, which shows `Review comments`.
- `state_db`: T3 Code state database. Default: `~/.t3/userdata/statev2.sqlite`.

## How it works

- The package sends messages and makes threads with `~/.t3/bin/t3 thread send` and `~/.t3/bin/t3 thread start`.
- The package reads projects and threads from the T3 Code state database with `/usr/bin/sqlite3 -readonly`. The CLI has no command to list projects and it starts Electron each time which takes about 0.7 s.
- Each comment is a markdown file link, e.g. `[a.js:3](/abs/path/a.js:3)`, and a `<review_comment>` block with the same fields as a comment from T3 Code's file browser. T3 Code shows the block as a chip because the UI still reads this older text format.

## Limits

- The database tables and the `<review_comment>` text format are internal to T3 Code. An update can break them.
- A comment is one line of text because the package uses the Sublime input panel.
- The package keeps comments only in memory. If you close a file or restart Sublime Text the comments that you did not send are lost.
- The package works only on macOS because the paths to `t3` and `sqlite3` are macOS paths.
