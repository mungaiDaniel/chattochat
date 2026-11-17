import "./profile.css";
import { useState } from "react";
import { Navigate } from "react-router-dom";
import { CalendarToday, Edit, Email, PermMedia } from "@mui/icons-material";
import Topbar from "../../components/topbar/Topbar";
import Sidebar from "../../components/sidebar/Sidebar";
import Feed from "../../components/feed/Feed";
import Rightbar from "../../components/rightbar/Rightbar";
import useFetch from "../../hooks/useFetch";
import { api } from "../../api";
import { useAuth } from "../../context/AuthContext";
import { imageSrc } from "../../utils/media";

const VALID_EXTENSIONS = ["png", "jpg", "jpeg", "gif", "webp"];
const DEFAULT_COVER =
  "data:image/svg+xml;utf8," +
  encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="400"><defs>' +
      '<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1877f2"/>' +
      '<stop offset="1" stop-color="#7b4dff"/></linearGradient></defs><rect width="1200" height="400" fill="url(#g)"/></svg>'
  );

export default function Profile() {
  const { user, ready, refresh } = useAuth();
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [activeTab, setActiveTab] = useState("posts");
  const { data: myPosts } = useFetch(() => (user ? api.getMyPosts() : Promise.resolve([])), [user?.id]);

  if (!ready) return <h2>Loading...</h2>;
  if (!user) return <Navigate to="/login" replace />;

  const flash = (setter, text) => {
    setter(text);
    setTimeout(() => setter(""), 4000);
  };

  // Upload the picked file, then store its path on the profile.
  const handleUpload = (field, label) => async (e) => {
    const file = e.target.files[0];
    e.target.value = "";
    if (!file) return;
    const ext = file.name.split(".").pop().toLowerCase();
    if (!VALID_EXTENSIONS.includes(ext)) {
      return flash(setError, "Please upload a png, jpg, jpeg, gif or webp image.");
    }
    setUploading(true);
    setError("");
    try {
      const uploaded = await api.uploadPhoto(file);
      await api.updateProfile({ [field]: uploaded.file_path });
      await refresh();
      flash(setSuccess, `${label} updated.`);
    } catch (err) {
      flash(setError, err.message);
    } finally {
      setUploading(false);
    }
  };

  const photos = (myPosts || []).filter((p) => p.postpic);

  return (
    <>
      <Topbar />
      <div className="profile">
        <Sidebar />
        <div className="profileRight">
          <div className="profileCoverSection">
            <div className="profileCoverContainer">
              <img className="profileCoverImg" src={imageSrc(user.coverPic, DEFAULT_COVER)} alt="Cover" />
              <div className="coverOverlay"></div>
              <label htmlFor="coverPicInput" className="coverPicUploadBtn">
                <Edit className="uploadIcon" />
                <span>Edit Cover Photo</span>
              </label>
              <input
                id="coverPicInput"
                type="file"
                accept="image/png,image/jpeg,image/gif,image/webp"
                onChange={handleUpload("coverPic", "Cover photo")}
                style={{ display: "none" }}
                disabled={uploading}
              />
            </div>
            <div className="profilePictureSection">
              <div className="profilePictureContainer">
                <img className="profileUserImg" src={imageSrc(user.personPic)} alt="Profile" />
                <label htmlFor="profilePicInput" className="profilePicUploadBtn">
                  <PermMedia className="uploadIcon" />
                </label>
                <input
                  id="profilePicInput"
                  type="file"
                  accept="image/png,image/jpeg,image/gif,image/webp"
                  onChange={handleUpload("personPic", "Profile picture")}
                  style={{ display: "none" }}
                  disabled={uploading}
                />
              </div>
            </div>
          </div>

          <div className="profileInfoSection">
            <div className="profileInfoContainer">
              <div className="profileInfoTop">
                <div className="profileInfoLeft">
                  <h2 className="profileInfoName">{user.name}</h2>
                  <p className="profileInfoUsername">
                    @{user.username} {user.user_role === "premium" && "· Premium"}
                  </p>
                  <div className="profileInfoDetails">
                    <div className="infoItem">
                      <Email className="infoIcon" />
                      <span>{user.email}</span>
                    </div>
                    <div className="infoItem">
                      <CalendarToday className="infoIcon" />
                      <span>Joined {new Date(user.date_created).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
              </div>

              {error && <div className="messageContainer errorMessage">{error}</div>}
              {success && <div className="messageContainer successMessage">{success}</div>}
              {uploading && <div className="messageContainer uploadingMessage">Uploading...</div>}

              <div className="profileTabs">
                {["posts", "photos"].map((tab) => (
                  <button
                    key={tab}
                    className={`tabButton ${activeTab === tab ? "active" : ""}`}
                    onClick={() => setActiveTab(tab)}
                  >
                    {tab === "posts" ? "Posts" : "Photos"}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="profileContentSection">
            {activeTab === "posts" && (
              <div className="profileContent">
                <Feed mine />
              </div>
            )}
            {activeTab === "photos" && (
              <div className="profileContent photosContent">
                <div className="photosGrid">
                  {photos.length === 0 && (
                    <div className="photoPlaceholder">
                      <PermMedia className="photoIcon" />
                      <p>No photos yet</p>
                    </div>
                  )}
                  {photos.map((p) => (
                    <img key={p.id} src={imageSrc(p.postpic)} alt="" style={{ width: "100%", borderRadius: 8 }} />
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="profileRightSidebar">
            <Rightbar profile />
          </div>
        </div>
      </div>
    </>
  );
}
