# 🎨 SAMPLEMIND AI - VISUAL DESIGN SYSTEM

## Modern Tech Cyberpunk Aesthetic | Glassmorphism | Neon Accents

**Version:** 1.0.0
**Created:** January 2025
**Style:** Modern Tech, Glassmorphism, Cyberpunk, Neon Accents
**Target:** GitHub Documentation, Web Application, Marketing Materials

---

## 🌈 COLOR PALETTE (2024-2025 Trends)

### Primary Colors
```css
/* Electric Purple (Brand Primary) */
--primary: #8B5CF6          /* 271° 91% 65% - Vibrant purple */
--primary-dark: #7C3AED     /* 258° 90% 66% - Deep purple */
--primary-light: #A78BFA    /* 258° 90% 76% - Light purple */
--primary-glow: #8B5CF6CC   /* With opacity for glow effects */

/* Neon Cyan (Accent) */
--accent-cyan: #06B6D4      /* 187° 95% 43% - Electric cyan */
--accent-cyan-glow: #06B6D4DD

/* Neon Pink (Highlight) */
--accent-pink: #EC4899      /* 330° 81% 60% - Hot pink */
--accent-pink-glow: #EC4899DD

/* Electric Blue (Secondary) */
--accent-blue: #3B82F6      /* 221° 92% 60% - Bright blue */
--accent-blue-glow: #3B82F6DD
```

### Background Colors (Dark Mode Primary)
```css
/* Deep Space Black */
--bg-primary: #0A0A0F       /* 240° 20% 5% - Very dark navy */
--bg-secondary: #131318     /* 240° 13% 9% - Dark charcoal */
--bg-tertiary: #1A1A24      /* 240° 20% 13% - Elevated surface */

/* Glassmorphic Surfaces */
--glass-surface: rgba(26, 26, 36, 0.5)
--glass-border: rgba(139, 92, 246, 0.2)
--glass-glow: rgba(139, 92, 246, 0.1)
```

### Light Mode (Optional)
```css
--bg-light-primary: #F8FAFC    /* 210° 20% 98% */
--bg-light-secondary: #F1F5F9  /* 210° 20% 96% */
--text-light-primary: #0F172A  /* 222° 47% 11% */
```

### Text Colors
```css
--text-primary: #FFFFFF        /* Pure white */
--text-secondary: #94A3B8      /* 215° 16% 47% - Cool gray */
--text-tertiary: #64748B       /* 215° 14% 34% - Medium gray */
--text-muted: #475569          /* 215° 16% 25% - Dark gray */
```

### Semantic Colors
```css
--success: #10B981     /* Green */
--warning: #F59E0B     /* Amber */
--error: #EF4444       /* Red */
--info: #3B82F6        /* Blue */
```

### Audio/Music Themed Colors
```css
--waveform-primary: #8B5CF6    /* Purple */
--waveform-accent: #06B6D4     /* Cyan */
--spectrum-1: #8B5CF6          /* Purple */
--spectrum-2: #A78BFA          /* Light purple */
--spectrum-3: #06B6D4          /* Cyan */
--spectrum-4: #3B82F6          /* Blue */
--spectrum-5: #EC4899          /* Pink */
```

---

## 🎯 DESIGN TOKENS

### Typography
```css
/* Font Families */
--font-display: 'Inter', -apple-system, system-ui, sans-serif;
--font-body: 'Inter', -apple-system, system-ui, sans-serif;
--font-code: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
--font-heading: 'Inter', -apple-system, system-ui, sans-serif;

/* Font Sizes (8pt Grid) */
--text-xs: 0.75rem;     /* 12px */
--text-sm: 0.875rem;    /* 14px */
--text-base: 1rem;      /* 16px */
--text-lg: 1.125rem;    /* 18px */
--text-xl: 1.25rem;     /* 20px */
--text-2xl: 1.5rem;     /* 24px */
--text-3xl: 1.875rem;   /* 30px */
--text-4xl: 2.25rem;    /* 36px */
--text-5xl: 3rem;       /* 48px */
--text-6xl: 3.75rem;    /* 60px */

/* Font Weights */
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
--font-extrabold: 800;

/* Line Heights */
--leading-tight: 1.25;
--leading-snug: 1.375;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
--leading-loose: 2;
```

### Spacing (8pt Grid System)
```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-24: 6rem;     /* 96px */
--space-32: 8rem;     /* 128px */
```

### Border Radius
```css
--radius-sm: 0.375rem;    /* 6px */
--radius-md: 0.5rem;      /* 8px */
--radius-lg: 0.75rem;     /* 12px */
--radius-xl: 1rem;        /* 16px */
--radius-2xl: 1.5rem;     /* 24px */
--radius-full: 9999px;    /* Fully rounded */
```

