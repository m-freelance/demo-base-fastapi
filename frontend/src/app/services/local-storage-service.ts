import {
  effect,
  inject,
  Injectable,
  Injector,
  PLATFORM_ID,
  signal,
  Signal,
  WritableSignal,
} from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

/**
 * Represents a reactive localStorage item with automatic synchronization.
 */
export interface StorageSignal<T> {
  /** Read-only signal containing the current value */
  value: Signal<T>;
  /** Update the value (also updates localStorage) */
  set: (value: T) => void;
  /** Remove the item from localStorage and reset to default */
  remove: () => void;
}

/**
 * Options for creating a storage signal.
 */
export interface StorageOptions<T> {
  /** Default value when item doesn't exist in localStorage */
  defaultValue: T;
  /** Custom serializer (defaults to JSON.stringify) */
  serialize?: (value: T) => string;
  /** Custom deserializer (defaults to JSON.parse) */
  deserialize?: (value: string) => T;
}

/**
 * Service providing reactive localStorage functionality with Angular signals.
 *
 * Usage example:
 * ```typescript
 * const tokenStorage = localStorageService.connect<string | null>('auth_token', {
 *   defaultValue: null
 * });
 *
 * // Read current value
 * const currentToken = tokenStorage.value();
 *
 * // Update value (automatically syncs to localStorage)
 * tokenStorage.set('new-token');
 *
 * // Remove from localStorage
 * tokenStorage.remove();
 * ```
 */
@Injectable({
  providedIn: 'root',
})
export class LocalStorageService {
  private readonly platformId = inject(PLATFORM_ID);
  private readonly isBrowser = isPlatformBrowser(this.platformId);
  private readonly injector = inject(Injector);

  /** Cache of created storage signals to avoid duplicates */
  private readonly storageSignals = new Map<string, StorageSignal<unknown>>();

  /**
   * Creates a reactive connection to a localStorage item.
   * Changes to the signal automatically sync to localStorage.
   *
   * @param key - The localStorage key
   * @param options - Configuration options including default value
   * @returns StorageSignal with reactive value and mutation methods
   */
  connect<T>(key: string, options: StorageOptions<T>): StorageSignal<T> {
    // Return cached signal if already created
    const cached = this.storageSignals.get(key);
    if (cached) {
      return cached as StorageSignal<T>;
    }

    const {
      defaultValue,
      serialize = (v: T) => JSON.stringify(v),
      deserialize = (v: string) => JSON.parse(v) as T,
    } = options;

    // Initialize with stored value or default
    const initialValue = this.getStoredValue(key, defaultValue, deserialize);
    const _signal: WritableSignal<T> = signal<T>(initialValue);

    // Bind the effect to this service's injector. Without it, connect() would
    // only work from a constructor and the effect would die with whichever
    // caller happened to create the entry first.
    effect(
      () => {
        const currentValue = _signal();
        this.setStoredValue(key, currentValue, serialize, defaultValue);
      },
      { injector: this.injector },
    );

    const storageSignal: StorageSignal<T> = {
      value: _signal.asReadonly(),
      set: (value: T) => _signal.set(value),
      remove: () => {
        this.removeItem(key);
        _signal.set(defaultValue);
      },
    };

    this.storageSignals.set(key, storageSignal as StorageSignal<unknown>);
    return storageSignal;
  }

  /**
   * Creates a simple string storage connection.
   * Convenience method for string values.
   */
  connectString(key: string, defaultValue: string | null = null): StorageSignal<string | null> {
    return this.connect<string | null>(key, {
      defaultValue,
      serialize: (v) => v ?? '',
      deserialize: (v) => (v === '' ? null : v),
    });
  }

  /**
   * Directly get an item from localStorage (non-reactive).
   */
  getItem(key: string): string | null {
    if (!this.isBrowser) return null;
    return localStorage.getItem(key);
  }

  /**
   * Directly set an item in localStorage (non-reactive).
   */
  setItem(key: string, value: string): void {
    if (!this.isBrowser) return;
    localStorage.setItem(key, value);
  }

  /**
   * Directly remove an item from localStorage.
   */
  removeItem(key: string): void {
    if (!this.isBrowser) return;
    localStorage.removeItem(key);
    // The cache entry deliberately stays. Evicting it here would let a later
    // connect() hand out a second signal for a key an earlier caller still
    // holds, and writes through one would be invisible to the other.
  }

  /**
   * Clear all localStorage items.
   */
  clear(): void {
    if (!this.isBrowser) return;
    localStorage.clear();
    // Reset the live signals instead of forgetting them, so existing holders
    // observe the wipe rather than keeping a value storage no longer has.
    for (const storageSignal of this.storageSignals.values()) {
      storageSignal.remove();
    }
  }

  /**
   * Check if localStorage is available.
   */
  isAvailable(): boolean {
    return this.isBrowser;
  }

  /**
   * Get the stored value from localStorage with deserialization.
   */
  private getStoredValue<T>(key: string, defaultValue: T, deserialize: (v: string) => T): T {
    if (!this.isBrowser) return defaultValue;

    try {
      const stored = localStorage.getItem(key);
      if (stored === null) return defaultValue;
      return deserialize(stored);
    } catch {
      return defaultValue;
    }
  }

  /**
   * Set the stored value in localStorage with serialization.
   */
  private setStoredValue<T>(
    key: string,
    value: T,
    serialize: (v: T) => string,
    defaultValue: T,
  ): void {
    if (!this.isBrowser) return;

    // If value equals default and represents "empty", remove from storage
    if (value === defaultValue && (value === null || value === undefined)) {
      localStorage.removeItem(key);
      return;
    }

    try {
      const serialized = serialize(value);
      localStorage.setItem(key, serialized);
    } catch (error) {
      console.error(`LocalStorageService: Failed to serialize value for key "${key}"`, error);
    }
  }
}
