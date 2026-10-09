import { signupUser, loginUser, logoutUser } from '../api/auth.api';

export const authApi = {
  signup: signupUser,
  login: loginUser,
  logout: logoutUser,
};