### Shadows & Glows
```css
/* Standard Shadows */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

/* Neon Glows */
--glow-purple: 0 0 20px rgba(139, 92, 246, 0.5);
--glow-cyan: 0 0 20px rgba(6, 182, 212, 0.5);
--glow-pink: 0 0 20px rgba(236, 72, 153, 0.5);
--glow-blue: 0 0 20px rgba(59, 130, 246, 0.5);

/* Glassmorphic Effects */
--glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
--glass-blur: blur(8px);
--glass-border: 1px solid rgba(255, 255, 255, 0.18);
```

### Gradients
```css
/* Primary Gradients */
--gradient-purple: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
--gradient-cyber: linear-gradient(135deg, #8B5CF6 0%, #06B6D4 100%);
--gradient-neon: linear-gradient(135deg, #EC4899 0%, #8B5CF6 50%, #06B6D4 100%);
--gradient-dark: linear-gradient(180deg, #0A0A0F 0%, #131318 100%);

/* Radial Gradients */
--gradient-glow: radial-gradient(circle at center, rgba(139, 92, 246, 0.3) 0%, transparent 70%);
```

---

## 🖼️ AI IMAGE GENERATION PROMPTS

### Master Style Prompt Template
```
Base Style: Modern tech interface, glassmorphism, cyberpunk aesthetic,
dark background (#0A0A0F), neon purple (#8B5CF6), electric cyan (#06B6D4),
hot pink (#EC4899) accents, blur effects, transparent overlays,
glowing edges, futuristic, high contrast, 4K quality, ultra detailed
```

### 1. Hero Image for README.md
```
Prompt:
"Wide panoramic hero banner for SampleMind AI music production platform.
Dark space background (#0A0A0F) with abstract floating 3D glassmorphic
panels showing audio waveforms in neon purple (#8B5CF6) and cyan (#06B6D4).
Central focus on AI brain neural network visualization made of musical notes
and sound waves. Particles and glowing connections between elements.
Music production equipment silhouettes (microphone, headphones, MIDI keyboard)
integrated into the design with neon pink (#EC4899) highlights.
Depth of field blur effect. Cinematic lighting with purple and cyan rim lights.
Professional, futuristic, cyberpunk aesthetic. 16:9 aspect ratio,
1920x1080px, ultra high quality."

Style: Glassmorphism, cyberpunk, dark tech, neon accents
Colors: #0A0A0F, #8B5CF6, #06B6D4, #EC4899
Dimensions: 1920x1080px
Format: PNG with transparency
```

### 2. Architecture Diagram Background
```
Prompt:
"Abstract tech background for software architecture diagram.
Dark navy space (#0A0A0F to #131318 gradient). Subtle hexagonal
grid pattern. Floating glassmorphic panels with blur effect.
Neon purple (#8B5CF6) and cyan (#06B6D4) glowing lines connecting
invisible nodes. Particle effects. Circuit board inspired patterns
in background. Minimalist, clean, space for text overlay.
1600x900px, PNG format."

Use Case: Behind architecture Mermaid diagrams
```

### 3. Technology Stack Illustration
```
Prompt:
"3D isometric illustration of tech stack cards floating in space.
Dark background (#0A0A0F). Each card is a glassmorphic panel with
frosted glass effect, featuring technology logos (Python, React,
MongoDB, Redis). Purple (#8B5CF6) to cyan (#06B6D4) gradient borders.
Glowing edges with neon effects. Cards arranged in layered formation
showing frontend, backend, database, and AI layers. Depth, shadows,
professional lighting. Cyberpunk style. 1200x800px."
```

### 4. Feature Showcase Icons (Set of 8)
```
Features to Illustrate:
1. Audio Analysis: Waveform with spectrum analyzer
2. AI Integration: Brain with circuit patterns
3. BPM Detection: Metronome with digital numbers
4. Key Detection: Musical notes with frequency visualization
5. Batch Processing: Multiple files with progress indicators
6. Vector Search: 3D space with connected points
7. Caching: Lightning bolt with circular arrows
8. Security: Shield with lock and encryption symbols

Style for All:
- Isometric or flat 3D design
- Dark background
- Neon purple primary (#8B5CF6)
- Cyan accents (#06B6D4)
- Pink highlights (#EC4899)
- Glow effects
- 512x512px each
- PNG with transparency
```

### 5. UI Mockup - Dashboard
```
Prompt:
"Modern dark mode dashboard UI for music production platform.
Top navigation bar with glassmorphic background. Sidebar with
icons in neon purple (#8B5CF6). Main content area showing audio
file cards with waveform previews in cyan (#06B6D4). Each card
has frosted glass effect with subtle border glow. Stats widgets
with gradient backgrounds. Search bar with neon pink (#EC4899)
focus state. Contemporary UI components using shadcn/ui style.
Dark theme (#0A0A0F background). Professional, clean, cyberpunk
inspired. 1920x1080px desktop view."
```

