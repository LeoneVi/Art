# Art Gallery — drop-in files

Copy the `content/`, `data/`, and `themes/mytheme/` folders into your existing
repo (merge, don't overwrite `themes/mytheme/layouts/baseof.html`).

## 1. Register taxonomies

In `hugo.toml` (or `config.yaml`), add:

```toml
[taxonomies]
  medium = "mediums"
  tag = "tags"
```

This makes `site.Taxonomies.mediums` / `site.Taxonomies.tags` available,
which `filter-bar.html` uses to auto-generate filter buttons.

## 2. Wire main.css into your CSS bundle

You already scope CSS per layout via `resources.Concat` with a
layout-specific cache key in `baseof.html`. Point that bundle at
`assets/css/main.css` — since it's just `@import`s of the base + component
files, no changes to your existing Concat logic are needed. The `gallery`
layout (`content/gallery/_index.md` sets `layout: "gallery"`) will pick up
its own cache key automatically from your existing
`printf "css/main-%s.css" (.Layout | default "default")` pattern.

## 3. Load the filter JS

In `baseof.html`, near the closing `</body>`, add (only needs to load on
gallery pages):

```go-html-template
{{ if eq .Layout "gallery" }}
  {{ $filterJS := resources.Get "js/gallery-filter.js" }}
  <script src="{{ $filterJS.RelPermalink }}" defer></script>
{{ end }}
```

## 4. Wire header/footer into baseof.html

```go-html-template
{{ partial "header.html" . }}
<main>{{ block "main" . }}{{ end }}</main>
{{ partial "footer.html" . }}
```

## 5. Update your social links

Edit `data/social.yaml` with your real Twitter / Instagram / Tumblr URLs.

## 6. Add your artwork

One file per piece in `content/gallery/`, following `piece-01.md`'s front
matter shape. Set `featured: true` for anything that should appear in the
top "Selected Work" section. `orientation` (`portrait` / `landscape` /
`square`) controls how it's sized in that featured grid so shapes stay
varied rather than uniform squares. Drop the actual image files under
`static/img/gallery/`.

## File map

```
content/gallery/_index.md          gallery landing page (layout: gallery)
content/gallery/piece-01.md        example artwork entry

data/social.yaml                   twitter/instagram/tumblr, used by header+footer

themes/mytheme/layouts/
  gallery/list.html                assembles featured + feed
  gallery/single.html              individual artwork page
  partials/header.html
  partials/footer.html
  partials/social-icons.html       loops data/social.yaml
  partials/gallery/featured.html   "Selected Work" — featured: true pieces
  partials/gallery/feed.html       full instagram-style feed, all pieces
  partials/gallery/filter-bar.html search input + medium/tag buttons

themes/mytheme/assets/css/
  base/_variables.css              cream bg, chocolate text, spacing, fonts
  base/_typography.css
  base/_reset.css
  components/_header.css
  components/_footer.css
  components/_gallery-featured.css
  components/_gallery-feed.css     CSS-columns masonry, non-square images
  components/_filter-bar.css
  main.css                         imports all of the above

themes/mytheme/assets/js/
  gallery-filter.js                search + medium/tag filtering, no framework
```
