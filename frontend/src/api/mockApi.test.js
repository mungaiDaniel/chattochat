import * as mock from "./mockApi";
import { clearSession, setSession } from "../auth";

beforeEach(() => clearSession());

const loginDemo = async () => {
  const session = await mock.demoLogin();
  setSession(session);
  return session;
};

test("demo login returns the fake demo user", async () => {
  const session = await loginDemo();
  expect(session.data.email).toBe("demo@example.com");
  expect((await mock.getMe()).username).toBe("demo");
});

test("unknown user cannot log in", async () => {
  await expect(mock.login({ username: "nobody" })).rejects.toThrow("Invalid username or password");
});

test("created posts appear in the feed, can be edited and deleted", async () => {
  await loginDemo();
  const post = await mock.createPost({ body: "hello demo" });
  expect((await mock.getPosts())[0].id).toBe(post.id);

  await mock.updatePost(post.id, "edited");
  expect((await mock.getPost(post.id)).body).toBe("edited");

  await mock.deletePost(post.id);
  await expect(mock.getPost(post.id)).rejects.toThrow("Post not found");
});

test("users cannot modify other users' posts", async () => {
  await loginDemo();
  await expect(mock.deletePost(1)).rejects.toThrow("only modify your own");
});

test("comments are added to the post", async () => {
  await loginDemo();
  const before = (await mock.getComments(2)).length;
  await mock.addComment(2, "nice");
  expect((await mock.getComments(2)).length).toBe(before + 1);
});

test("follow and unfollow update the following list", async () => {
  await loginDemo();
  await mock.follow(3);
  expect((await mock.getFollowing()).map((u) => u.id)).toContain(3);
  await expect(mock.follow(3)).rejects.toThrow("already follow");
  await mock.unfollow(3);
  expect((await mock.getFollowing()).map((u) => u.id)).not.toContain(3);
});

test("public user data never includes emails", async () => {
  (await mock.getUsers()).forEach((u) => expect(u.email).toBeUndefined());
});

test("registration validates and rejects duplicates", async () => {
  await expect(mock.register({ name: "A", username: "demo", email: "x@example.com", password: "longenough" })).rejects.toThrow(
    "already registered"
  );
  const user = await mock.register({ name: "New Person", username: "newbie", email: "new@example.com", password: "longenough" });
  expect(user.user_role).toBe("user");
});
