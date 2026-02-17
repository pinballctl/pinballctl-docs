# Manual

The Manual feature provides built-in documentation inside Pinball CTL.

<img src="/api/manual/assets/screenshots/feature-manual.png" alt="Manual feature overview" style="width: 100%; max-width: 800px; height: auto;">

The Manual is the in-app knowledge base for user guides and technical references.

## What This Feature Does

It lets you browse, search, bookmark, and read documentation without leaving Pinball CTL.

## Page Layout

The page is split into two columns:

- Left sidebar: search, tree, results, bookmarks.
- Right content area: toolbar, table of contents, article body.

## Left Sidebar Controls

### Search box

- Filters docs by query.
- Switches view from tree to search results when active.
- Includes status text for results.

### Tree navigation

- Expand/collapse folder structure.
- Open pages directly.
- Remembers expanded folders.

### Bookmarks block

- Shows saved document shortcuts.
- Supports removing bookmarks from the list.

## Article Toolbar Controls

### Table of Content button

- Opens generated heading index for current page.
- Links jump to section anchors.

### Bookmark button

- Adds/removes current page from bookmarks.
- Bookmark state is persisted.

## Reading Behaviour

- Internal manual links open inside the manual viewer.
- External links open in new tab and are marked as external.
- Images support click-to-open modal for large view.
- Modal closes on click or `Esc`.

## Image Viewer

In-article images can be inspected in a full-size modal.

Behaviour:

- Click image to open.
- Cursor shows zoom-out style in modal.
- Click anywhere in modal to close.

## Typical Workflow

1. Search for the feature/topic.
2. Open page from results or tree.
3. Use table of contents for section jumps.
4. Bookmark frequent pages.

## Practical Examples

### Build operator quick-reference list

Bookmark the pages you use most often:

- Getting Started
- Rules
- Lighting
- Service Log

### Maintenance handover

Use bookmarks + ToC links to quickly move through required checklists during handover.

## Related Features

- [Interface Tour](2-interface.md)
- [Features](3-featured.md)
