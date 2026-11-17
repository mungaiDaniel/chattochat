import axios from "axios";
import { API_URL } from "./config";
import { getToken } from "../auth";

const http = axios.create({ baseURL: `${API_URL}/api/v1` });

http.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Normalise every failure into an Error with a readable message.
http.interceptors.response.use(
  (response) => response,
  (error) => {
    const body = error.response?.data;
    let message = body?.message;
    if (body?.errors) {
      message = Object.entries(body.errors)
        .map(([field, msgs]) => `${field}: ${[].concat(msgs).join(" ")}`)
        .join("; ");
    }
    if (!message) message = error.response ? `Request failed (${error.response.status})` : "Cannot reach the server";
    const err = new Error(message);
    err.status = error.response?.status;
    return Promise.reject(err);
  }
);

const unwrap = (promise) => promise.then((res) => res.data.data);

export const assetUrl = (path) => {
  if (!path) return null;
  if (/^(https?:|data:|blob:)/.test(path)) return path;
  return `${API_URL}/${path.replace(/^\/+/, "")}`;
};

export const login = ({ username, password }) =>
  http.post("/login", { username, password }).then((res) => res.data);
export const register = (form) => unwrap(http.post("/register", form));

export const getUsers = () => unwrap(http.get("/user"));
export const getMe = () => unwrap(http.get("/user/me"));
export const updateProfile = (fields) => unwrap(http.put("/user/profile", fields));
export const upgradeRole = (user_role) => unwrap(http.put("/premium", { user_role }));
export const uploadPhoto = (file) => {
  const form = new FormData();
  form.append("photo", file);
  return http.post("/upload-photo", form).then((res) => res.data);
};

export const getPosts = () => unwrap(http.get("/post"));
export const getPost = (id) => unwrap(http.get(`/post/${id}`));
export const getMyPosts = () => unwrap(http.get("/mypost"));
export const createPost = ({ body, photo }) => {
  if (!photo) return unwrap(http.post("/post", { body }));
  const form = new FormData();
  form.append("body", body);
  form.append("photo", photo);
  return unwrap(http.post("/post", form));
};
export const updatePost = (id, body) => unwrap(http.put(`/post/${id}`, { body }));
export const deletePost = (id) => http.delete(`/post/${id}`).then(() => undefined);

export const getComments = (postId) => unwrap(http.get(`/comments/${postId}`));
export const addComment = (postId, body) => unwrap(http.post(`/comment/${postId}`, { body }));

export const follow = (id) => unwrap(http.post(`/follow/${id}`));
export const unfollow = (id) => http.post(`/unfollow/${id}`).then(() => undefined);
export const getFollowing = () => unwrap(http.get("/following"));
