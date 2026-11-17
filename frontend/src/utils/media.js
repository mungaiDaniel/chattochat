import { api } from "../api";

// Neutral grey silhouette, inline so it never depends on an external image host.
export const DEFAULT_AVATAR =
  "data:image/svg+xml;utf8," +
  encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">' +
      '<rect width="200" height="200" fill="#c9ced6"/><circle cx="100" cy="80" r="38" fill="#fff"/>' +
      '<path d="M30 190c4-42 36-62 70-62s66 20 70 62z" fill="#fff"/></svg>'
  );

// Resolve a path returned by the API (or mock) into something usable as <img src>.
export const imageSrc = (path, fallback = DEFAULT_AVATAR) => api.assetUrl(path) || fallback;

export const formatDate = (iso) =>
  iso ? new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }) : "";
