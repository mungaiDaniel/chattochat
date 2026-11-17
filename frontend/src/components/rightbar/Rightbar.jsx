import "./rightbar.css";
import Online from "../online/Online";
import useFetch from "../../hooks/useFetch";
import { api } from "../../api";
import { imageSrc } from "../../utils/media";

export default function Rightbar({ profile }) {
  const { data: users, loading } = useFetch(() => api.getUsers());
  const list = users || [];

  return (
    <div className="rightbar">
      <div className="rightbarWrapper">
        {loading && <p>Loading...</p>}
        {profile ? (
          <>
            <h4 className="rightbarTitle">People</h4>
            <div className="rightbarFollowings">
              {list.map((user) => (
                <div key={user.id} className="rightbarFollowing">
                  <img src={imageSrc(user.personPic)} alt={user.name} className="rightbarFollowingImg" />
                  <span className="rightbarFollowingName">{user.name}</span>
                </div>
              ))}
            </div>
          </>
        ) : (
          <>
            <h4 className="rightbarTitle">Members</h4>
            <ul className="rightbarFriendList">
              {list.map((u) => (
                <Online key={u.id} user={u} />
              ))}
            </ul>
          </>
        )}
      </div>
    </div>
  );
}
