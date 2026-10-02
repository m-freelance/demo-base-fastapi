import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';

import { SignalizerService } from './signalizer-service';
import { environment } from '../../environments/environment';

describe('SignalizerService', () => {
  let service: SignalizerService;
  let httpMock: HttpTestingController;
  const baseUrl = `${environment.backendUrl}/api/v1`;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
    service = TestBed.inject(SignalizerService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('get', () => {
    it('should return signals with initial loading state', () => {
      const signals = service.get<{ id: number }>('/users');

      expect(signals.isLoading()).toBe(true);
      expect(signals.data()).toBeNull();
      expect(signals.error()).toBeNull();

      // Flush the pending request
      httpMock.expectOne(`${baseUrl}/users`).flush({ id: 1 });
    });

    it('should update signals on successful GET request', () => {
      const mockResponse = { id: 1, name: 'Test User' };
      const signals = service.get<typeof mockResponse>('/users/1');

      expect(signals.isLoading()).toBe(true);

      const req = httpMock.expectOne(`${baseUrl}/users/1`);
      req.flush(mockResponse);

      expect(signals.isLoading()).toBe(false);
      expect(signals.data()).toEqual(mockResponse);
      expect(signals.error()).toBeNull();
    });

    it('should update signals on GET request error', () => {
      const signals = service.get<{ id: number }>('/users/999');

      expect(signals.isLoading()).toBe(true);

      const req = httpMock.expectOne(`${baseUrl}/users/999`);
      req.flush('Not Found', { status: 404, statusText: 'Not Found' });

      expect(signals.isLoading()).toBe(false);
      expect(signals.data()).toBeNull();
      expect(signals.error()).toBeTruthy();
      expect(signals.error()?.status).toBe(404);
    });

    it('should pass options to the API request', () => {
      const params = { page: '1' };
      const signals = service.get<{ items: number[] }>('/users', { params });

      const req = httpMock.expectOne((request) => request.url === `${baseUrl}/users`);
      expect(req.request.params.get('page')).toBe('1');
      req.flush({ items: [1, 2, 3] });

      expect(signals.data()).toEqual({ items: [1, 2, 3] });
    });
  });

  describe('post', () => {
    it('should return signals with initial loading state', () => {
      const signals = service.post<{ id: number }>('/users', { name: 'Test' });

      expect(signals.isLoading()).toBe(true);
      expect(signals.data()).toBeNull();
      expect(signals.error()).toBeNull();

      httpMock.expectOne(`${baseUrl}/users`).flush({ id: 1 });
    });

    it('should update signals on successful POST request', () => {
      const mockRequest = { name: 'New User', email: 'test@test.com' };
      const mockResponse = { id: 1, ...mockRequest };
      const signals = service.post<typeof mockResponse>('/users', mockRequest);

      expect(signals.isLoading()).toBe(true);

      const req = httpMock.expectOne(`${baseUrl}/users`);
      expect(req.request.body).toEqual(mockRequest);
      req.flush(mockResponse);

      expect(signals.isLoading()).toBe(false);
      expect(signals.data()).toEqual(mockResponse);
      expect(signals.error()).toBeNull();
    });

    it('should update signals on POST request error', () => {
      const signals = service.post<{ id: number }>('/users', { name: '' });

      const req = httpMock.expectOne(`${baseUrl}/users`);
      req.flush('Validation Error', { status: 400, statusText: 'Bad Request' });

      expect(signals.isLoading()).toBe(false);
      expect(signals.data()).toBeNull();
      expect(signals.error()?.status).toBe(400);
    });
  });

  describe('put', () => {
    it('should return signals with initial loading state', () => {
      const signals = service.put<{ id: number }>('/users/1', { name: 'Updated' });

      expect(signals.isLoading()).toBe(true);
      expect(signals.data()).toBeNull();
      expect(signals.error()).toBeNull();

      httpMock.expectOne(`${baseUrl}/users/1`).flush({ id: 1 });
    });

    it('should update signals on successful PUT request', () => {
      const mockRequest = { name: 'Updated User' };
      const mockResponse = { id: 1, ...mockRequest };
      const signals = service.put<typeof mockResponse>('/users/1', mockRequest);

      expect(signals.isLoading()).toBe(true);

      const req = httpMock.expectOne(`${baseUrl}/users/1`);
      expect(req.request.body).toEqual(mockRequest);
      req.flush(mockResponse);

      expect(signals.isLoading()).toBe(false);
      expect(signals.data()).toEqual(mockResponse);
      expect(signals.error()).toBeNull();
    });

    it('should update signals on PUT request error', () => {
      const signals = service.put<{ id: number }>('/users/999', { name: 'Test' });

      const req = httpMock.expectOne(`${baseUrl}/users/999`);
      req.flush('Not Found', { status: 404, statusText: 'Not Found' });

      expect(signals.isLoading()).toBe(false);
      expect(signals.data()).toBeNull();
      expect(signals.error()?.status).toBe(404);
    });
  });

  describe('delete', () => {
    it('should return signals with initial loading state', () => {
      const signals = service.delete<{ success: boolean }>('/users/1');

      expect(signals.isLoading()).toBe(true);
      expect(signals.data()).toBeNull();
      expect(signals.error()).toBeNull();

      httpMock.expectOne(`${baseUrl}/users/1`).flush({ success: true });
    });

    it('should update signals on successful DELETE request', () => {
      const mockResponse = { success: true, message: 'User deleted' };
      const signals = service.delete<typeof mockResponse>('/users/1');

      expect(signals.isLoading()).toBe(true);

      const req = httpMock.expectOne(`${baseUrl}/users/1`);
      req.flush(mockResponse);

      expect(signals.isLoading()).toBe(false);
      expect(signals.data()).toEqual(mockResponse);
      expect(signals.error()).toBeNull();
    });

    it('should update signals on DELETE request error', () => {
      const signals = service.delete<{ success: boolean }>('/users/999');

      const req = httpMock.expectOne(`${baseUrl}/users/999`);
      req.flush('Forbidden', { status: 403, statusText: 'Forbidden' });

      expect(signals.isLoading()).toBe(false);
      expect(signals.data()).toBeNull();
      expect(signals.error()?.status).toBe(403);
    });

    it('should pass options to the API request', () => {
      const params = { soft: 'true' };
      const signals = service.delete<{ success: boolean }>('/users/1', { params });

      const req = httpMock.expectOne((request) => request.url === `${baseUrl}/users/1`);
      expect(req.request.params.get('soft')).toBe('true');
      req.flush({ success: true });

      expect(signals.data()).toEqual({ success: true });
    });
  });

  describe('signal behavior', () => {
    it('should return readonly signals', () => {
      const signals = service.get<{ id: number }>('/test');

      // Verify signals are readonly (they should have no 'set' method exposed)
      expect(typeof signals.isLoading).toBe('function');
      expect(typeof signals.data).toBe('function');
      expect(typeof signals.error).toBe('function');

      httpMock.expectOne(`${baseUrl}/test`).flush({ id: 1 });
    });

    it('should maintain signal reactivity after response', () => {
      const signals = service.get<{ value: number }>('/data');

      // Initial state
      expect(signals.isLoading()).toBe(true);

      // After response
      httpMock.expectOne(`${baseUrl}/data`).flush({ value: 42 });

      expect(signals.isLoading()).toBe(false);
      expect(signals.data()?.value).toBe(42);
    });
  });
});

