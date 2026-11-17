import "./post.css";
import { useState } from "react";
import { Link } from "react-router-dom";
import { MoreVert, ThumbUpAlt } from "@mui/icons-material";
import { api } from "../../api";
import { useAuth } from "../../context/AuthContext";
import { formatDate, imageSrc } from "../../utils/media";

export default function Post({ post, onChanged }) {
  const { user } = useAuth();
  const [likes, setLikes] = useState(post.likes);
  const [liked, setLiked] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(post.body);
  const [error, setError] = useState("");

  const isOwner = user && user.id === post.user_id;

  const toggleLike = () => {
    setLikes((n) => (liked ? n - 1 : n + 1));
    setLiked(!liked);
  };

  const saveEdit = async () => {
    setError("");
    try {
      await api.updatePost(post.id, draft);
      setEditing(false);
      onChanged?.();
    } catch (err) {
      setError(err.message);
    }
  };

  const remove = async () => {
    setMenuOpen(false);
    if (!window.confirm("Delete this post?")) return;
    try {
      await api.deletePost(post.id);
      onChanged?.();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="post">
      <div className="postWrapper">
        <div className="postTop">
          <div className="postTopLeft">
            <img className="postProfileImg" src={imageSrc(post.author.personPic)} alt="" />
            <span className="postUsername">{post.author.name}</span>
            <span className="postDate">{formatDate(post.date_created)}</span>
          </div>
          {isOwner && (
            <div className="postTopRight postMenu">
              <button className="postMenuButton" aria-label="Post options" onClick={() => setMenuOpen((o) => !o)}>
                <MoreVert />
              </button>
              {menuOpen && (
                <div className="postMenuList">
                  <button
                    onClick={() => {
                      setEditing(true);
                      setMenuOpen(false);
                    }}
                  >
                    Edit
                  </button>
                  <button onClick={remove}>Delete</button>
                </div>
              )}
            </div>
          )}
        </div>
        <div className="postCenter">
          {editing ? (
            <div className="postEdit">
              <textarea value={draft} onChange={(e) => setDraft(e.target.value)} maxLength={500} rows={3} />
              <div className="postEditActions">
                <button className="btn btn-primary btn-sm" onClick={saveEdit}>
                  Save
                </button>
                <button
                  className="btn btn-light btn-sm"
                  onClick={() => {
                    setEditing(false);
                    setDraft(post.body);
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <span className="postText">{post.body}</span>
          )}
          {post.postpic && <img className="postImg" src={imageSrc(post.postpic)} alt="" />}
          {error && <div className="postError">{error}</div>}
        </div>
        <div className="postBottom">
          <div className="postBottomLeft">
            <ThumbUpAlt
              className="postIcons"
              onClick={toggleLike}
              style={{ color: liked ? "#1877f2" : undefined }}
            />
            <span className="postLikeCounter">{likes} people like this</span>
          </div>
          <div className="postBottomRight">
            <Link to={`/comments?id=${post.id}`} className="postCommentText">
              {post.comments.length} comments
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
