import { Navigate } from "react-router-dom";
import Topbar from "../../components/topbar/Topbar";
import Sidebar from "../../components/sidebar/Sidebar";
import Feed from "../../components/feed/Feed";
import Rightbar from "../../components/rightbar/Rightbar";
import "../home/home.css";
import { useAuth } from "../../context/AuthContext";

const MyPost = () => {
  const { user, ready } = useAuth();
  if (!ready) return <h2>Loading...</h2>;
  if (!user) return <Navigate to="/login" replace />;

  return (
    <>
      <Topbar />
      <div className="homeContainer">
        <Sidebar />
        <Feed mine />
        <Rightbar />
      </div>
    </>
  );
};

export default MyPost;
