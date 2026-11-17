import "./sidebar.css";
import { Link } from "react-router-dom";
import { Bookmark, Group, Home, RssFeed, WorkspacePremium } from "@mui/icons-material";
import Friends from "../friends/Friends";
import useFetch from "../../hooks/useFetch";
import { api } from "../../api";

const Sidebar = () => {
  const { data: users } = useFetch(() => api.getUsers());

  return (
    <div className="sidebar">
      <div className="sidebarWrapper">
        <ul className="sidebarList">
          <Link to="/home">
            <li className="sidebarListItem">
              <RssFeed className="sidebarIcon" />
              <span className="sidebarListItemText">Feed</span>
            </li>
          </Link>
          <Link to="/profile">
            <li className="sidebarListItem">
              <Home className="sidebarIcon" />
              <span className="sidebarListItemText">Profile</span>
            </li>
          </Link>
          <Link to="/mypost">
            <li className="sidebarListItem">
              <Bookmark className="sidebarIcon" />
              <span className="sidebarListItemText">My Posts</span>
            </li>
          </Link>
          <Link to="/follow">
            <li className="sidebarListItem">
              <Group className="sidebarIcon" />
              <span className="sidebarListItemText">Following</span>
            </li>
          </Link>
          <Link to="/upgrade">
            <li className="sidebarListItem">
              <WorkspacePremium className="sidebarIcon" />
              <span className="sidebarListItemText">Upgrade</span>
            </li>
          </Link>
        </ul>
        <hr className="sidebarHr" />
        <ul className="sidebarFriendList">
          {(users || []).map((u) => (
            <Friends key={u.id} user={u} />
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Sidebar;