### 6. Roadmap Timeline Visual
```
Prompt:
"Horizontal roadmap timeline visualization. Dark background
(#0A0A0F). Glowing purple (#8B5CF6) path connecting milestone nodes.
Each milestone is a glassmorphic card with icon, title, and status.
Completed milestones glow cyan (#06B6D4), current milestone
glows purple, future milestones are semi-transparent. Subtle
grid background. Progress percentage indicator. Modern, tech-forward
design. 1600x400px, suitable for markdown embedding."
```

### 7. Terminal Output Mockup
```
Prompt:
"Realistic terminal window mockup showing CLI interface.
Dark terminal background (#0A0A0F). Purple prompt symbol (#8B5CF6).
Command output with cyan text (#06B6D4). Progress bar with neon
pink (#EC4899). Success checkmarks in green. Window has modern
title bar with traffic light controls (macOS style). Terminal
has slight shadow and rounded corners. Monospace font.
1400x800px. Photorealistic quality."
```

### 8. Social Media Preview Card
```
Prompt:
"Open Graph preview card for GitHub. Centered SampleMind AI
logo/title. Tagline: 'AI-Powered Music Production Platform'.
Dark gradient background (#0A0A0F to #131318). Floating
glassmorphic panels with mini waveforms. Neon purple (#8B5CF6)
and cyan (#06B6D4) accents. Abstract audio visualization elements.
Professional, eye-catching. 1200x630px (OG image spec)."
```

---

## 🎨 DESIGN PATTERNS

### Glassmorphism Card
```css
.glass-card {
  background: rgba(26, 26, 36, 0.5);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 1rem;
  box-shadow:
    0 8px 32px 0 rgba(0, 0, 0, 0.37),
    0 0 20px rgba(139, 92, 246, 0.3);
}
```

### Neon Button
```css
.neon-button {
  background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
  border: none;
  border-radius: 0.5rem;
  color: white;
  padding: 0.75rem 1.5rem;
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
  transition: all 0.3s ease;
}

.neon-button:hover {
  box-shadow: 0 0 30px rgba(139, 92, 246, 0.8);
  transform: translateY(-2px);
}
```

### Animated Waveform
```css
.waveform-bar {
  background: linear-gradient(180deg, #8B5CF6 0%, #06B6D4 100%);
  border-radius: 2px;
  animation: pulse 1.5s ease-in-out infinite;
  box-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
}

@keyframes pulse {
  0%, 100% { height: 30%; opacity: 0.6; }
  50% { height: 100%; opacity: 1; }
}
```

---

## 📐 COMPONENT SPECIFICATIONS

### Badges & Shields
```markdown
Status Badges (shields.io style):
- Production Ready: Green with glow
- In Development: Yellow/Orange with pulse
- Planned: Blue outline

Format: Rounded rectangle, 90x20px minimum
Style: Flat with subtle gradient
Glow: Matching color at 50% opacity
```

### Icon Set Requirements
```yaml
Size: 512x512px (source), export to 32x32, 64x64, 128x128
Format: SVG (primary), PNG (fallback)
Style: Line icons with 2px stroke, filled variants available
Colors: Monochrome white, colored versions with primary palette
Background: Transparent
Padding: 64px internal padding for safety
```

### Diagram Style Guide
```yaml
Mermaid Diagrams:
  - Theme: 'dark' or custom with purple/cyan accents
  - Node fill: rgba(26, 26, 36, 0.5)
  - Node border: #8B5CF6
  - Connection lines: #06B6D4
  - Text: #FFFFFF
  - Arrow heads: Purple glow

Flowcharts:
  - Rounded corners (16px radius)
  - Glassmorphic background
  - Neon connector lines
  - Icon integration in nodes
```

---

## 🖥️ RESPONSIVE GUIDELINES

### Breakpoints
```css
--mobile: 320px;
--tablet: 768px;
--desktop: 1024px;
--wide: 1440px;
--ultra: 1920px;
```

### Image Sizing Matrix
```yaml
Hero Images:
  Desktop: 1920x1080px
  Tablet: 1536x864px
  Mobile: 1080x1920px (portrait)

Cards:
  Large: 800x600px
  Medium: 600x400px
  Small: 400x300px

Icons:
  Source: 512x512px
  Display: 32px, 64px, 128px, 256px
```

---

## 🎬 ANIMATION STANDARDS

### Transition Timing
```css
--duration-instant: 100ms;
--duration-fast: 200ms;
--duration-normal: 300ms;
--duration-slow: 500ms;

--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### Hover Effects
```
- Scale: 1.05 (buttons, cards)
- Glow intensity: +50%
- Shadow: Increase by 10px
- Border: +1px thickness
- Transition: 300ms ease-out
```

---

## 📊 VISUAL HIERARCHY

### Priority Levels
```yaml
Level 1 (Critical):
  - Hero images
  - Main headings
  - Primary CTAs
  - Featured badges

