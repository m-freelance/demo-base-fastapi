/**
 * Typed view of the design tokens for code that cannot read a stylesheet.
 *
 * The CSS custom properties in tokens/_tokens.scss are the source of truth.
 * The `value` here is the light theme default, useful as a var() fallback or
 * for canvas and chart code; anything that renders in the DOM should prefer
 * `tokenVar` so a theme override still applies.
 */

/** A single token: the custom property name and its light theme default. */
export interface DesignToken {
  readonly variable: `--ds-${string}`;
  readonly value: string;
}

export const designTokens = {
  // Typography
  'font-family-base': {
    variable: '--ds-font-family-base',
    value: "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif",
  },
  'font-family-mono': {
    variable: '--ds-font-family-mono',
    value: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
  },
  'font-size-xs': { variable: '--ds-font-size-xs', value: '0.75rem' },
  'font-size-sm': { variable: '--ds-font-size-sm', value: '0.875rem' },
  'font-size-md': { variable: '--ds-font-size-md', value: '1rem' },
  'font-size-lg': { variable: '--ds-font-size-lg', value: '1.25rem' },
  'font-size-xl': { variable: '--ds-font-size-xl', value: '1.5rem' },
  'font-size-2xl': { variable: '--ds-font-size-2xl', value: '2rem' },
  'font-size-display': { variable: '--ds-font-size-display', value: '4rem' },
  'font-weight-regular': { variable: '--ds-font-weight-regular', value: '400' },
  'font-weight-medium': { variable: '--ds-font-weight-medium', value: '500' },
  'font-weight-semibold': { variable: '--ds-font-weight-semibold', value: '600' },
  'font-weight-bold': { variable: '--ds-font-weight-bold', value: '700' },
  'line-height-tight': { variable: '--ds-line-height-tight', value: '1.2' },
  'line-height-base': { variable: '--ds-line-height-base', value: '1.5' },
  'line-height-relaxed': { variable: '--ds-line-height-relaxed', value: '1.75' },

  // Spacing, 4px base unit
  'space-0': { variable: '--ds-space-0', value: '0' },
  'space-1': { variable: '--ds-space-1', value: '0.25rem' },
  'space-2': { variable: '--ds-space-2', value: '0.5rem' },
  'space-3': { variable: '--ds-space-3', value: '0.75rem' },
  'space-4': { variable: '--ds-space-4', value: '1rem' },
  'space-5': { variable: '--ds-space-5', value: '1.5rem' },
  'space-6': { variable: '--ds-space-6', value: '2rem' },
  'space-7': { variable: '--ds-space-7', value: '3rem' },

  // Shape
  'radius-sm': { variable: '--ds-radius-sm', value: '0.25rem' },
  'radius-md': { variable: '--ds-radius-md', value: '0.375rem' },
  'radius-lg': { variable: '--ds-radius-lg', value: '0.5rem' },
  'radius-pill': { variable: '--ds-radius-pill', value: '50rem' },
  'radius-circle': { variable: '--ds-radius-circle', value: '50%' },
  'border-width': { variable: '--ds-border-width', value: '1px' },
  'border-width-strong': { variable: '--ds-border-width-strong', value: '2px' },

  // Elevation
  'shadow-none': { variable: '--ds-shadow-none', value: 'none' },
  'shadow-sm': { variable: '--ds-shadow-sm', value: '0 0.125rem 0.25rem rgba(0, 0, 0, 0.075)' },
  'shadow-md': { variable: '--ds-shadow-md', value: '0 0.5rem 1rem rgba(0, 0, 0, 0.15)' },
  'shadow-lg': { variable: '--ds-shadow-lg', value: '0 1rem 3rem rgba(0, 0, 0, 0.175)' },

  // Motion
  'duration-fast': { variable: '--ds-duration-fast', value: '120ms' },
  'duration-base': { variable: '--ds-duration-base', value: '300ms' },
  'easing-standard': { variable: '--ds-easing-standard', value: 'ease-in-out' },

  // Layout
  'layout-page-max-width': { variable: '--ds-layout-page-max-width', value: '1140px' },
  'layout-form-max-width': { variable: '--ds-layout-form-max-width', value: '400px' },
  'layout-nav-height': { variable: '--ds-layout-nav-height', value: '56px' },
  'z-nav': { variable: '--ds-z-nav', value: '1000' },

  // Surfaces
  'color-surface-page': { variable: '--ds-color-surface-page', value: '#fafafa' },
  'color-surface-raised': { variable: '--ds-color-surface-raised', value: '#ffffff' },
  'color-surface-sunken': { variable: '--ds-color-surface-sunken', value: '#f8f9fa' },
  'color-surface-hover': { variable: '--ds-color-surface-hover', value: 'rgba(0, 0, 0, 0.04)' },
  'color-surface-inverse': { variable: '--ds-color-surface-inverse', value: '#212529' },
  'color-surface-disabled': { variable: '--ds-color-surface-disabled', value: '#e9ecef' },

  // Text
  'color-text-default': { variable: '--ds-color-text-default', value: '#212529' },
  'color-text-muted': { variable: '--ds-color-text-muted', value: '#6c757d' },
  'color-text-inverse': { variable: '--ds-color-text-inverse', value: '#ffffff' },
  'color-text-disabled': { variable: '--ds-color-text-disabled', value: '#adb5bd' },
  'color-text-link': { variable: '--ds-color-text-link', value: '#0d6efd' },
  'color-text-link-hover': { variable: '--ds-color-text-link-hover', value: '#0a58ca' },

  // Borders
  'color-border': { variable: '--ds-color-border', value: '#dee2e6' },
  'color-border-strong': { variable: '--ds-color-border-strong', value: '#adb5bd' },
  'color-border-inverse': {
    variable: '--ds-color-border-inverse',
    value: 'rgba(255, 255, 255, 0.15)',
  },

  // Primary
  'color-primary': { variable: '--ds-color-primary', value: '#0d6efd' },
  'color-primary-hover': { variable: '--ds-color-primary-hover', value: '#0b5ed7' },
  'color-primary-active': { variable: '--ds-color-primary-active', value: '#0a58ca' },
  'color-primary-on': { variable: '--ds-color-primary-on', value: '#ffffff' },
  'color-primary-surface': { variable: '--ds-color-primary-surface', value: '#cfe2ff' },
  'color-primary-border': { variable: '--ds-color-primary-border', value: '#b6d4fe' },
  'color-primary-text': { variable: '--ds-color-primary-text', value: '#084298' },
  'color-primary-ring': { variable: '--ds-color-primary-ring', value: 'rgba(13, 110, 253, 0.25)' },

  // Danger
  'color-danger': { variable: '--ds-color-danger', value: '#dc3545' },
  'color-danger-hover': { variable: '--ds-color-danger-hover', value: '#bb2d3b' },
  'color-danger-active': { variable: '--ds-color-danger-active', value: '#b02a37' },
  'color-danger-on': { variable: '--ds-color-danger-on', value: '#ffffff' },
  'color-danger-surface': { variable: '--ds-color-danger-surface', value: '#f8d7da' },
  'color-danger-border': { variable: '--ds-color-danger-border', value: '#f5c2c7' },
  'color-danger-text': { variable: '--ds-color-danger-text', value: '#842029' },
  'color-danger-ring': { variable: '--ds-color-danger-ring', value: 'rgba(220, 53, 69, 0.25)' },

  // Success
  'color-success': { variable: '--ds-color-success', value: '#198754' },
  'color-success-hover': { variable: '--ds-color-success-hover', value: '#157347' },
  'color-success-active': { variable: '--ds-color-success-active', value: '#146c43' },
  'color-success-on': { variable: '--ds-color-success-on', value: '#ffffff' },
  'color-success-surface': { variable: '--ds-color-success-surface', value: '#d1e7dd' },
  'color-success-border': { variable: '--ds-color-success-border', value: '#badbcc' },
  'color-success-text': { variable: '--ds-color-success-text', value: '#0f5132' },
  'color-success-ring': { variable: '--ds-color-success-ring', value: 'rgba(25, 135, 84, 0.25)' },

  // Info
  'color-info': { variable: '--ds-color-info', value: '#0dcaf0' },
  'color-info-hover': { variable: '--ds-color-info-hover', value: '#31d2f2' },
  'color-info-active': { variable: '--ds-color-info-active', value: '#3dd5f3' },
  'color-info-on': { variable: '--ds-color-info-on', value: '#212529' },
  'color-info-surface': { variable: '--ds-color-info-surface', value: '#cff4fc' },
  'color-info-border': { variable: '--ds-color-info-border', value: '#b6effb' },
  'color-info-text': { variable: '--ds-color-info-text', value: '#055160' },
  'color-info-ring': { variable: '--ds-color-info-ring', value: 'rgba(13, 202, 240, 0.25)' },

  // Neutral, for secondary emphasis
  'color-neutral': { variable: '--ds-color-neutral', value: '#6c757d' },
  'color-neutral-hover': { variable: '--ds-color-neutral-hover', value: '#5c636a' },
  'color-neutral-active': { variable: '--ds-color-neutral-active', value: '#565e64' },
  'color-neutral-on': { variable: '--ds-color-neutral-on', value: '#ffffff' },
  'color-neutral-surface': { variable: '--ds-color-neutral-surface', value: '#e2e3e5' },
  'color-neutral-border': { variable: '--ds-color-neutral-border', value: '#d3d6d8' },
  'color-neutral-text': { variable: '--ds-color-neutral-text', value: '#41464b' },
  'color-neutral-ring': { variable: '--ds-color-neutral-ring', value: 'rgba(108, 117, 125, 0.25)' },
} as const satisfies Readonly<Record<string, DesignToken>>;

