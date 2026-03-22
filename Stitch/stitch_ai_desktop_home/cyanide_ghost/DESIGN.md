# Cyanide Ghost Design System

### 1. Overview & Creative North Star
**Creative North Star: "The Neon Neuralist"**
Cyanide Ghost is a design system that visualizes the intersection of high-frequency computation and human-centric clarity. It moves away from the "static app" feel into an immersive OS-like environment. The system prioritizes **Atmospheric Immersion** over traditional UI structures. By leveraging deep blacks, electric cyan accents, and glassmorphic layers, it creates a sense of infinite depth—as if the interface is floating within a dark, data-rich void.

The layout is intentionally airy, using wide margins and large-scale central visualizations to anchor the user experience, while secondary information orbits the periphery in translucent modules.

### 2. Colors
The palette is rooted in a "Void Black" foundation with a single, high-intensity "Cyanide" primary color.

*   **Primary (#0df2f2):** Used sparingly for interactive nodes, critical status indicators, and energetic highlights.
*   **The "No-Line" Rule:** Division of content must never rely on 1px solid high-contrast borders. Instead, sections are defined by `surface-container` background shifts (e.g., `rgba(255,255,255,0.05)`) or subtle backdrop blurs (`backdrop-blur-md`).
*   **Surface Hierarchy:** Layers are "stacked" using increasing opacities of white-on-black. The base is `background-dark`, while floating widgets use `surface-container` with a glass effect.
*   **Signature Textures:** Use a central "Ambient Glow" (a large, blurred radial gradient of 10% opacity primary color) to provide a soft light source behind the main content.

### 3. Typography
Cyanide Ghost utilizes **Inter** across all levels to maintain a technical, clean, and highly readable aesthetic. 

**Typography Scale (Calibrated to Source):**
-   **Display (Headline 1):** `3.75rem` (60px) - Light weight, wide tracking, uppercase for hero states.
-   **System Headlines:** `2.25rem` (36px) / `1.875rem` (30px) - Bold for critical data points.
-   **Titles:** `1.125rem` (18px) / `1.25rem` (20px) - Medium weight for card headers.
-   **Body:** `0.875rem` (14px) - Regular weight for primary reading.
-   **Labels/Metadata:** `10px` / `0.75rem` (12px) - Uppercase with `0.1em` tracking for a "technical readout" feel.

The typographic rhythm relies on high contrast between massive, light-weight display text and tiny, bold, tracked-out metadata.

### 4. Elevation & Depth
Depth is achieved through light simulation rather than physical drop shadows.

*   **The Layering Principle:** Use `white/5` (surface_container) for background elements and `white/10` for active or hovered states.
*   **Ambient Shadows:** Traditional shadows are replaced by "Glows". For example, the `shadow-2xl` value is applied to the bottom dock to lift it off the background, but active nodes use `0 0 10px #0df2f2` to simulate emission.
*   **Glassmorphism:** All containers must feature `backdrop-blur-md` or `backdrop-blur-xl`. This ensures that the "Ambient Glow" of the background filters through the UI, creating a cohesive environment.

### 5. Components
*   **Buttons:** Primary buttons are solid `primary` with `on_primary` text. Secondary buttons are "Ghost" style: `white/5` background with a `white/10` border.
*   **Progress Bars:** Ultra-thin (`1.5rem` or 6px) tracks with high-saturation primary fills.
*   **The Bottom Dock:** A signature floating component using `white/5` background and `backdrop-blur-2xl`. Icons are placed in `12x12` (rem equivalent) rounded-xl containers.
*   **Neural Nodes:** Use `animate-pulse` and `animate-spin` on circular elements to represent active processing states.
*   **Search:** Integrated into the header with a low-opacity container, expanding or highlighting the border color on focus.

### 6. Do's and Don'ts
*   **Do:** Use uppercase and letter-spacing for labels to evoke a command-line/terminal aesthetic.
*   **Do:** Use gradients for "Neural Load" indicators to show fluid data movement.
*   **Don't:** Use solid, opaque backgrounds for cards; always maintain at least 5-10% transparency.
*   **Don't:** Use sharp 90-degree corners. Maintain a consistent `rounded-lg` (0.5rem) to `rounded-xl` (0.75rem) radius to soften the technical edge.
*   **Do:** Ensure high contrast for data—white text on dark backgrounds is the standard, with Cyan reserved for *actionable* or *live* data.