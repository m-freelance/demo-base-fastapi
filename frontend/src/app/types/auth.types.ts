/**
 * Login request DTO - matches backend OAuth2PasswordRequestForm
 * Note: Backend uses 'username' field for email (OAuth2 standard)
 */
export interface LoginRequest {
  username: string; // email address
  password: string;
}

/**
 * Login response DTO - matches backend LoginResponseDto
 */
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

/**
 * Register request DTO - matches backend RegisterRequestDto
 */
export interface RegisterRequest {
  email: string;
  password: string;
}

/**
 * Register response DTO - matches backend RegisterResponseDto
 */
export interface RegisterResponse {
  id: string; // UUID
  email: string;
}

