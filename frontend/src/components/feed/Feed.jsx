import "./feed.css";
import Post from "../post/Post";
import Share from "../share/Share";
import useFetch from "../../hooks/useFetch";
import { api } from "../../api";

// `mine` switches between the public feed and the logged-in user's own posts.
export default function Feed({ mine = false }) {
  const { data: posts, error, loading, reload } = useFetch(() => (mine ? api.getMyPosts() : api.getPosts()), [mine]);

  return (
    <div className="feed">
      <div className="feedWrapper">
        <Share onPosted={reload} />
        {loading && <p className="mt-3">Loading...</p>}
        {error && <div className="alert alert-danger mt-3">{error}</div>}
        {posts && posts.length === 0 && <p className="mt-3">No posts yet.</p>}
        {(posts || []).map((p) => (
          <Post key={p.id} post={p} onChanged={reload} />
        ))}
      </div>
    </div>
  );
}