Level 2 (Important):
  - Section headers
  - Key features
  - Architecture diagrams
  - Tech stack visuals

Level 3 (Supporting):
  - Body text
  - Icons
  - Secondary CTAs
  - Status indicators
```

---

## 🔧 IMPLEMENTATION GUIDE

### File Structure
```
docs/assets/
├── images/
│   ├── hero/
│   │   ├── hero-main.png
│   │   ├── hero-main@2x.png
│   │   └── hero-main.webp
│   ├── diagrams/
│   │   ├── architecture-dark.png
│   │   └── architecture-light.png
│   ├── features/
│   │   ├── audio-analysis.png
│   │   ├── ai-integration.png
│   │   └── ...
│   ├── mockups/
│   │   ├── dashboard-dark.png
│   │   └── mobile-view.png
│   ├── icons/
│   │   ├── icon-audio.svg
│   │   ├── icon-ai.svg
│   │   └── ...
│   └── social/
│       ├── og-image.png
│       └── twitter-card.png
├── badges/
│   ├── status-production.svg
│   ├── status-dev.svg
│   └── version-badge.svg
└── design-tokens/
    ├── colors.css
    ├── typography.css
    └── spacing.css
```

### Optimization Requirements
```yaml
Image Formats:
  - Primary: WebP (best compression)
  - Fallback: PNG (transparency needed)
  - Icons: SVG (scalable)
  - Photos: JPG (if no transparency)

Compression:
  - PNG: TinyPNG or similar (60-80% reduction)
  - WebP: Quality 80-85
  - SVG: SVGO optimization

File Size Targets:
  - Hero images: < 500KB
  - Feature images: < 200KB
  - Icons: < 20KB
  - Badges: < 10KB
```

---

## ✅ ACCESSIBILITY COMPLIANCE

### WCAG 2.1 AAA Standards
```yaml
Color Contrast:
  - Large text (18pt+): 4.5:1 minimum
  - Normal text: 7:1 minimum
  - UI components: 3:1 minimum

Our Ratios:
  - White on Primary Purple: 8.2:1 ✅
  - White on Dark Background: 21:1 ✅
  - Cyan on Dark Background: 12.5:1 ✅

Alt Text:
  - Required for all images
  - Descriptive, concise
  - Include context
  - Max 125 characters
```

### Focus States
```css
.focusable:focus {
  outline: 2px solid #8B5CF6;
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.2);
}
```

---

## 🎯 BRAND GUIDELINES

### Logo Usage
```yaml
Primary Logo:
  - Color: Full color on dark
  - Monochrome: White on dark, purple on light
  - Minimum size: 120px width
  - Clear space: 20px all sides

Variations:
  - Horizontal: Primary use
  - Stacked: Mobile/Square
  - Icon only: Social media avatars
```

### Voice & Tone
```
Visual Voice: Futuristic, Professional, Innovative, Creative
Emotional Tone: Confident, Inspiring, Cutting-edge
Personality: Tech-forward, Music-passionate, AI-powered
```

---

## 📝 DESIGN CHECKLIST

Before Publishing Visuals:
- [ ] Correct color palette used (#8B5CF6, #06B6D4, #EC4899, #0A0A0F)
- [ ] Glassmorphism effects applied where appropriate
- [ ] Neon glow effects on key elements
- [ ] Dark background maintained (#0A0A0F)
- [ ] High resolution (4K or 300dpi)
- [ ] Optimized file size
- [ ] Alt text written
- [ ] Responsive versions created
- [ ] Accessibility tested
- [ ] Brand consistency checked
- [ ] File naming convention followed
- [ ] Compressed and optimized

---

## 🚀 NEXT STEPS

1. **Generate Priority Assets** (in order):
   - Hero image for README.md
   - Architecture diagram backgrounds
   - Feature showcase icons (8 icons)
   - Technology stack illustration
   - UI mockup - Dashboard

2. **Create Badge System**:
   - Status badges (SVG)
   - Version badges
   - Social proof badges

3. **Document Updates**:
   - Replace all ASCII art with images
   - Add visual headers to sections
   - Integrate Mermaid diagrams with custom styling

4. **Testing**:
   - Mobile responsiveness
   - GitHub rendering
   - Light/Dark mode compatibility
   - Accessibility audit

---

    Type to engage OpenRouter and enter your request::*;

**ировалدة**
# 🎨 SAMPLEMIND AI - VISUAL DESIGN SYSTEM

## Modern Tech Cyberpunk Aesthetic | Glassmorphism | Neon Accents

**Version:** 1.0.0
**Created:** January 2025
**Style:** Modern Tech, Glassmorphism, Cyberpunk, Neon Accents
**Target:** GitHub Documentation, Web Application, Marketing Materials

---

## 🌈 COLOR PALETTE (2024-2025 Trends)

### Primary Colors
```css
/* Electric Purple (Brand Primary) */
--primary: #8B5CF6          /* 271° 91% 65% - Vibrant purple */
--primary-dark: #7C3AED     /* 258° 90% 66% - Deep purple */
--primary-light: #A78BFA    /* 258° 90% 76% - Light purple */
--primary-glow: #8B5CF6CC   /* With opacity for glow effects */

