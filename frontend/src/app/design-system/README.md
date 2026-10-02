# Design system

Everything the app looks like is decided here. Views and components only name
patterns (`ds-card`, `ds-field`, `ds-badge--danger`); they never set a color, a
size or a spacing value themselves.

## Files

```
design-system/
  README.md                   this file
  theme.scss                  the entry point src/styles.scss loads
  index.ts                    barrel for the TypeScript side
  tokens.ts                   typed token map plus helpers
  tokens/
    _tokens.scss              the theme: every custom property, light and dark
    _breakpoints.scss         Sass breakpoints, emits no CSS
  patterns/
    _reset.scss               element baseline, replaces Bootstrap's reboot
    _layout.scss              page shell, clusters, detail rows, text helpers
    _nav.scss                 top bar
    _card.scss                card header, body, footer, loading and empty state
    _form.scss                label, control, addon group, hint
    _button.scss              primary, danger, quiet, block
    _table.scss               data table and pagination
    _feedback.scss            alert, badge, spinner
```

## Swapping the theme

Replace `tokens/_tokens.scss`. That file declares custom properties and nothing
else, so a replacement only has to cover the same property names. No pattern,
view or component needs an edit.

If you would rather keep both files side by side, add yours next to it and
change the one `@use 'tokens/tokens';` line in `theme.scss` to point at it.

Two rules for a replacement file:

- define every `--ds-*` property the current file defines, or patterns fall back
  to whatever the browser does with an empty `var()`
- do not import anything from `patterns/`, and do not emit selectors other than
  `:root`

Breakpoints are the one exception to the custom property rule, because a media
query cannot read `var()`. They are Sass variables in `tokens/_breakpoints.scss`
and are changed there.

## Dark mode

`tokens/_tokens.scss` ships a dark palette twice: once under
`prefers-color-scheme: dark` for viewers who have not chosen, and once under
`[data-ds-theme="dark"]` for an explicit toggle. Setting
`data-ds-theme="light"` on `<html>` pins the light palette against the system
preference. From TypeScript:

```ts
import { applyThemeMode } from './design-system';

applyThemeMode('dark', document.documentElement);
```

## Reading tokens from code

Prefer `tokenVar`, which produces `var(--ds-x, default)` so a theme override
still wins. `tokenValue` hands back the light theme literal for code that cannot
take a `var()`, such as a canvas. `resolveToken` asks the browser what a token
currently computes to, which is the only way to see an override in effect.

```ts
import { designTokens, tokenVar, resolveToken } from './design-system';

element.style.borderColor = tokenVar('color-border');
const spacing = resolveToken('space-4', document.documentElement);
designTokens['color-danger'].variable; // '--ds-color-danger'
```

The token names in `tokens.ts` mirror the custom properties in
`tokens/_tokens.scss` with the `--ds-` prefix stripped. The stylesheet is the
source of truth; when you add a property there, add it here too.

## Adding a pattern

A pattern earns its place once two views need it. Put it in its own file under
`patterns/`, register it in `theme.scss`, and build it only out of `var(--ds-*)`
values. A one-off stays in the component's own stylesheet, where it should still
use tokens rather than literals.
