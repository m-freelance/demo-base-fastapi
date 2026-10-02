import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface ApiRequestOptions {
  headers?: HttpHeaders | { [header: string]: string | string[] };
  params?: HttpParams | { [param: string]: string | number | boolean | (string | number | boolean)[] };
}

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.backendUrl}/api/v1`;

  /**
   * Performs a GET request to the specified endpoint.
   * @param endpoint - The endpoint path without base URL and api/v1 prefix (e.g., '/users', '/auth/login')
   * @param options - Optional HTTP request options
   * @returns Observable of the response
   */
  get<T>(endpoint: string, options?: ApiRequestOptions): Observable<T> {
    return this.http
      .get<T>(this.buildUrl(endpoint), options)
      .pipe(catchError(this.handleError));
  }

  /**
   * Performs a POST request to the specified endpoint.
   * @param endpoint - The endpoint path without base URL and api/v1 prefix
   * @param body - The request body
   * @param options - Optional HTTP request options
   * @returns Observable of the response
   */
  post<T>(endpoint: string, body: unknown, options?: ApiRequestOptions): Observable<T> {
    return this.http
      .post<T>(this.buildUrl(endpoint), body, options)
      .pipe(catchError(this.handleError));
  }

  /**
   * Performs a PUT request to the specified endpoint.
   * @param endpoint - The endpoint path without base URL and api/v1 prefix
   * @param body - The request body
   * @param options - Optional HTTP request options
   * @returns Observable of the response
   */
  put<T>(endpoint: string, body: unknown, options?: ApiRequestOptions): Observable<T> {
    return this.http
      .put<T>(this.buildUrl(endpoint), body, options)
      .pipe(catchError(this.handleError));
  }

  /**
   * Performs a DELETE request to the specified endpoint.
   * @param endpoint - The endpoint path without base URL and api/v1 prefix
   * @param options - Optional HTTP request options
   * @returns Observable of the response
   */
  delete<T>(endpoint: string, options?: ApiRequestOptions): Observable<T> {
    return this.http
      .delete<T>(this.buildUrl(endpoint), options)
      .pipe(catchError(this.handleError));
  }

  /**
   * Builds the full URL from the endpoint.
   * @param endpoint - The endpoint path
   * @returns Full URL string
   */
  private buildUrl(endpoint: string): string {
    // Ensure endpoint starts with /
    const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    return `${this.baseUrl}${normalizedEndpoint}`;
  }

  /**
   * Handles HTTP errors.
   * @param error - The HTTP error response
   * @returns Observable that throws the error
   */
  private handleError(error: HttpErrorResponse): Observable<never> {
    return throwError(() => error);
  }
}

