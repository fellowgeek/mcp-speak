---
name: MCP Speak
description: Retro-futuristic neural audio synthesizer interface and Model Context Protocol voice bridge for macOS AI agents.
colors:
  primary: "#ffb000"
  primary-bright: "#ffd000"
  primary-dim: "#996a00"
  primary-shade: "#cc8800"
  primary-deep: "#664400"
  secondary: "#00e5ff"
  accent-green: "#00ff66"
  accent-red: "#ef4444"
  bg-void: "#090a0f"
  bg-chassis: "#10121a"
  bg-panel: "#161924"
  bg-bezel: "#1c2030"
  chassis-screw-bg: "#202430"
  chassis-screw-border: "#363d50"
  chassis-screw-slot: "#475169"
  btn-mechanical-border: "#3d465f"
  btn-mechanical-top: "#242938"
  btn-mechanical-bottom: "#151822"
  border-chassis: "#252b3d"
  border-highlight: "rgba(255, 176, 0, 0.35)"
  text-main: "#f3f4f6"
  text-dim: "#94a3b8"
  text-sub: "#64748b"
  light-bg-void: "#f8fafc"
  light-bg-chassis: "#f1f5f9"
  light-bg-panel: "#ffffff"
  light-bg-bezel: "#e2e8f0"
  light-border-chassis: "#cbd5e1"
  light-amber-primary: "#f59e0b"
  light-amber-dim: "#d97706"
  light-amber-text: "#b45309"
  light-amber-deep: "#92400e"
  light-amber-subtle: "#fef3c7"
  light-amber-lightest: "#fffbeb"
  light-amber-hover: "#fde68a"
  light-cyan-accent: "#0284c7"
  light-green-phosphor: "#059669"
  light-text-main: "#0f172a"
  light-text-dim: "#475569"
  light-text-sub: "#64748b"
  light-chassis-screw: "#cbd5e1"
  light-screw-slot: "#64748b"
  light-btn-top: "#ffffff"
  light-btn-bottom: "#e2e8f0"
  light-btn-border-bottom: "#94a3b8"
  light-btn-amber-top: "#fbbf24"
  light-btn-amber-bottom: "#f59e0b"
  light-btn-amber-border: "#fcd34d"
  light-btn-amber-border-bottom: "#d97706"
typography:
  display:
    fontFamily: "Chakra Petch, sans-serif"
    fontSize: "clamp(2rem, 5vw, 3.75rem)"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Chakra Petch, sans-serif"
    fontSize: "1.875rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.02em"
  body:
    fontFamily: "Rajdhani, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 500
    lineHeight: 1.5
    letterSpacing: "0.01em"
  mono:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: "0.8125rem"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "0.02em"
  telemetry-sm:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: "11px"
    fontWeight: 500
  telemetry-xs:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: "10px"
    fontWeight: 500
  telemetry-badge:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: "9px"
    fontWeight: 500
  telemetry-micro:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: "8px"
    fontWeight: 500
rounded:
  sm: "2px"
  md: "4px"
  lg: "8px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  xxl: "48px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.bg-void}"
    typography: "{typography.display}"
    rounded: "{rounded.md}"
    padding: "14px 24px"
  button-mechanical:
    backgroundColor: "{colors.bg-panel}"
    textColor: "{colors.text-main}"
    typography: "{typography.display}"
    rounded: "{rounded.md}"
    padding: "8px 16px"
  cartridge-card:
    backgroundColor: "{colors.bg-panel}"
    textColor: "{colors.text-main}"
    rounded: "{rounded.md}"
    padding: "16px"
---

# Design System: MCP Speak

## Overview

**Creative North Star: "The Neural Synthesizer Mainframe"**

MCP Speak pairs an authentic, tactile cassette-futuristic audio engineering console aesthetic with dual-mode lighting environments: a high-contrast darkroom console mode (default) and a crisp laboratory instrument mode (light). Inspired by 1980s mainframe terminals, aerospace telemetry racks, and analog modular synthesizers (such as Moog and Braun audio instrumentation), the design language combines brushed industrial chassis panels, amber/green phosphor CRT screens, tactile mechanical buttons, full-color persona modules, and real-time canvas oscilloscope waveforms.

## Colors

The system supports dual telemetry palettes:

### Dark Mode (Console Environment)
- **Primary Amber (`#ffb000` / `#ffd000`):** Active signal and command triggers.
- **Chassis Void (`#090a0f` / `#10121a`):** Non-reflective base materials.
- **Panel & Bezel Neutrals (`#161924`, `#1c2030`, `#252b3d`):** Brushed metallic module boundaries.
- **Phosphor Green (`#00ff66`):** Hardware nominal indicator.
- **Cyan Accent (`#00e5ff`):** Secondary telemetry markers.

### Light Mode (Laboratory Instrumentation)
- **Primary Amber (`#f59e0b` / `#fbbf24`):** Vibrant golden amber with crisp high-contrast text tones (`#d97706`, `#b45309`).
- **Chassis Void (`#f8fafc` / `#f1f5f9`):** Clean cool anodized aluminum laboratory surface.
- **Panel Face (`#ffffff`, `#e2e8f0`):** Pure white component modules with soft slate borders (`#cbd5e1`).
- **Phosphor Green (`#059669`):** Deep emerald nominal indicator.
- **Cyan Accent (`#0284c7`):** Engineering cyan data markers.
- **Avatar Pods & Terminal Screens:** Clean laboratory white and light-slate surfaces eliminating harsh pitch-black backgrounds.

## Typography

- **Display & Section Headers:** `Chakra Petch` (700/600 weight, uppercase, tracking-tight).
- **Body Text:** `Rajdhani` (500/600 weight, 18px base).
- **Telemetry & Code:** `JetBrains Mono` (400/500 weight).

## Components

- **Theme Toggle (`#theme-toggle`):** Mechanical button with dynamic sun/moon icons persisting preference to `localStorage`.
- **Persona Cartridges (`.cartridge`):** Full-color persona avatars housed within soft-lit circular bezels with active status LEDs and direct audio preview triggers.
- **Live Oscilloscope Canvas (`#oscilloscope-canvas`):** HTML5 Canvas simulating real-time dual-harmonic sine synthesis, adjusting stroke contrast automatically per active theme.
