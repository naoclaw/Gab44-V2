# Gab44 V2 — Design System

> **Purpose**: Any AI reading this file knows every visual rule, CSS class, color token, typography choice, and design constraint. This is the implementation reference — for brand philosophy, see `BRAND_IDENTITY.md`.

---

## 1. Theme System

Gab44 supports light and dark themes. Theme is stored in `localStorage("gab44_theme")` and toggled via `ThemeContext`. The `.dark` class on `<html>` activates dark mode CSS variables.

### Light Theme (`:root`)

| Token | HSL Value | Visual |
|-------|-----------|--------|
| `--background` | `35 40% 95%` | Warm parchment |
| `--foreground` | `240 10% 15%` | Deep charcoal |
| `--card` | `36 35% 98%` | Soft cream |
| `--primary` | `38 92% 50%` | Rich amber |
| `--primary-foreground` | `0 0% 100%` | White |
| `--secondary` | `35 25% 91%` | Light sand |
| `--muted` | `35 25% 91%` | Light sand |
| `--muted-foreground` | `240 5% 45%` | Medium gray |
| `--accent` | `245 50% 95%` | Nebula tint |
| `--accent-foreground` | `245 50% 40%` | Nebula dark |
| `--border` | `35 20% 85%` | Warm gray |
| `--destructive` | `0 84% 60%` | Red |
| `--ring` | `38 92% 50%` | Amber (focus ring) |

### Dark Theme (`.dark`)

| Token | HSL Value | Visual |
|-------|-----------|--------|
| `--background` | `240 15% 6%` | Cosmic void |
| `--foreground` | `40 20% 96%` | Cream white |
| `--card` | `240 15% 8%` | Dark card |
| `--primary` | `42 92% 55%` | Warm gold |
| `--primary-foreground` | `240 10% 10%` | Dark text on gold |
| `--secondary` | `240 10% 14%` | Deep slate |
| `--muted` | `240 10% 14%` | Deep slate |
| `--muted-foreground` | `240 5% 55%` | Light gray |
| `--accent` | `240 10% 14%` | Deep slate |
| `--border` | `240 10% 18%` | Slate edge |

### Cosmic Extended Colors (Tailwind config)

| Token | Hex | Usage |
|-------|-----|-------|
| `cosmic-void` | `#050505` | Deepest black |
| `cosmic-starlight` | `#F8FAFC` | Off-white |
| `cosmic-gold` | `#D4AF37` | Luxury gold accents |
| `cosmic-nebula` | `#6366F1` | Indigo — light-mode cosmic accent |
| `cosmic-silver` | `#E2E8F0` | Light gray |

### Chart Colors (for data visualization)

| Token | Maps to |
|-------|---------|
| `--chart-1` | Primary (amber) |
| `--chart-2` | Blue/indigo |
| `--chart-3` | Purple |
| `--chart-4` | Cyan |
| `--chart-5` | Rose |

---

## 2. Typography

### Font Stack

| Family | Font | Tailwind Class | Usage |
|--------|------|----------------|-------|
| Sans | Manrope | `font-sans` | Body text, UI elements, buttons, nav |
| Serif | Cinzel | `font-serif` | Headings, hero text, titles |
| Mono | JetBrains Mono | `font-mono` | Planetary degrees, coordinates, numbers |

**Import**: Google Fonts loaded in `public/index.html`

### Heading Hierarchy

```css
h1 { text-4xl md:text-5xl lg:text-6xl tracking-normal; }  /* Hero/page titles */
h2 { text-3xl md:text-4xl tracking-normal; }               /* Section headings */
h3 { text-xl md:text-2xl tracking-tight; }                  /* Subsections */
```

**Rule**: H1 and H2 use `tracking-normal` (not tight) because Cinzel at large sizes needs room to breathe.

---

## 3. CSS Classes Reference

### Surfaces

| Class | Purpose | Key Properties |
|-------|---------|----------------|
| `.glass-card` | Primary container | `bg-card/80`, `backdrop-blur(16px)`, `border: 1px solid border/0.5`, `shadow 4px 24px` |
| `.glass-header` | Navigation bar | `bg-background/70`, `backdrop-blur(20px)`, `border-bottom` |
| `.feature-card` | Landing page features | `bg-card/50`, `border border-border/50` |
| `.pricing-popular` | Highlighted pricing tier | `border-primary/50`, enhanced shadow |
| `.testimonial-card` | User testimonials | (extends glass-card) |
| `.transit-card` | Transit display | (extends glass-card) |
| `.friend-preview-card` | Saoul preview card | `border-color: rose-500/20` |

### Buttons

| Class | Purpose | Key Properties |
|-------|---------|----------------|
| `.glow-button` | Primary CTA | `box-shadow: 0 4px 20px primary/0.25` |

**Button variants** (from Shadcn): `default`, `outline`, `ghost`, `secondary`, `destructive`, `link`

### Chat Bubbles

| Class | Purpose | Visual |
|-------|---------|--------|
| `.chat-bubble-user` | User messages | Primary-tinted background |
| `.chat-bubble-assistant` | Coach messages | Neutral/muted background |
| `.chat-bubble-friend` | Saoul messages | Rose-tinted background (`rose-500/8` dark, `rose-500/10` light) |

### Backgrounds

