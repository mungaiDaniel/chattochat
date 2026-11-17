// Tiny session helper. The JWT (or the fake demo token) lives in localStorage.
const KEYS = { token: "token", id: "user_id", role: "user_role" };

const read = (key) => {
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
};

export const getToken = () => read(KEYS.token);
export const getUserId = () => {
  const id = read(KEYS.id);
  return id ? Number(id) : null;
};
export const getRole = () => read(KEYS.role);
export const isLoggedIn = () => Boolean(getToken());

export function setSession({ token, id, user_role }) {
  window.localStorage.setItem(KEYS.token, token);
  window.localStorage.setItem(KEYS.id, String(id));
  window.localStorage.setItem(KEYS.role, user_role);
}

export function setRole(role) {
  window.localStorage.setItem(KEYS.role, role);
}

export function clearSession() {
  Object.values(KEYS).forEach((key) => window.localStorage.removeItem(key));
}
