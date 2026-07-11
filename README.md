#RedDot { background-color: #ff5f56; border-radius: 6px; }
            #YellowDot { background-color: #ffbd2e; border-radius: 6px; }
            #GreenDot { background-color: #27c93f; border-radius: 6px; }

material design light



## Project structure

```
core/
  config.py             paths for config/cache/data dirs
  models.py              LibraryItem / Chapter dataclasses
  database.py             SQLite persistence (thread-safe)
  scanner.py               background QThread scanner
  thumbnail_service.py      CBZ/PDF cover extraction + caching
  natural_sort.py            "Chapter2" < "Chapter10" ordering
ui/
  main_window.py         top bar, favorites filter, wiring
  library_view.py          searchable/filterable grid container
  cover_widget.py            individual cover tile
  flow_layout.py               reflowing gallery layout
resources/
  style.qss             Apple-inspired light theme
```

## Notes on design decisions

- **CBZ** is read via Python's built-in `zipfile` — no external unrar
  dependency needed for this format set.
- **PDF** covers are rendered via PyMuPDF (`fitz`), which also gives us
  fast page counts without opening every page.
- The scanner runs on a background `QThread` so the UI never freezes,
  even on a large library. The SQLite connection is guarded by a lock
  since it's now accessed from both the scanner thread and the UI thread.
- Series vs. single-comic detection: any top-level *folder* inside your
  library path is treated as a series; its cover comes from the first
  chapter (naturally sorted, so `Chapter10` doesn't jump ahead of
  `Chapter2`).

## Suggested Phase 2

- Reader screen (`QGraphicsView` + `QGraphicsScene`) with keyboard
  navigation, zoom, fullscreen, and per-chapter page tracking.
- Comic Details page (progress bar, chapter list, "Continue" button).
- Settings sidebar (Appearance / Reader / Library / About), dark mode.