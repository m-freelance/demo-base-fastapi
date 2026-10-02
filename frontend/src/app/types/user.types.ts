/**
 * User role enum - matches backend UserRole
 */
export enum UserRole {
  ADMIN = 'admin',
  USER = 'user'
}

/**
 * User info response DTO - matches backend GetUserResponseDto
 */
export interface UserInfo {
  user_uuid: string;
  email: string;
  is_active: boolean;
  role: UserRole;
}
