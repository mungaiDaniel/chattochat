import React, { useState } from 'react'
import axios from 'axios';

const FollowButton = ({ user, initiallyFollowing = false }) => {
  const [isFollowing, setIsFollowing] = useState(initiallyFollowing);
  const token = localStorage.getItem("token");

  const handleFollow = async () => {
    try {
      await axios.post(
        `http://127.0.0.1:5000/api/v1/follow/${user.id}`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setIsFollowing(true);
    } catch (err) {
      console.log(err);
      // Optionally show an error message to the user
    }
  };

  const handleUnFollow = async () => {
    try {
      await axios.post(
        `http://127.0.0.1:5000/api/v1/unfollow/${user.id}`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setIsFollowing(false);
    } catch (err) {
      console.log(err);
      // Optionally show an error message to the user
    }
  };

  return (
    <div>
      {isFollowing ? (
        <button className="btn" onClick={handleUnFollow}>
          Unfollow
        </button>
      ) : (
        <button className="btn" onClick={handleFollow}>
          Follow
        </button>
      )}
    </div>
  );
};

export default FollowButton;