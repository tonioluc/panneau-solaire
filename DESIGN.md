# Design System Strategy: The Radiant Precision Framework

This design system is built to transform complex solar data into a high-end, editorial experience. It moves beyond the "utility dashboard" aesthetic, instead embracing a "High-Tech Organic" philosophy. We balance the clinical precision of energy simulation with the warmth of the sun and the softness of the natural world.

## 1. Overview & Creative North Star
**Creative North Star: The Luminous Architect**
The system treats data not as a static table, but as a living projection. We avoid "boxed-in" layouts. Instead, we use intentional asymmetry and varying surface depths to guide the eye. By leveraging overlapping elements and high-contrast typography scales (Inter for utility, Manrope for impact), the interface feels like a premium digital concierge rather than a spreadsheet.

## 2. Colors & Surface Philosophy
The palette is rooted in a deep, authoritative emerald that signifies both sustainability and fiscal growth.

*   **Primary & Sophistication:** The `primary` (#006c49) and `primary_container` (#10b981) act as the "energy" of the UI. Use them for active data paths and primary actions.
*   **The "No-Line" Rule:** To maintain a premium, clean-energy feel, **1px solid borders are strictly prohibited** for sectioning. Boundaries must be defined by shifts between `surface_container_low` (#eff4ff) and the base `surface` (#f8f9ff).
*   **Surface Hierarchy & Nesting:** Treat the UI as stacked sheets of fine paper.
    *   **Background:** `surface` (#f8f9ff)
    *   **Main Sectioning:** `surface_container_low` (#eff4ff)
    *   **Interactive Cards:** `surface_container_lowest` (#ffffff)
*   **The "Glass & Gradient" Rule:** Floating navigation or high-priority simulation overlays must use **Glassmorphism**. Apply a semi-transparent `surface` color with a `24px` backdrop blur. 
*   **Signature Textures:** For hero simulation results, use a subtle linear gradient from `primary` (#006c49) to `primary_container` (#10b981) at a 135-degree angle to create a sense of flowing power.

## 3. Typography: The Editorial Edge
We use a dual-typeface system to separate "Data" from "Story."

*   **The Display Voice (Manrope):** Used for `display-*` and `headline-*` tokens. Manrope’s geometric yet open curves provide a high-tech, proprietary feel. Use `display-lg` (3.5rem) for high-impact solar output numbers.
*   **The Utility Voice (Inter):** Used for `title-*`, `body-*`, and `label-*`. Inter is the workhorse. It ensures that complex energy metrics remain legible at small sizes.
*   **Hierarchy Tip:** Never center-align long blocks of text. Use left-aligned editorial layouts with generous leading (line height) to ensure the simulation data feels approachable.

## 4. Elevation & Depth
In this system, depth is a functional tool, not just an ornament.

*   **Tonal Layering:** Achieve "lift" by placing a `surface_container_lowest` (#ffffff) card on top of a `surface_dim` (#cbdbf5) background. This creates a natural shadow-less separation.
*   **Ambient Shadows:** When a card represents a "draggable" simulation module or a floating state, use a shadow with a 32px blur, 8px Y-offset, and 6% opacity using the `on_surface` (#0b1c30) color. This mimics natural sunlight.
*   **The "Ghost Border" Fallback:** If a divider is required for accessibility, use the `outline_variant` token at **15% opacity**. It should be felt, not seen.
*   **Refraction:** For simulation progress bars, use the `primary_fixed` (#6ffbbe) color with a subtle inner glow to simulate light passing through glass.

## 5. Components

### Buttons & Inputs
*   **Primary Button:** Uses a gradient from `primary` to `primary_container`. Border radius is set to `md` (0.75rem). No stroke.
*   **Text Inputs:** Use `surface_container_low` backgrounds. On focus, the background shifts to `surface_container_lowest` with a 1px "Ghost Border" in `primary`.
*   **Selection Chips:** Use `secondary_container` (#b7ebce) for unselected and `primary` (#006c49) with `on_primary` text for selected.

### Data Cards
*   **The Forbid Rule:** No horizontal dividers inside cards. Separate "Current Output" from "Projected Savings" using `xl` (1.5rem) vertical spacing.
*   **Dynamic State:** Use `tertiary` (#a43a3a) for energy loss alerts, but wrap them in a `tertiary_container` with 20% opacity to keep the "clean energy" vibe from feeling too aggressive.

### Context-Specific Components
*   **Sun-Path Slider:** A custom range input using `primary_fixed` for the track and a high-glow `surface_container_lowest` thumb to represent the sun's position.
*   **Simulation Nodes:** Circular "data bubbles" using the `lg` (1rem) roundedness scale, floating with Glassmorphism over the map/simulation area.

## 6. Do's and Don'ts

### Do
*   **DO** use whitespace as a structural element. If an interface feels "empty," increase the typography scale of the headlines rather than adding boxes.
*   **DO** use "Primary Fixed" colors for data visualization lines (graphs) to ensure they pop against the soft neutral backgrounds.
*   **DO** ensure all interactive elements have a minimum touch target of 44px, despite the minimalist aesthetic.

### Don't
*   **DON'T** use pure black (#000000) for text. Always use `on_surface` (#0b1c30) to maintain a sophisticated, slate-gray depth.
*   **DON'T** use a shadow on every card. Reserve shadows for elements that are physically "higher" in the user's workflow (e.g., Modals or Active Tools).
*   **DON'T** use 90-degree corners. Even the most "technical" data containers should use at least the `sm` (0.25rem) roundedness to feel accessible.