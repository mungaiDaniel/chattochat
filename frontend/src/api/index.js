// Single entry point for all data access. Components import `api` and never know
// whether they are talking to the Flask backend or to the in-memory demo.
import { DEMO_MODE } from "./config";

// The condition is written against process.env directly so webpack can inline it
// and drop the unused implementation (the mock never ships in a non-demo build).
const impl =
  process.env.REACT_APP_DEMO_MODE === "true" ? require("./mockApi") : require("./realApi");

export { DEMO_MODE };
export const api = impl;
