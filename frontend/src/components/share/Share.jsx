import "./share.css";
import { useState } from "react";
import { Link } from "react-router-dom";
import { PermMedia } from "@mui/icons-material";
import { api } from "../../api";
import { useAuth } from "../../context/AuthContext";
import { imageSrc } from "../../utils/media";

export default function Share({ onPosted }) {
  const { user } = useAuth();
  const [body, setBody] = useState("");
  const [photo, setPhoto] = useState(null);
  const [message, setMessage] = useState({ text: "", error: false });
  const [busy, setBusy] = useState(false);

  const flash = (text, error = false) => {
    setMessage({ text, error });
    setTimeout(() => setMessage({ text: "", error: false }), 4000);
  };

  const submit = async () => {
    if (!body.trim()) return flash("Write something first.", true);
    setBusy(true);
    try {
      await api.createPost({ body, photo });
      setBody("");
      setPhoto(null);
      flash("Posted!");
      onPosted?.();
    } catch (err) {
      flash(err.message, true);
    } finally {
      setBusy(false);
    }
  };

  if (!user) {
    return (
      <div className="share">
        <div className="shareWrapper">
          <p className="mb-0">
            <Link to="/login">Log in</Link> to share a post.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="share">
      <div className="shareWrapper">
        <div className="shareTop">
          <img className="shareProfileImg" src={imageSrc(user.personPic)} alt="" />
          <input
            placeholder={`What's on your mind, ${user.name.split(" ")[0]}?`}
            className="shareInput"
            value={body}
            maxLength={500}
            onChange={(e) => setBody(e.target.value)}
          />
        </div>
        <hr className="shareHr" />
        <span className="successfull" style={{ color: message.error ? "#c62828" : undefined }}>
          {message.text}
        </span>
        <div className="shareBottom">
          <div className="shareOptions">
            <label htmlFor="postPhoto" className="shareOption">
              <PermMedia htmlColor="tomato" className="shareIcon" />
              <span className="shareOptionText">{photo ? photo.name : "Photo"}</span>
              <input
                id="postPhoto"
                type="file"
                accept=".png,.jpg,.jpeg,.gif,.webp"
                style={{ display: "none" }}
                onChange={(e) => setPhoto(e.target.files[0] || null)}
              />
            </label>
          </div>
          <button type="button" className="shareButton" onClick={submit} disabled={busy}>
            {busy ? "Posting..." : "Share"}
          </button>
        </div>
      </div>
    </div>
  );
}
