import { TestBed } from '@angular/core/testing';
import { PLATFORM_ID, Injector, runInInjectionContext } from '@angular/core';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { LocalStorageService } from './local-storage-service';

describe('LocalStorageService', () => {
  let service: LocalStorageService;
  let injector: Injector;

  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();

    TestBed.configureTestingModule({
      providers: [
        LocalStorageService,
        { provide: PLATFORM_ID, useValue: 'browser' }
      ]
    });

    service = TestBed.inject(LocalStorageService);
    injector = TestBed.inject(Injector);
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('connect', () => {
    it('should create a storage signal with default value when key does not exist', () => {
      runInInjectionContext(injector, () => {
        const storage = service.connect<string | null>('test_key', { defaultValue: null });
        expect(storage.value()).toBeNull();
      });
    });

    it('should return existing value from localStorage', () => {
      localStorage.setItem('existing_key', JSON.stringify('existing_value'));
      runInInjectionContext(injector, () => {
        const storage = service.connect<string | null>('existing_key', { defaultValue: null });
        expect(storage.value()).toBe('existing_value');
      });
    });

    it('should update localStorage when value changes', () => {
      runInInjectionContext(injector, () => {
        const storage = service.connect<string | null>('update_key', { defaultValue: null });
        storage.set('new_value');
        // Effect runs synchronously in this context, but localStorage may need TestBed.flushEffects()
        TestBed.flushEffects();
        expect(localStorage.getItem('update_key')).toBe(JSON.stringify('new_value'));
      });
    });

    it('should remove item from localStorage when remove is called', () => {
      localStorage.setItem('remove_key', JSON.stringify('value'));
      runInInjectionContext(injector, () => {
        const storage = service.connect<string | null>('remove_key', { defaultValue: null });
        storage.remove();
        expect(localStorage.getItem('remove_key')).toBeNull();
        expect(storage.value()).toBeNull();
      });
    });

    it('should return cached signal for same key', () => {
      runInInjectionContext(injector, () => {
        const storage1 = service.connect<string | null>('cache_key', { defaultValue: null });
        const storage2 = service.connect<string | null>('cache_key', { defaultValue: null });
        expect(storage1).toBe(storage2);
      });
    });
  });

  describe('connectString', () => {
    it('should handle string values with proper serialization', () => {
      runInInjectionContext(injector, () => {
        const storage = service.connectString('string_key', null);
        storage.set('test_string');
        TestBed.flushEffects();
        expect(storage.value()).toBe('test_string');
        expect(localStorage.getItem('string_key')).toBe('test_string');
      });
    });

    it('should handle null values correctly', () => {
      runInInjectionContext(injector, () => {
        const storage = service.connectString('null_key', null);
        expect(storage.value()).toBeNull();
      });
    });
  });

  describe('direct methods', () => {
    it('should get item directly', () => {
      localStorage.setItem('direct_key', 'direct_value');
      expect(service.getItem('direct_key')).toBe('direct_value');
    });

    it('should set item directly', () => {
      service.setItem('set_key', 'set_value');
      expect(localStorage.getItem('set_key')).toBe('set_value');
    });

    it('should remove item directly', () => {
      localStorage.setItem('remove_direct', 'value');
      service.removeItem('remove_direct');
      expect(localStorage.getItem('remove_direct')).toBeNull();
    });

    it('should clear all items', () => {
      localStorage.setItem('key1', 'value1');
      localStorage.setItem('key2', 'value2');
      service.clear();
      expect(localStorage.length).toBe(0);
    });

    it('should check availability', () => {
      expect(service.isAvailable()).toBe(true);
    });
  });

  describe('custom serialization', () => {
    it('should use custom serialize and deserialize functions', () => {
      runInInjectionContext(injector, () => {
        const storage = service.connect<Date | null>('date_key', {
          defaultValue: null,
          serialize: (d) => d?.toISOString() ?? '',
          deserialize: (s) => s ? new Date(s) : null,
        });

        const testDate = new Date('2024-01-15T10:30:00.000Z');
        storage.set(testDate);
        TestBed.flushEffects();

        expect(storage.value()?.toISOString()).toBe(testDate.toISOString());
      });
    });
  });
});

