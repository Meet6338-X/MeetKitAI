---
name: flutter-ui-ux
description: Expert Flutter UI/UX design patterns, animations, and responsive layouts.
---

# Flutter UI/UX Mastery

> **Goal**: Create stunning, smooth, and responsive Flutter applications that feel premium.

## 1. Core Principles

- **60fps is Non-Negotiable**: Avoid jank at all costs. Use `RepaintBoundary` for complex static subtrees.
- **Pixel Perfection**: Match design specs exactly.
- **Micro-Interactions**: Every tap should have feedback. Use `InkWell`, `AnimatedContainer`, or custom animations.
- **Adaptive Design**: UI must scale from narrow phones to wide desktop screens.

## 2. Animation Patterns

### Implicit Animations (The "Easy" Wins)
Use these for simple state changes (hover, expand, color change).
- `AnimatedContainer`, `AnimatedOpacity`, `AnimatedPadding`, `AnimatedSwitcher`.

```dart
AnimatedContainer(
  duration: Duration(milliseconds: 300),
  curve: Curves.easeInOut,
  height: _isExpanded ? 200 : 0,
  child: Content(),
)
```

### Explicit Animations (Complex Choreography)
Use `AnimationController` for repeatable, pausable, or multi-stage animations.
- **Staggered Animations**: Use `Interval` in your Curves to sequence animations.
- **Rive / Lottie**: Use for complex vector animations (onboarding, success states).

### Hero Animations
Always use `Hero` tags for navigation transitions between lists and details.

## 3. Responsive & Adaptive Layout

### Breakpoints
Don't check `Platform.isAndroid`. Check screen size.

```dart
bool isMobile(BuildContext context) => MediaQuery.of(context).size.width < 600;
bool isTablet(BuildContext context) => MediaQuery.of(context).size.width >= 600 && MediaQuery.of(context).size.width < 1200;
bool isDesktop(BuildContext context) => MediaQuery.of(context).size.width >= 1200;
```

### Flexible Widgets
- Use `Flex`, `Expanded`, and `Flexible` correctly.
- Use `LayoutBuilder` to make decisions based on parent constraints.
- Use `Wrap` for flow layouts that handle overflow gracefully.

## 4. Theming & Styling (Material 3)

### Color Extensions
Don't hardcode colors. Extend `ThemeData`.

```dart
@immutable
class MyColors extends ThemeExtension<MyColors> {
  final Color? brandColor;
  // ... implementation
}
```

### Typography
Use `TextTheme` consistently.
`style: Theme.of(context).textTheme.headlineMedium`

## 5. Advanced UI Components

- **Slivers**: Use `CustomScrollView` and `SliverAppBar` for scrollable areas with collapsing headers.
- **CustomPainters**: For unique shapes or charts that ready-made widgets can't handle.
- **Glassmorphism**: Use `BackdropFilter` with a semi-transparent white/black container.

## 6. Performance Pitfalls

- ❌ `Opacity` widget on large subtrees (use `FadeTransition` or `AnimatedOpacity`).
- ❌ Clipping (ClipRRect) on heavy lists (expensive).
- ❌ Unnecessary `build()` calls (use `const` constructors everywhere).
- ❌ Blocking the main thread (move heavy JSON parsing to `compute`).

## 7. Folder Structure for UI

```
lib/
├── core/
│   ├── theme/          # AppTheme, text styles, colors
│   └── responsive/     # Responsive layout helpers
├── presentation/
│   ├── components/     # Reusable atoms (Buttons, Inputs)
│   │   ├── animations/ # Reusable animation widgets
│   │   └── dialogs/    # Custom dialogs
│   └── screens/
│       └── home/
│           ├── home_screen.dart
│           └── widgets/ # Widgets specific to Home
```
