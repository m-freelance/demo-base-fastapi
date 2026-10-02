import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpErrorResponse, HttpParams } from '@angular/common/http';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';

import { ApiService } from './api-service';
import { environment } from '../../environments/environment';

describe('ApiService', () => {
  let service: ApiService;
  let httpMock: HttpTestingController;
  const baseUrl = `${environment.backendUrl}/api/v1`;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
    service = TestBed.inject(ApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('get', () => {
    it('should perform GET request with correct URL', () => {
      const mockResponse = { id: 1, name: 'Test' };

      service.get<typeof mockResponse>('/users').subscribe((response) => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${baseUrl}/users`);
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });

    it('should handle endpoint without leading slash', () => {
      const mockResponse = { data: 'test' };

      service.get<typeof mockResponse>('users').subscribe((response) => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${baseUrl}/users`);
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });

    it('should pass query params', () => {
      const mockResponse = [{ id: 1 }];
      const params = new HttpParams().set('page', '1').set('limit', '10');

      service.get<typeof mockResponse>('/users', { params }).subscribe((response) => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne((request) => request.url === `${baseUrl}/users`);
      expect(req.request.params.get('page')).toBe('1');
      expect(req.request.params.get('limit')).toBe('10');
      req.flush(mockResponse);
    });

    it('should handle HTTP errors', () => {
      service.get('/users').subscribe({
        next: () => {},
        error: (error: HttpErrorResponse) => {
          expect(error.status).toBe(404);
          expect(error.statusText).toBe('Not Found');
        },
      });

      const req = httpMock.expectOne(`${baseUrl}/users`);
      req.flush('Not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('post', () => {
    it('should perform POST request with correct URL and body', () => {
      const mockRequest = { name: 'New User', email: 'test@test.com' };
      const mockResponse = { id: 1, ...mockRequest };

      service.post<typeof mockResponse>('/users', mockRequest).subscribe((response) => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${baseUrl}/users`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(mockRequest);
      req.flush(mockResponse);
    });

    it('should handle HTTP errors on POST', () => {
      const mockRequest = { name: 'Test' };

      service.post('/users', mockRequest).subscribe({
        next: () => {},
        error: (error: HttpErrorResponse) => {
          expect(error.status).toBe(400);
        },
      });

      const req = httpMock.expectOne(`${baseUrl}/users`);
      req.flush('Bad Request', { status: 400, statusText: 'Bad Request' });
    });
  });

  describe('put', () => {
    it('should perform PUT request with correct URL and body', () => {
      const mockRequest = { name: 'Updated User' };
      const mockResponse = { id: 1, ...mockRequest };

      service.put<typeof mockResponse>('/users/1', mockRequest).subscribe((response) => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${baseUrl}/users/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(mockRequest);
      req.flush(mockResponse);
    });

    it('should handle HTTP errors on PUT', () => {
      const mockRequest = { name: 'Test' };

      service.put('/users/999', mockRequest).subscribe({
        next: () => {},
        error: (error: HttpErrorResponse) => {
          expect(error.status).toBe(404);
        },
      });

      const req = httpMock.expectOne(`${baseUrl}/users/999`);
      req.flush('Not Found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('delete', () => {
    it('should perform DELETE request with correct URL', () => {
      const mockResponse = { success: true };

      service.delete<typeof mockResponse>('/users/1').subscribe((response) => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${baseUrl}/users/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush(mockResponse);
    });

    it('should handle HTTP errors on DELETE', () => {
      service.delete('/users/999').subscribe({
        next: () => {},
        error: (error: HttpErrorResponse) => {
          expect(error.status).toBe(403);
        },
      });

      const req = httpMock.expectOne(`${baseUrl}/users/999`);
      req.flush('Forbidden', { status: 403, statusText: 'Forbidden' });
    });
  });

  describe('URL building', () => {
    it('should handle nested endpoints', () => {
      service.get('/users/1/posts').subscribe();

      const req = httpMock.expectOne(`${baseUrl}/users/1/posts`);
      expect(req.request.url).toBe(`${baseUrl}/users/1/posts`);
      req.flush([]);
    });

    it('should handle endpoints with query strings in options', () => {
      const params = { search: 'test', active: 'true' };

      service.get('/users', { params }).subscribe();

      const req = httpMock.expectOne((request) => request.url === `${baseUrl}/users`);
      expect(req.request.params.get('search')).toBe('test');
      expect(req.request.params.get('active')).toBe('true');
      req.flush([]);
    });
  });
});