/** Every token name, without the `--ds-` prefix. */
export type DesignTokenName = keyof typeof designTokens;

/** Breakpoints are Sass variables, media queries cannot read custom properties. */
export const breakpoints = {
  sm: 576,
  md: 768,
  lg: 992,
  xl: 1200,
} as const satisfies Readonly<Record<string, number>>;

export type BreakpointName = keyof typeof breakpoints;

/** Themes the token file ships with. `system` leaves it to the media query. */
export type ThemeMode = 'light' | 'dark' | 'system';

/** Attribute on the root element that pins a theme. */
export const THEME_ATTRIBUTE = 'data-ds-theme';

/** `var(--ds-x, default)`, so a missing property still renders sanely. */
export function tokenVar(name: DesignTokenName): string {
  const token: DesignToken = designTokens[name];
  return `var(${token.variable}, ${token.value})`;
}

/** The light theme default, for code that needs a literal rather than a var. */
export function tokenValue(name: DesignTokenName): string {
  return designTokens[name].value;
}

/**
 * Resolves what the browser currently computes for a token, which is the only
 * way to see the effect of a theme override.
 */
export function resolveToken(name: DesignTokenName, element: Element): string {
  const computed = getComputedStyle(element).getPropertyValue(designTokens[name].variable);
  return computed.trim() || designTokens[name].value;
}

/** Pins the theme on an element, or hands it back to the system preference. */
export function applyThemeMode(mode: ThemeMode, element: HTMLElement): void {
  if (mode === 'system') {
    element.removeAttribute(THEME_ATTRIBUTE);
    return;
  }

  element.setAttribute(THEME_ATTRIBUTE, mode);
}
