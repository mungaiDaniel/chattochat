import "./topbar.css";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { DEFAULT_AVATAR, imageSrc } from "../../utils/media";

const Topbar = () => {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  const logout = () => {
    signOut();
    navigate("/login");
  };

  return (
    <div className="topbarContainer">
      <div className="topbarLeft">
        <Link to="/home">
          <span className="logo">Chats</span>
        </Link>
      </div>
      <div className="topbarCenter" />
      <div className="topbarRight">
        <div className="topbarLinks">
          <Link to="/home">
            <span className="topbarLink">Feed</span>
          </Link>
          {user ? (
            <>
              <Link to="/profile">
                <span className="topbarLink">Profile</span>
              </Link>
              <Link to="/mypost">
                <span className="topbarLink">My Posts</span>
              </Link>
              <span onClick={logout} className="topbarLink" role="button">
                Logout
              </span>
            </>
          ) : (
            <>
              <Link to="/login">
                <span className="topbarLink">Login</span>
              </Link>
              <Link to="/register">
                <span className="topbarLink">Register</span>
              </Link>
            </>
          )}
        </div>
        <img src={user ? imageSrc(user.personPic) : DEFAULT_AVATAR} alt="" className="topbarImg" />
      </div>
    </div>
  );
};

export default Topbar;
