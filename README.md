# Sublime Text personal settings

As the title says, these are my personal settings for Sublime Text.

## Installation

1. Install [Package Control](https://sublime.wbond.net/installation).
2. Clone this repo to `~/.subl`.
3. Run `cp Package\ Control.sublime-settings ~/Library/Application\ Support/Sublime\ Text/Packages/User/
` so that Sublime Text can install all necessary packages first (you can open console with View → Show Console to see progress). If installation is going slow, system gets unresponsive or some packages don’t get installed, try installing them manually one by one.
4. After installation, run `~/.subl/bin/symlink`. This will symlink all necessary files to Sublime Text user folder so you can keep your preferences in version control without messing up standard User folder.
