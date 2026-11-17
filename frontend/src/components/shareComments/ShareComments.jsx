import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api";
import { useAuth } from "../../context/AuthContext";

const ShareComments = ({ postId, onPosted }) => {
  const { user } = useAuth();
  const [body, setBody] = useState("");
  const [message, setMessage] = useState({ text: "", error: false });

  const flash = (text, error = false) => {
    setMessage({ text, error });
    setTimeout(() => setMessage({ text: "", error: false }), 4000);
  };

  const submit = async () => {
    if (!body.trim()) return flash("Write a comment first.", true);
    try {
      await api.addComment(postId, body);
      setBody("");
      flash("Comment added");
      onPosted?.();
    } catch (err) {
      flash(err.message, true);
    }
  };

  if (!user) {
    return (
      <div className="share">
        <div className="shareWrapper">
          <Link to="/login">Log in</Link> to comment.
        </div>
      </div>
    );
  }

  return (
    <div className="share">
      <div className="shareWrapper">
        <div className="shareTop">
          <input
            placeholder="Add a comment"
            className="shareInput"
            type="text"
            value={body}
            maxLength={400}
            onChange={(e) => setBody(e.target.value)}
          />
        </div>
        <hr className="shareHr" />
        <span className="successfull" style={{ color: message.error ? "#c62828" : undefined }}>
          {message.text}
        </span>
        <div className="shareBottom">
          <button type="button" className="shareButton" onClick={submit}>
            Share
          </button>
        </div>
      </div>
    </div>
  );
};

export default ShareComments;