| Class | Purpose | Notes |
|-------|---------|-------|
| `.cosmic-page-bg` | Applied to every inner page | Radial gradients (nebula + gold at low opacity) |
| `.cosmic-gradient` | Hero section overlay | Radial gradient blend |
| `.hero-gradient-light` | Light hero overlay | Gradient from background to transparent |
| `.hero-gradient-dark` | Dark hero overlay | Gradient from background to transparent |
| `.noise-overlay` | Grain texture | SVG noise at 1.5% (light) / 2.5% (dark) opacity, `pointer-events: none` |

### Navigation

| Class | Purpose |
|-------|---------|
| `.sidebar-link` | Dashboard sidebar navigation items |
| `.zodiac-badge` | Tier/zodiac indicator badge |
| `.theme-toggle` | Dark/light mode switch |

### Utilities

| Class | Purpose |
|-------|---------|
| `.fade-in` | Entrance animation (0.6s translateY) |
| `.animate-float` | Floating particle animation (6s loop) |
| `.animate-pulse-glow` | Button glow pulse (3s loop) |
| `.skeleton` | Loading state placeholder |
| `.stat-number` | Stats display styling |
| `.gradient-text` | Gold gradient text effect |
| `.card-lift` | Hover lift effect on cards |
| `.link-hover` | Link hover color transition |

---

## 4. Animations (Tailwind Config)

| Name | Duration | Effect |
|------|----------|--------|
| `accordion-down` | 0.2s | Expand accordion content |
| `accordion-up` | 0.2s | Collapse accordion content |
| `fade-in` | 0.6s | Fade in + slide up 20px |
| `float` | 6s infinite | Gentle vertical float (-10px) |
| `pulse-glow` | 3s infinite | Box-shadow pulse (gold glow) |

---

## 5. Critical Design Rules

These rules come from `design_guidelines.json` and must NEVER be violated:

### ❌ NEVER Do

1. **`transition: all`** — Always specify exact properties (`transition: box-shadow 0.3s ease, transform 0.3s ease`). Universal transitions break transforms and cause layout jank.

2. **Center-aligned App container** — No `.App { text-align: center; }`. This disrupts natural reading flow.

3. **Emoji icons** — No 🔮🌟📅💜📢🎉🤖🧠 etc. Emoji renders differently across OS and is not styleable. Use Lucide React icons instead.

4. **Dark-color gradients** — Dark colors look good independently. Don't use dark-on-dark gradients.

5. **Generic centered layouts** — Create depth through layered z-index hierarchy.

6. **Placeholder images** — Always use provided Unsplash URLs or real content.

### ✅ ALWAYS Do

1. **Glassmorphism** — Use backdrop-filter blur (12-24px) on cards
2. **Generous spacing** — Use 2-3x more spacing than feels comfortable (p-8, p-12, p-24)
3. **Micro-animations** — Every interactive element needs hover states and transitions
4. **Noise overlay** — Subtle grain on all solid backgrounds
5. **Named exports** for components, **default exports** for pages
6. **`data-testid`** on all interactive elements
7. **Sonner** for toasts (component in `/components/ui/sonner.tsx`)

---

## 6. Component Library

**Base**: Shadcn/ui (44 components in `src/components/ui/`)

Key components used across the app:
- `Button` — with variants: default, outline, ghost, secondary
- `Input` — styled with `bg-background/50 border-border rounded-xl`
- `Card` — rarely used directly; `glass-card` CSS class preferred
- `Accordion` — FAQ section
- `Dialog` — modals
- `Tabs` — chart page sections
- `Select` — settings dropdowns
- `Textarea` — contact form

**Utility**: `cn()` from `lib/utils.js` — merges Tailwind classes via `clsx` + `tailwind-merge`

---

## 7. Responsive Breakpoints

Follows Tailwind defaults:
- `sm:` → 640px
- `md:` → 768px (tablet)
- `lg:` → 1024px (desktop)

**Key patterns**:
- Dashboard sidebar: hidden below `lg:`, slides in as drawer on mobile
- Landing page grids: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`
- Hero text: `text-5xl md:text-7xl lg:text-8xl`
- Page padding: `p-4 lg:p-8`

---

## 8. Print Styles

`@media print` is defined in `index.css`:
- Hides non-essential elements (nav, sidebar, buttons)
- Removes backgrounds and shadows
- Forces black text on white
- Used for chart export (ChartPage has "Print / Save as PDF" button)

---

## 9. Accessibility

- `prefers-reduced-motion`: All animations respect this media query
- Custom `::selection` styling with primary color
- Focus rings use `--ring` variable (amber)
- Scrollbar styled for dark theme (webkit)
- `aria-label` on theme toggle buttons

---

## 10. Image Assets

From `design_guidelines.json`:

| Key | URL | Usage |
|-----|-----|-------|
| `hero_background` | Unsplash nebula | Hero section background |
| `auth_background` | Blue nebula | Auth page split-screen |
| `features_chart` | Starfield visualization | Feature section |
| `testimonial_avatar_1` | Mystical avatar | Testimonials |
| `zodiac_icons` | Gold zodiac symbols | Decorative |

**Current hero**: Uses a different Unsplash URL (generic starfield) than the design guidelines recommend (deep space nebula). This is a known gap.

---

*For brand philosophy and voice guidelines, see `BRAND_IDENTITY.md`. For architecture and navigation, see `ARCHITECTURE.md`. For feature inventory, see `PRD.md`.*