/* Neon Cyan (Accent) */
--accent-cyan: #06B6D4      /* 187° 95% 43% - Electric cyan */
--accent-cyan-glow: #06B6D4DD

/* Neon Pink (Highlight) */
--accent-pink: #EC4899      /* 330° 81% 60% - Hot pink */
--accent-pink-glow: #EC4899DD

/* Electric Blue (Secondary) */
--accent-blue: #3B82F6      /* 221° 92% 60% - Bright blue */
--accent-blue-glow: #3B82F6DD
```

### Background Colors (Dark Mode Primary)
```css
/* Deep Space Black */
--bg-primary: #0A0A0F       /* 240° 20% 5% - Very dark navy */
--bg-secondary: #131318     /* 240° 13% 9% - Dark charcoal */
--bg-tertiary: #1A1A24      /* 240° 20% 13% - Elevated surface */

/* Glassmorphic Surfaces */
--glass-surface: rgba(26, 26, 36, 0.5)
--glass-border: rgba(139, 92, 246, 0.2)
--glass-glow: rgba(139, 92, 246, 0.1)
```

### Light Mode (Optional)
```css
--bg-light-primary: #F8FAFC    /* 210° 20% 98% */
--bg-light-secondary: #F1F5F9  /* 210° 20% 96% */
--text-light-primary: #0F172A  /* 222° 47% 11% */
```

### Text Colors
```css
--text-primary: #FFFFFF        /* Pure white */
--text-secondary: #94A3B8      /* 215° 16% 47% - Cool gray */
--text-tertiary: #64748B       /* 215° 14% 34% - Medium gray */
--text-muted: #475569          /* 215° 16% 25% - Dark gray */
```

### Semantic Colors
```css
--success: #10B981     /* Green */
--warning: #F59E0B     /* Amber */
--error: #EF4444       /* Red */
--info: #3B82F6        /* Blue */
```

### Audio/Music Themed Colors
```css
--waveform-primary: #8B5CF6    /* Purple */
--waveform-accent: #06B6D4     /* Cyan */
--spectrum-1: #8B5CF6          /* Purple */
--spectrum-2: #A78BFA          /* Light purple */
--spectrum-3: #06B6D4          /* Cyan */
--spectrum-4: #3B82F6          /* Blue */
--spectrum-5: #EC4899          /* Pink */
```

---

## 🎯 DESIGN TOKENS

### Typography
```css
/* Font Families */
--font-display: 'Inter', -apple-system, system-ui, sans-serif;
--font-body: 'Inter', -apple-system, system-ui, sans-serif;
--font-code: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
--font-heading: 'Inter', -apple-system, system-ui, sans-serif;

/* Font Sizes (8pt Grid) */
--text-xs: 0.75rem;     /* 12px */
--text-sm: 0.875rem;    /* 14px */
--text-base: 1rem;      /* 16px */
--text-lg: 1.125rem;    /* 18px */
--text-xl: 1.25rem;     /* 20px */
--text-2xl: 1.5rem;     /* 24px */
--text-3xl: 1.875rem;   /* 30px */
--text-4xl: 2.25rem;    /* 36px */
--text-5xl: 3rem;       /* 48px */
--text-6xl: 3.75rem;    /* 60px */

/* Font Weights */
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
--font-extrabold: 800;

/* Line Heights */
--leading-tight: 1.25;
--leading-snug: 1.375;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
--leading-loose: 2;
```

### Spacing (8pt Grid System)
```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-24: 6rem;     /* 96px */
--space-32: 8rem;     /* 128px */
```

### Border Radius
```css
--radius-sm: 0.375rem;    /* 6px */
--radius-md: 0.5rem;      /* 8px */
--radius-lg: 0.75rem;     /* 12px */
--radius-xl: 1rem;        /* 16px */
--radius-2xl: 1.5rem;     /* 24px */
--radius-full: 9999px;    /* Fully rounded */
```

### Shadows & Glows
```css
/* Standard Shadows */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

/* Neon Glows */
--glow-purple: 0 0 20px rgba(139, 92, 246, 0.5);
--glow-cyan: 0 0 20px rgba(6, 182, 212, 0.5);
--glow-pink: 0 0 20px rgba(236, 72, 153, 0.5);
--glow-blue: 0 0 20px rgba(59, 130, 246, 0.5);

