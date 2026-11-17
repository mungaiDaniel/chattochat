import "./friends.css";
import { imageSrc } from "../../utils/media";

export default function Friends({ user }) {
  return (
    <li className="sidebarFriend">
      <img className="sidebarFriendImg" src={imageSrc(user.personPic)} alt="" />
      <span className="sidebarFriendName">{user.name}</span>
    </li>
  );
}
