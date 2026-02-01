---
name: typescript-patterns
description: Advanced TypeScript patterns. Type utilities, generics, discriminated unions, branded types, module augmentation.
---

# TypeScript Patterns Skill

Advanced TypeScript patterns for type-safe, maintainable code.

## When to Use
- Designing type-safe APIs
- Creating reusable type utilities
- Implementing complex generic patterns
- Migrating JavaScript to TypeScript

## Core Patterns

### 1. Strict Configuration

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,
    "noPropertyAccessFromIndexSignature": true,
    "forceConsistentCasingInFileNames": true,
    "verbatimModuleSyntax": true
  }
}
```

### 2. Utility Types Mastery

```typescript
// Built-in utilities
type User = {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
};

type UserUpdate = Partial<User>;           // All optional
type UserRequired = Required<User>;        // All required  
type UserReadonly = Readonly<User>;        // All readonly
type UserPreview = Pick<User, 'id' | 'name'>;  // Select fields
type UserWithoutDates = Omit<User, 'createdAt'>; // Remove fields

// Record for dictionaries
type UserMap = Record<string, User>;

// Extract and Exclude
type EventType = 'click' | 'scroll' | 'keypress';
type MouseEvents = Extract<EventType, 'click' | 'scroll'>; // 'click' | 'scroll'
type NonMouseEvents = Exclude<EventType, 'click' | 'scroll'>; // 'keypress'
```

### 3. Discriminated Unions

```typescript
// Type-safe state machines
type RequestState<T> = 
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

function handleRequest<T>(state: RequestState<T>) {
  switch (state.status) {
    case 'idle':
      return 'Ready to fetch';
    case 'loading':
      return 'Loading...';
    case 'success':
      return state.data; // TypeScript knows `data` exists
    case 'error':
      return state.error.message; // TypeScript knows `error` exists
  }
}
```

### 4. Branded Types

```typescript
// Prevent mixing up primitive types
type UserId = string & { readonly brand: unique symbol };
type OrderId = string & { readonly brand: unique symbol };

function createUserId(id: string): UserId {
  return id as UserId;
}

function createOrderId(id: string): OrderId {
  return id as OrderId;
}

function getUser(id: UserId) { /* ... */ }
function getOrder(id: OrderId) { /* ... */ }

const userId = createUserId('user-123');
const orderId = createOrderId('order-456');

getUser(userId);   // ✅ OK
getUser(orderId);  // ❌ Error: OrderId not assignable to UserId
```

### 5. Generic Constraints

```typescript
// Constrain generics for safety
interface HasId {
  id: string;
}

function findById<T extends HasId>(items: T[], id: string): T | undefined {
  return items.find(item => item.id === id);
}

// Keyof constraint
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// Conditional types
type ArrayElement<T> = T extends (infer E)[] ? E : never;
type StringArray = ArrayElement<string[]>; // string
```

### 6. Template Literal Types

```typescript
// Type-safe string manipulation
type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type APIEndpoint = `/api/${string}`;
type Route = `${HTTPMethod} ${APIEndpoint}`;

// Event handlers
type EventName = 'click' | 'focus' | 'blur';
type EventHandler = `on${Capitalize<EventName>}`; // 'onClick' | 'onFocus' | 'onBlur'

// CSS properties
type CSSValue = `${number}${'px' | 'em' | 'rem' | '%'}`;
```

### 7. Type Guards

```typescript
// Custom type guards
function isString(value: unknown): value is string {
  return typeof value === 'string';
}

function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'name' in value
  );
}

// Assertion functions
function assertIsString(value: unknown): asserts value is string {
  if (typeof value !== 'string') {
    throw new Error('Expected string');
  }
}
```

### 8. Module Augmentation

```typescript
// Extend third-party types
declare module 'express' {
  interface Request {
    user?: {
      id: string;
      role: 'admin' | 'user';
    };
  }
}

// Extend global types
declare global {
  interface Window {
    analytics: {
      track: (event: string, data?: object) => void;
    };
  }
}
```

### 9. Mapped Types

```typescript
// Create types programmatically
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

type UserGetters = Getters<User>;
// { getId: () => string; getName: () => string; ... }

// Make all properties optional and nullable
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// Readonly deep
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};
```

### 10. Function Overloads

```typescript
// Multiple signatures for different use cases
function createElement(tag: 'div'): HTMLDivElement;
function createElement(tag: 'span'): HTMLSpanElement;
function createElement(tag: 'canvas'): HTMLCanvasElement;
function createElement(tag: string): HTMLElement {
  return document.createElement(tag);
}

const div = createElement('div'); // Type: HTMLDivElement
```

### 11. Const Assertions

```typescript
// Immutable, literal types
const routes = {
  home: '/',
  about: '/about',
  users: '/users',
} as const;

type Route = typeof routes[keyof typeof routes]; // '/' | '/about' | '/users'

// Array literals
const statuses = ['pending', 'approved', 'rejected'] as const;
type Status = typeof statuses[number]; // 'pending' | 'approved' | 'rejected'
```

### 12. Infer Keyword

```typescript
// Extract types from other types
type ReturnTypeOf<T> = T extends (...args: any[]) => infer R ? R : never;

type PromiseValue<T> = T extends Promise<infer V> ? V : T;
type Resolved = PromiseValue<Promise<string>>; // string

// Props from component
type PropsOf<T> = T extends React.ComponentType<infer P> ? P : never;
```

## Best Practices

1. **Prefer `unknown` over `any`** - Forces type checking
2. **Use `satisfies`** - Validate types without widening
3. **Avoid type assertions** - Use type guards instead
4. **Enable strict mode** - Catches bugs at compile time
5. **Use `readonly`** - Enforce immutability
6. **Document complex types** - Add JSDoc for generics
