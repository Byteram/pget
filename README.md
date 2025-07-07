# pget

# pget

**pget** is a cross-platform, Python-native package manager for userland CLI apps on Linux and macOS.

- Installs apps to `~/.pget/bin/`
- No `sudo`, no system interference
- Inspired by `apt`, `pacman`, and `brew`
- Written 100% in PURE Python ~(wiht extensions)~

---

## Example

```bash
pget install timer
pget remove timer
pget list
pget upgrade
