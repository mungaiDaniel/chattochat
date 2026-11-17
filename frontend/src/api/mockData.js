// Seed data for demo mode. Everything here is obviously fictional: made-up names,
// reserved example.com addresses and generated SVG artwork (no real photos or people).

const svg = (markup, w, h) =>
  `data:image/svg+xml;utf8,${encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${markup}</svg>`
  )}`;

export const avatar = (initials, color) =>
  svg(
    `<rect width="200" height="200" fill="${color}"/>` +
      `<text x="100" y="124" font-family="Arial,sans-serif" font-size="80" font-weight="700" ` +
      `fill="#fff" text-anchor="middle">${initials}</text>`,
    200,
    200
  );

const banner = (c1, c2, label) =>
  svg(
    `<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">` +
      `<stop offset="0" stop-color="${c1}"/><stop offset="1" stop-color="${c2}"/></linearGradient></defs>` +
      `<rect width="800" height="450" fill="url(#g)"/>` +
      `<text x="400" y="235" font-family="Arial,sans-serif" font-size="40" fill="#fff" ` +
      `fill-opacity=".85" text-anchor="middle">${label}</text>`,
    800,
    450
  );

export const coverPlaceholder = banner("#1877f2", "#7b4dff", "Sample cover photo");

const daysAgo = (days, hours = 0) =>
  new Date(Date.now() - days * 86400000 - hours * 3600000).toISOString();

export const DEMO_USER_ID = 1;

export const seedUsers = () => [
  { id: 1, name: "Demo User", username: "demo", email: "demo@example.com", user_role: "user",
    personPic: avatar("DU", "#1877f2"), coverPic: coverPlaceholder, date_created: daysAgo(40) },
  { id: 2, name: "Sample Sam", username: "sample_sam", email: "sam@example.com", user_role: "premium",
    personPic: avatar("SS", "#e0584d"), coverPic: null, date_created: daysAgo(35) },
  { id: 3, name: "Placeholder Pat", username: "placeholder_pat", email: "pat@example.com", user_role: "user",
    personPic: avatar("PP", "#2e9e6b"), coverPic: null, date_created: daysAgo(30) },
  { id: 4, name: "Test Taylor", username: "test_taylor", email: "taylor@example.com", user_role: "user",
    personPic: avatar("TT", "#c98a00"), coverPic: null, date_created: daysAgo(21) },
  { id: 5, name: "Mock Morgan", username: "mock_morgan", email: "morgan@example.com", user_role: "user",
    personPic: avatar("MM", "#8a4fff"), coverPic: null, date_created: daysAgo(14) },
  { id: 6, name: "Example Eli", username: "example_eli", email: "eli@example.com", user_role: "user",
    personPic: avatar("EE", "#00899e"), coverPic: null, date_created: daysAgo(7) },
];

export const seedPosts = () => [
  { id: 1, user_id: 2, body: "Welcome to the Chat2Chat demo! Everything you see here is sample data.",
    postpic: banner("#ff9966", "#ff5e62", "Sample image"), likes: 12, date_created: daysAgo(0, 2) },
  { id: 2, user_id: 3, body: "Try creating a post, editing it, or leaving a comment. Changes live only in this tab.",
    postpic: null, likes: 5, date_created: daysAgo(0, 6) },
  { id: 3, user_id: 4, body: "The real app is a Flask + PostgreSQL REST API. This page runs on mock data instead.",
    postpic: banner("#56ccf2", "#2f80ed", "Placeholder photo"), likes: 9, date_created: daysAgo(1) },
  { id: 4, user_id: 5, body: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    postpic: null, likes: 2, date_created: daysAgo(2) },
  { id: 5, user_id: 1, body: "This is a post written by the demo user. You can edit or delete it from the menu.",
    postpic: null, likes: 3, date_created: daysAgo(3) },
  { id: 6, user_id: 6, body: "Follow a few people on the Following page and watch the list update.",
    postpic: null, likes: 7, date_created: daysAgo(4) },
];

export const seedComments = () => [
  { id: 1, post_id: 1, user_id: 3, body: "Looks great, sample data is the best data.", date_created: daysAgo(0, 1) },
  { id: 2, post_id: 1, user_id: 4, body: "Nothing here is real, and that is the point.", date_created: daysAgo(0, 1) },
  { id: 3, post_id: 3, user_id: 2, body: "Mock data keeps the demo free to host.", date_created: daysAgo(0, 20) },
  { id: 4, post_id: 5, user_id: 2, body: "Nice post, Demo User!", date_created: daysAgo(2) },
];

export const seedFollows = () => [{ follower_id: 1, followee_id: 2 }];
