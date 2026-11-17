// In-memory implementation of the same interface as realApi.js, used when
// REACT_APP_DEMO_MODE=true. State lives in module scope, so create/edit/delete
// feel real for the session and reset on page reload. Nothing is sent anywhere.
import { getUserId } from "../auth";
import { DEMO_USER_ID, avatar, seedComments, seedFollows, seedPosts, seedUsers } from "./mockData";

const LATENCY_MS = 150;
const delay = (value) => new Promise((resolve) => setTimeout(() => resolve(value), LATENCY_MS));
const clone = (value) => JSON.parse(JSON.stringify(value));

const state = {
  users: seedUsers(),
  posts: seedPosts(),
  comments: seedComments(),
  follows: seedFollows(),
  nextId: { user: 100, post: 100, comment: 100 },
};

// Mirror the backend's error behaviour so the UI's error handling is exercised too.
const fail = (status, message) => {
  const err = new Error(message);
  err.status = status;
  return Promise.reject(err);
};

const publicUser = ({ email, ...rest }) => rest;
const findUser = (id) => state.users.find((u) => u.id === id);
const currentUser = () => findUser(getUserId());

const withAuthor = (post) => ({
  ...post,
  author: publicUser(findUser(post.user_id)),
  comments: state.comments
    .filter((c) => c.post_id === post.id)
    .map((c) => ({ ...c, author: publicUser(findUser(c.user_id)) })),
});
const newestFirst = (a, b) => new Date(b.date_created) - new Date(a.date_created) || b.id - a.id;

// Blob URLs for photos picked during the session; they die with the tab, like everything else.
export const assetUrl = (path) => path || null;

// --- auth -------------------------------------------------------------------------

export const login = ({ username }) => {
  const key = (username || "").toLowerCase();
  const user = state.users.find((u) => u.username === key || u.email === key);
  if (!user) return fail(401, "Invalid username or password");
  return delay({ token: `demo-token-${user.id}`, id: user.id, user_role: user.user_role, data: clone(user) });
};

// Only exposed in demo mode: the "Try Demo" button.
export const demoLogin = () => login({ username: "demo" });

export const register = ({ name, username, email, password }) => {
  if (!name || !username || !email || !password) return fail(422, "All fields are required");
  if (password.length < 8) return fail(422, "password: Shorter than minimum length 8.");
  const taken = state.users.some(
    (u) => u.username.toLowerCase() === username.toLowerCase() || u.email === email.toLowerCase()
  );
  if (taken) return fail(409, "Username or email is already registered");
  const initials = name.split(/\s+/).map((w) => w[0]).join("").slice(0, 2).toUpperCase();
  const user = {
    id: state.nextId.user++, name, username, email: email.toLowerCase(), user_role: "user",
    personPic: avatar(initials, "#6c757d"), coverPic: null, date_created: new Date().toISOString(),
  };
  state.users.push(user);
  return delay(clone(user));
};

// --- users ------------------------------------------------------------------------

export const getUsers = () => delay(state.users.map((u) => clone(publicUser(u))));
export const getMe = () => (currentUser() ? delay(clone(currentUser())) : fail(401, "Authentication required"));

export const updateProfile = (fields) => {
  const user = currentUser();
  if (!user) return fail(401, "Authentication required");
  if ("personPic" in fields) user.personPic = fields.personPic;
  if ("coverPic" in fields) user.coverPic = fields.coverPic;
  return delay(clone(user));
};

export const upgradeRole = (user_role) => {
  const user = currentUser();
  if (!user) return fail(401, "Authentication required");
  user.user_role = user_role;
  return delay({ user_role });
};

export const uploadPhoto = (file) => {
  const url = URL.createObjectURL(file);
  return delay({ filename: file.name, file_path: url, photo_url: url });
};

// --- posts ------------------------------------------------------------------------

export const getPosts = () => delay([...state.posts].sort(newestFirst).map((p) => clone(withAuthor(p))));

export const getPost = (id) => {
  const post = state.posts.find((p) => p.id === Number(id));
  return post ? delay(clone(withAuthor(post))) : fail(404, "Post not found");
};

export const getMyPosts = () =>
  delay(state.posts.filter((p) => p.user_id === getUserId()).sort(newestFirst).map((p) => clone(withAuthor(p))));

export const createPost = ({ body, photo }) => {
  if (!currentUser()) return fail(401, "Authentication required");
  if (!body || !body.trim()) return fail(422, "body: Must not be blank.");
  const post = {
    id: state.nextId.post++, user_id: getUserId(), body: body.trim(),
    postpic: photo ? URL.createObjectURL(photo) : null, likes: 0, date_created: new Date().toISOString(),
  };
  state.posts.push(post);
  return delay(clone(withAuthor(post)));
};

const ownPost = (id) => {
  const post = state.posts.find((p) => p.id === Number(id));
  if (!post) return [null, fail(404, "Post not found")];
  if (post.user_id !== getUserId()) return [null, fail(403, "You can only modify your own posts")];
  return [post, null];
};

export const updatePost = (id, body) => {
  const [post, error] = ownPost(id);
  if (error) return error;
  if (!body || !body.trim()) return fail(422, "body: Must not be blank.");
  post.body = body.trim();
  return delay(clone(withAuthor(post)));
};

export const deletePost = (id) => {
  const [post, error] = ownPost(id);
  if (error) return error;
  state.posts = state.posts.filter((p) => p !== post);
  state.comments = state.comments.filter((c) => c.post_id !== post.id);
  return delay(undefined);
};

// --- comments ---------------------------------------------------------------------

export const getComments = (postId) => {
  if (!state.posts.some((p) => p.id === Number(postId))) return fail(404, "Post not found");
  return delay(
    state.comments
      .filter((c) => c.post_id === Number(postId))
      .map((c) => clone({ ...c, author: publicUser(findUser(c.user_id)) }))
  );
};

export const addComment = (postId, body) => {
  if (!currentUser()) return fail(401, "Authentication required");
  if (!state.posts.some((p) => p.id === Number(postId))) return fail(404, "Post not found");
  if (!body || !body.trim()) return fail(422, "body: Must not be blank.");
  const comment = {
    id: state.nextId.comment++, post_id: Number(postId), user_id: getUserId(),
    body: body.trim(), date_created: new Date().toISOString(),
  };
  state.comments.push(comment);
  return delay(clone({ ...comment, author: publicUser(findUser(comment.user_id)) }));
};

// --- follows ----------------------------------------------------------------------

export const follow = (id) => {
  const me = getUserId() ?? DEMO_USER_ID;
  if (Number(id) === me) return fail(400, "You cannot follow yourself");
  if (!findUser(Number(id))) return fail(404, "User not found");
  if (state.follows.some((f) => f.follower_id === me && f.followee_id === Number(id))) {
    return fail(409, "You already follow this user");
  }
  state.follows.push({ follower_id: me, followee_id: Number(id) });
  return delay({ follower_id: me, followee_id: Number(id) });
};

export const unfollow = (id) => {
  const me = getUserId() ?? DEMO_USER_ID;
  state.follows = state.follows.filter((f) => !(f.follower_id === me && f.followee_id === Number(id)));
  return delay(undefined);
};

export const getFollowing = () =>
  delay(
    state.follows
      .filter((f) => f.follower_id === getUserId())
      .map((f) => clone(publicUser(findUser(f.followee_id))))
  );
