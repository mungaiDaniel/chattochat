import { useState } from "react";
import { api } from "../../api";

const FollowButton = ({ user, initiallyFollowing = false }) => {
  const [isFollowing, setIsFollowing] = useState(initiallyFollowing);
  const [error, setError] = useState("");

  const toggle = async () => {
    setError("");
    try {
      if (isFollowing) await api.unfollow(user.id);
      else await api.follow(user.id);
      setIsFollowing(!isFollowing);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <button className="btn" onClick={toggle}>
        {isFollowing ? "Unfollow" : "Follow"}
      </button>
      {error && <small className="text-danger d-block">{error}</small>}
    </div>
  );
};

export default FollowButton;
