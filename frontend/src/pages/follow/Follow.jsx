import "./follow.css";
import { Navigate } from "react-router-dom";
import Topbar from "../../components/topbar/Topbar";
import FollowButton from "../../components/followButton/FollowButton";
import useFetch from "../../hooks/useFetch";
import { api } from "../../api";
import { useAuth } from "../../context/AuthContext";
import { formatDate, imageSrc } from "../../utils/media";

const Follow = () => {
  const { user: me, ready } = useAuth();
  const { data, error, loading } = useFetch(
    async () => {
      if (!me) return null;
      const [users, following] = await Promise.all([api.getUsers(), api.getFollowing()]);
      return { users, followingIds: new Set(following.map((u) => u.id)) };
    },
    [me?.id]
  );

  if (!ready) return <h2>Loading...</h2>;
  if (!me) return <Navigate to="/login" replace />;

  return (
    <>
      <Topbar />
      {loading && <h2>Loading...</h2>}
      {error && <div className="alert alert-danger m-3">{error}</div>}
      {data &&
        data.users
          .filter((u) => u.id !== me.id)
          .map((u) => (
            <div className="postr container" key={u.id}>
              <div className="postTopr">
                <div className="postTopLeftr">
                  <img className="postProfileImgr" src={imageSrc(u.personPic)} alt="" />
                  <span className="postUsernamer">{u.name}</span>
                  <span className="postDater">Joined {formatDate(u.date_created)}</span>
                </div>
                <div className="postTopRightr">
                  <FollowButton user={u} initiallyFollowing={data.followingIds.has(u.id)} />
                </div>
              </div>
            </div>
          ))}
    </>
  );
};

export default Follow;