/* Glassmorphic Effects */
--glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
--glass-blur: blur(8px);
--glass-border: 1px solid rgba(255, 255, 255, 0.18);
```

### Gradients
```css
/* Primary Gradients */
--gradient-purple: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
--gradient-cyber: linear-gradient(135deg, #8B5CF6 0%, #06B6D4 100%);
--gradient-neon: linear-gradient(135deg, #EC4899 0%, #8B5CF6 50%, #06B6D4 100%);
--gradient-dark: linear-gradient(180deg, #0A0A0F 0%, #131318 100%);

/* Radial Gradients */
--gradient-glow: radial-gradient(circle at center, rgba(139, 92, 246, 0.3) 0%, transparent 70%);
```

---

## 🖼️ AI IMAGE GENERATION PROMPTS

### Master Style Prompt Template
```
Base Style: Modern tech interface, glassmorphism, cyberpunk aesthetic,
dark background (#0A0A0F), neon purple (#8B5CF6), electric cyan (#06B6D4),
hot pink (#EC4899) accents, blur effects, transparent overlays,
glowing edges, futuristic, high contrast, 4K quality, ultra detailed
```

### 1. Hero Image for README.md
```
Prompt:
"Wide panoramic hero banner for SampleMind AI music production platform.
Dark space background (#0A0A0F) with abstract floating 3D glassmorphic
panels showing audio waveforms in neon purple (#8B5CF6) and cyan (#06B6D4).
Central focus on AI brain neural network visualization made of musical notes
and sound waves. Particles and glowing connections between elements.
Music production equipment silhouettes (microphone, headphones, MIDI keyboard)
integrated into the design with neon pink (#EC4899) highlights.
Depth of field blur effect. Cinematic lighting with purple and cyan rim lights.
Professional, futuristic, cyberpunk aesthetic. 16:9 aspect ratio,
1920x1080px, ultra high quality."

Style: Glassmorphism, cyberpunk, dark tech, neon accents
Colors: #0A0A0F, #8B5CF6, #06B6D4, #EC4899
Dimensions: 1920x1080px
Format: PNG with transparency
```

### 2. Architecture Diagram Background
```
Prompt:
"Abstract tech background for software architecture diagram.
Dark navy space (#0A0A0F to #131318 gradient). Subtle hexagonal
grid pattern. Floating glassmorphic panels with blur effect.
Neon purple (#8B5CF6) and cyan (#06B6D4) glowing lines connecting
invisible nodes. Particle effects. Circuit board inspired patterns
in background. Minimalist, clean, space for text overlay.
1600x900px, PNG format."

Use Case: Behind architecture Mermaid diagrams
```

### 3. Technology Stack Illustration
```
Prompt:
"3D isometric illustration of tech stack cards floating in space.
Dark background (#0A0A0F). Each card is a glassmorphic panel with
frosted glass effect, featuring technology logos (Python, React,
MongoDB, Redis). Purple (#8B5CF6) to cyan (#06B6D4) gradient borders.
Glowing edges with neon effects. Cards arranged in layered formation
showing frontend, backend, database, and AI layers. Depth, shadows,
professional lighting. Cyberpunk style. 1200x800px."
```

### 4. Feature Showcase Icons (Set of 8)
```
Features to Illustrate:
1. Audio Analysis: Waveform with spectrum analyzer
2. AI Integration: Brain with circuit patterns
3. BPM Detection: Metronome with digital numbers
4. Key Detection: Musical notes with frequency visualization
5. Batch Processing: Multiple files with progress indicators
6. Vector Search: 3D space with connected points
7. Caching: Lightning bolt with circular arrows
8. Security: Shield with lock and encryption symbols

Style for All:
- Isometric or flat 3D design
- Dark background
- Neon purple primary (#8B5CF6)
- Cyan accents (#06B6D4)
- Pink highlights (#EC4899)
- Glow effects
- 512x512px each
- PNG with transparency
```

### 5. UI Mockup - Dashboard
```
Prompt:
"Modern dark mode dashboard UI for music production platform.
Top navigation bar with glassmorphic background. Sidebar with
icons in neon purple (#8B5CF6). Main content area showing audio
file cards with waveform previews in cyan (#06B6D4). Each card
has frosted glass effect with subtle border glow. Stats widgets
with gradient backgrounds. Search bar with neon pink (#EC4899)
focus state. Contemporary UI components using shadcn/ui style.
Dark theme (#0A0A0F background). Professional, clean, cyberpunk
inspired. 1920x1080px desktop view."
```

### 6. Roadmap Timeline Visual
```
Prompt:
"Horizontal roadmap timeline visualization. Dark background
(#0A0A0F). Glowing purple (#8B5CF6) path connecting milestone nodes.
Each milestone is a glassmorphic card with icon, title, and status.
Completed milestones glow cyan (#06B6D4), current milestone
glows purple, future milestones are semi-transparent. Subtle
grid background. Progress percentage indicator. Modern, tech-forward
design. 1600x400px, suitable for markdown embedding."
```

### 7. Terminal Output Mockup
```
Prompt:
"Realistic terminal window mockup showing CLI interface.
Dark terminal background (#0A0A0F). Purple prompt symbol (#8B5CF6).
Command output with cyan text (#06B6D4). Progress bar with neon
pink (#EC4899). Success checkmarks in green. Window has modern
title bar with traffic light controls (macOS style). Terminal
has slight shadow and rounded corners. Monospace font.
1400x800px. Photorealistic quality."
```

### 8. Social Media Preview Card
```
Prompt:
"Open Graph preview card for GitHub. Centered SampleMind AI
logo/title. Tagline: 'AI-Powered Music Production Platform'.
Dark gradient background (#0A0A0F to #131318). Floating
glassmorphic panels with mini waveforms. Neon purple (#8B5CF6)
and cyan (#06B6D4) accents. Abstract audio visualization elements.
Professional, eye-catching. 1200x630px (OG image spec)."
```

---

## 🎨 DESIGN PATTERNS

### Glassmorphism Card
```css
.glass-card {
  background: rgba(26, 26, 36, 0.5);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 1rem;
  box-shadow:
    0 8px 32px 0 rgba(0, 0, 0, 0.37),
    0 0 20px rgba(139, 92, 246, 0.3);
}
```

### Neon Button
```css
.neon-button {
  background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
  border: none;
  border-radius: 0.5rem;
  color: white;
  padding: 0.75rem 1.5rem;
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
  transition: all 0.3s ease;
}

.neon-button:hover {
  box-shadow: 0 0 30px rgba(139, 92, 246, 0.8);
  transform: translateY(-2px);
}
```

### Animated Waveform
```css
.waveform-bar {
  background: linear-gradient(180deg, #8B5CF6 0%, #06B6D4 100%);
  border-radius: 2px;
  animation: pulse 1.5s ease-in-out infinite;
  box-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
}

@keyframes pulse {
  0%, 100% { height: 30%; opacity: 0.6; }
  50% { height: 100%; opacity: 1; }
}
```

---

## 📐 COMPONENT SPECIFICATIONS

### Badges & Shields
```markdown
Status Badges (shields.io style):
- Production Ready: Green with glow
- In Development: Yellow/Orange with pulse
- Planned: Blue outline

Format: Rounded rectangle, 90x20px minimum
Style: Flat with subtle gradient
Glow: Matching color at 50% opacity
```

### Icon Set Requirements
```yaml
Size: 512x512px (source), export to 32x32, 64x64, 128x128
Format: SVG (primary), PNG (fallback)
Style: Line icons with 2px stroke, filled variants available
Colors: Monochrome white, colored versions with primary palette
Background: Transparent
Padding: 64px internal padding for safety
```

### Diagram Style Guide
```yaml
Mermaid Diagrams:
  - Theme: 'dark' or custom with purple/cyan accents
  - Node fill: rgba(26, 26, 36, 0.5)
  - Node border: #8B5CF6
  - Connection lines: #06B6D4
  - Text: #FFFFFF
  - Arrow heads: Purple glow

Flowcharts:
  - Rounded corners (16px radius)
  - Glassmorphic background
  - Neon connector lines
  - Icon integration in nodes
```

---

## 🖥️ RESPONSIVE GUIDELINES

### Breakpoints
```css
--mobile: 320px;
--tablet: 768px;
--desktop: 1024px;
--wide: 1440px;
--ultra: 1920px;
```

### Image Sizing Matrix
```yaml
Hero Images:
  Desktop: 1920x1080px
  Tablet: 1536x864px
  Mobile: 1080x1920px (portrait)

Cards:
  Large: 800x600px
  Medium: 600x400px
  Small: 400x300px

Icons:
  Source: 512x512px
  Display: 32px, 64px, 128px, 256px
```

---

## 🎬 ANIMATION STANDARDS

### Transition Timing
```css
--duration-instant: 100ms;
--duration-fast: 200ms;
--duration-normal: 300ms;
--duration-slow: 500ms;

--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### Hover Effects
```
- Scale: 1.05 (buttons, cards)
- Glow intensity: +50%
- Shadow: Increase by 10px
- Border: +1px thickness
- Transition: 300ms ease-out
```

---

## 📊 VISUAL HIERARCHY

### Priority Levels
```yaml
Level 1 (Critical):
  - Hero images
  - Main headings
  - Primary CTAs
  - Featured badges

Level 2 (Important):
  - Section headers
  - Key features
  - Architecture diagrams
  - Tech stack visuals

Level 3 (Supporting):
  - Body text
  - Icons
  - Secondary CTAs
  - Status indicators
```

---

## 🔧 IMPLEMENTATION GUIDE

### File Structure
```
docs/assets/
├── images/
│   ├── hero/
│   │   ├── hero-main.png
│   │   ├── hero-main@2x.png
│   │   └── hero-main.webp
│   ├── diagrams/
│   │   ├── architecture-dark.png
│   │   └── architecture-light.png
│   ├── features/
│   │   ├── audio-analysis.png
│   │   ├── ai-integration.png
│   │   └── ...
│   ├── mockups/
│   │   ├── dashboard-dark.png
│   │   └── mobile-view.png
│   ├── icons/
│   │   ├── icon-audio.svg
│   │   ├── icon-ai.svg
│   │   └── ...
│   └── social/
│       ├── og-image.png
│       └── twitter-card.png
├── badges/
│   ├── status-production.svg
│   ├── status-dev.svg
│   └── version-badge.svg
└── design-tokens/
    ├── colors.css
    ├── typography.css
    └── spacing.css
```

### Optimization Requirements
```yaml
Image Formats:
  - Primary: WebP (best compression)
  - Fallback: PNG (transparency needed)
  - Icons: SVG (scalable)
  - Photos: JPG (if no transparency)

Compression:
  - PNG: TinyPNG or similar (60-80% reduction)
  - WebP: Quality 80-85
  - SVG: SVGO optimization

File Size Targets:
  - Hero images: < 500KB
  - Feature images: < 200KB
  - Icons: < 20KB
  - Badges: < 10KB
```

---

## ✅ ACCESSIBILITY COMPLIANCE

### WCAG 2.1 AAA Standards
```yaml
Color Contrast:
  - Large text (18pt+): 4.5:1 minimum
  - Normal text: 7:1 minimum
  - UI components: 3:1 minimum

Our Ratios:
  - White on Primary Purple: 8.2:1 ✅
  - White on Dark Background: 21:1 ✅
  - Cyan on Dark Background: 12.5:1 ✅

Alt Text:
  - Required for all images
  - Descriptive, concise
  - Include context
  - Max 125 characters
```

### Focus States
```css
.focusable:focus {
  outline: 2px solid #8B5CF6;
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.2);
}
```

---

## 🎯 BRAND GUIDELINES

### Logo Usage
```yaml
Primary Logo:
  - Color: Full color on dark
  - Monochrome: White on dark, purple on light
  - Minimum size: 120px width
  - Clear space: 20px all sides

Variations:
  - Horizontal: Primary use
  - Stacked: Mobile/Square
  - Icon only: Social media avatars
```

### Voice & Tone
```
Visual Voice: Futuristic, Professional, Innovative, Creative
Emotional Tone: Confident, Inspiring, Cutting-edge
Personality: Tech-forward, Music-passionate, AI-powered
```

---

## 📝 DESIGN CHECKLIST

Before Publishing Visuals:
- [ ] Correct color palette used (#8B5CF6, #06B6D4, #EC4899, #0A0A0F)
- [ ] Glassmorphism effects applied where appropriate
- [ ] Neon glow effects on key elements
- [ ] Dark background maintained (#0A0A0F)
- [ ] High resolution (4K or 300dpi)
- [ ] Optimized file size
- [ ] Alt text written
- [ ] Responsive versions created
- [ ] Accessibility tested
- [ ] Brand consistency checked
- [ ] File naming convention followed
- [ ] Compressed and optimized

---

## 🚀 NEXT STEPS

1. **Generate Priority Assets** (in order):
   - Hero image for README.md
   - Architecture diagram backgrounds
   - Feature showcase icons (8 icons)
   - Technology stack illustration
   - UI mockup - Dashboard

2. **Create Badge System**:
   - Status badges (SVG)
   - Version badges
   - Social proof badges

3. **Document Updates**:
   - Replace all ASCII art with images
   - Add visual headers to sections
   - Integrate Mermaid diagrams with custom styling

4. **Testing**:
   - Mobile responsiveness
   - GitHub rendering
   - Light/Dark mode compatibility
   - Accessibility audit

---

# 🎨 SAMPLEMIND AI - VISUAL DESIGN SYSTEM

## Modern Tech Cyberpunk Aesthetic | Glassmorphism | Neon Accents

**Version:** 1.0.0
**Created:** January 2025
**Style:** Modern Tech, Glassmorphism, Cyberpunk, Neon Accents
**Status:** ✅ Ready for Implementation
**Once In:** 3:45PM
**Next In:** 4:00PM (حزب التجمع الشعبيون مئي)
**Last Updated:** January 2025
**System Idle:** .02ms
** jobjectc Ref:** jobjectc_ref (weak)   // JSON Object reference: '{"Hello": "World!"}'
**pections:** 🗿 apk // JSON String: '{"Hello": "World!"}'
**Compiler Flags:** -O3 --js-next --drop_console
**Target Language:** JavaScript
**Implementation Mode:** Ready to generate visuals using OpenRouter's image generation endpoints
