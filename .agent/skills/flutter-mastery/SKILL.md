---
name: flutter-mastery
description: Advanced Flutter architectural patterns, state management, and production-grade engineering.
---

# Flutter Mastery

> **Goal**: Build scalable, maintainable, and robust Flutter applications using Clean Architecture and proven engineering practices.

## 1. Architectural Patterns

### Clean Architecture (The Standard)
Divide your app into three distinct layers. Dependency rule: Domain depends on nothing.

1.  **Domain Layer** (Inner Circle)
    *   **Entities**: Pure Dart objects (business logic).
    *   **Repositories (Interfaces)**: Contracts for data operations.
    *   **Use Cases**: Specific business actions (e.g., `LoginUser`, `GetProducts`).
2.  **Data Layer**
    *   **Models**: Data Transfer Objects (DTOs) with `fromJson`/`toJson`. Extend Entities.
    *   **Data Sources**: Remote (API) and Local (Database/Hive).
    *   **Repositories (Impl)**: Implementation of Domain interfaces.
3.  **Presentation Layer**
    *   **State Management**: BLoC / Riverpod / Provider.
    *   **Widgets**: UI components.

### Folder Structure
```
lib/
├── core/               # Shared utilities (Failure, UseCase, Extensions)
├── features/
│   └── authentication/
│       ├── domain/
│       │   ├── entities/
│       │   ├── repositories/
│       │   └── usecases/
│       ├── data/
│       │   ├── models/
│       │   ├── datasources/
│       │   └── repositories/
│       └── presentation/
│           ├── bloc/
│           └── pages/
```

## 2. State Management Mastery

### Riverpod (Recommended for Modern Flutter)
*   **Providers**: `Provider`, `StateProvider`, `FutureProvider`, `StreamProvider`.
*   **NotifierProvider**: For complex state logic (replace `StateNotifier`).
*   **AsyncValue**: Handle loading/error/data states gracefully in UI.
*   **Family & AutoDispose**: Manage state lifecycle and parameter passing.

### BLoC (Business Logic Component)
*   **Events**: Inputs to the Bloc (interactions).
*   **States**: Outputs from the Bloc (UI updates).
*   **BlocBuilder**: Rebuilds UI on state change.
*   **BlocListener**: Runs side effects (navigation, snackbars) on state change.

## 3. Dependency Injection (DI)

*   **get_it + injectable**: Use code generation for compile-time safety and ease of use.
*   **Riverpod**: Acts as its own DI system.

## 4. Testing Strategy

*   **Unit Tests**: Test UseCases, Repositories, and DataSources. Mock dependencies with `mockito` or `mocktail`.
*   **Widget Tests**: Test UI components in isolation (`pumpWidget`). Use `finder` to verify elements.
*   **Golden Tests**: Pixel-perfect regression testing (`golden_toolkit`).
*   **Integration Tests**: Run on huge device farms (`integration_test` package).

## 5. Advanced Dart Features

*   **Extensions**: Add functionality to existing classes without inheritance.
*   **Mixins**: Share behavior across class hierarchies.
*   **Generics**: Write reusable type-safe code.
*   **Streams/Async**: Master `StreamController`, `StreamSubscription`, and `Completer`.
*   **Isolates**: Offload heavy computation (parsing large JSON, image processing) to keep UI thread free.

## 6. Production Hardening

### Error Handling
*   Create a `Failure` class hierarchy (NetworkFailure, ServerFailure, CacheFailure).
*   Use `fpdart` or `dartz` for `Either<Failure, Success>` return types to force error handling.

### Networking
*   Use `Dio` or `Http` with Interceptors (logging, token refresher).
*   Handle timeouts and connectivity issues globally.

### Local Storage
*   **Secure**: `flutter_secure_storage` for tokens/secrets.
*   **Fast**: `hive` or `isar` for NoSQL local caching.
*   **Relational**: `drift` (SQLite) for complex relational queries.

## 7. CI/CD & Deploy
*   **Flavors**: Setup Dev, Staging, Prod environments (different API URLs, app bundles).
*   **Fastlane**: Automate screenshots and store deployment.
*   **Shorebird**: Code push (update apps without app store review).
