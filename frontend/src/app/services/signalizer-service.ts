import { inject, Injectable, signal, Signal, WritableSignal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { ApiService, ApiRequestOptions } from './api-service';

/**
 * Represents the result of an API request with signals for reactive state management.
 */
export interface ApiSignals<T> {
  /** Signal indicating if the request is currently loading */
  isLoading: Signal<boolean>;
  /** Signal containing the response data (null if not yet loaded or error occurred) */
  data: Signal<T | null>;
  /** Signal containing the error (null if no error) */
  error: Signal<HttpErrorResponse | null>;
}

/**
 * Internal writable version of ApiSignals for state management within the service.
 */
interface WritableApiSignals<T> {
  isLoading: WritableSignal<boolean>;
  data: WritableSignal<T | null>;
  error: WritableSignal<HttpErrorResponse | null>;
}

@Injectable({
  providedIn: 'root',
})
export class SignalizerService {
  private readonly apiService = inject(ApiService);

  /**
   * Creates a set of signals and performs a GET request.
   * @param endpoint - The endpoint path without base URL and api/v1 prefix
   * @param options - Optional HTTP request options
   * @returns ApiSignals containing isLoading, data, and error signals
   */
  get<T>(endpoint: string, options?: ApiRequestOptions): ApiSignals<T> {
    const signals = this.createSignals<T>();
    this.executeRequest(() => this.apiService.get<T>(endpoint, options), signals);
    return this.toReadonlySignals(signals);
  }

  /**
   * Creates a set of signals and performs a POST request.
   * @param endpoint - The endpoint path without base URL and api/v1 prefix
   * @param body - The request body
   * @param options - Optional HTTP request options
   * @returns ApiSignals containing isLoading, data, and error signals
   */
  post<T>(endpoint: string, body: unknown, options?: ApiRequestOptions): ApiSignals<T> {
    const signals = this.createSignals<T>();
    this.executeRequest(() => this.apiService.post<T>(endpoint, body, options), signals);
    return this.toReadonlySignals(signals);
  }

  /**
   * Creates a set of signals and performs a PUT request.
   * @param endpoint - The endpoint path without base URL and api/v1 prefix
   * @param body - The request body
   * @param options - Optional HTTP request options
   * @returns ApiSignals containing isLoading, data, and error signals
   */
  put<T>(endpoint: string, body: unknown, options?: ApiRequestOptions): ApiSignals<T> {
    const signals = this.createSignals<T>();
    this.executeRequest(() => this.apiService.put<T>(endpoint, body, options), signals);
    return this.toReadonlySignals(signals);
  }

  /**
   * Creates a set of signals and performs a DELETE request.
   * @param endpoint - The endpoint path without base URL and api/v1 prefix
   * @param options - Optional HTTP request options
   * @returns ApiSignals containing isLoading, data, and error signals
   */
  delete<T>(endpoint: string, options?: ApiRequestOptions): ApiSignals<T> {
    const signals = this.createSignals<T>();
    this.executeRequest(() => this.apiService.delete<T>(endpoint, options), signals);
    return this.toReadonlySignals(signals);
  }

  /**
   * Creates the initial writable signals with default values.
   */
  private createSignals<T>(): WritableApiSignals<T> {
    return {
      isLoading: signal<boolean>(true),
      data: signal<T | null>(null),
      error: signal<HttpErrorResponse | null>(null),
    };
  }

  /**
   * Converts writable signals to readonly signals for external consumption.
   */
  private toReadonlySignals<T>(signals: WritableApiSignals<T>): ApiSignals<T> {
    return {
      isLoading: signals.isLoading.asReadonly(),
      data: signals.data.asReadonly(),
      error: signals.error.asReadonly(),
    };
  }

  /**
   * Executes the API request and updates the signals accordingly.
   * @param requestFn - Function that returns the Observable for the request
   * @param signals - The writable signals to update
   */
  private executeRequest<T>(
    requestFn: () => import('rxjs').Observable<T>,
    signals: WritableApiSignals<T>
  ): void {
    requestFn().subscribe({
      next: (response) => {
        signals.data.set(response);
        signals.isLoading.set(false);
      },
      error: (err: HttpErrorResponse) => {
        signals.error.set(err);
        signals.isLoading.set(false);
      },
    });
  }
}

