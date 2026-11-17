import "./profile.css";
import Topbar from "../../components/topbar/Topbar";
import Sidebar from "../../components/sidebar/Sidebar";
import Feed from "../../components/feed/Feed";
import Rightbar from "../../components/rightbar/Rightbar";
import { useState, useEffect } from "react";
import axios from "axios";
import { PermMedia, Edit, LocationOn, Email, Person, CalendarToday } from "@material-ui/icons";

export default function Profile() {
  const [user, setUser] = useState(null);
  const [profilePic, setProfilePic] = useState("");
  const [coverPic, setCoverPic] = useState("");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [activeTab, setActiveTab] = useState("posts");

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;
      
      const response = await axios.get("http://127.0.0.1:5000/api/v1/user", {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      if (response.data.data && response.data.data.length > 0) {
        let currentUser = response.data.data[0];
        try {
          const tokenData = JSON.parse(atob(token.split('.')[1]));
          currentUser = response.data.data.find(u => 
            u.id === tokenData.sub || 
            u.id === tokenData.id || 
            u.id === tokenData.user_id ||
            u.username === tokenData.username
          ) || response.data.data[0];
        } catch (e) {
          console.log("Could not decode token, using first user");
        }
        
        setUser(currentUser);
        // Handle profile picture URL
        const profilePicUrl = currentUser.personPic || "";
        if (profilePicUrl && !profilePicUrl.startsWith('http://') && !profilePicUrl.startsWith('https://')) {
          setProfilePic(`http://127.0.0.1:5000/uploads/${profilePicUrl.replace('uploads/', '')}`);
        } else {
          setProfilePic(profilePicUrl);
        }
        // Handle cover picture URL
        const coverPicUrl = currentUser.coverPic || "";
        if (coverPicUrl && !coverPicUrl.startsWith('http://') && !coverPicUrl.startsWith('https://')) {
          setCoverPic(`http://127.0.0.1:5000/uploads/${coverPicUrl.replace('uploads/', '')}`);
        } else {
          setCoverPic(coverPicUrl);
        }
      }
    } catch (err) {
      console.error("Error fetching user data:", err);
    }
  };

  const validateFile = (file) => {
    const validTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp'];
    const validExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp'];
    
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    const isValidType = validTypes.includes(file.type);
    const isValidExtension = validExtensions.includes(fileExtension);
    
    if (!isValidType || !isValidExtension) {
      setError("Please upload a valid image file (png, jpg, jpeg, gif, or webp)");
      setTimeout(() => setError(""), 5000);
      return false;
    }
    
    // Removed file size limit - accepts any size
    return true;
  };

  const updateUserProfile = async (field, value) => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.put(
        "http://127.0.0.1:5000/api/v1/user/profile",
        { [field]: value },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      return response.data;
    } catch (err) {
      console.error("Error updating profile:", err);
      throw err;
    }
  };

  const handleProfilePicUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!validateFile(file)) {
      return;
    }

    setUploading(true);
    setError("");
    setSuccess("");

    try {
      // Step 1: Upload the photo file
      const formData = new FormData();
      formData.append('photo', file);

      const token = localStorage.getItem("token");
      const uploadResponse = await axios.post(
        "http://127.0.0.1:5000/api/v1/upload-photo",
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      // Step 2: Get the filename from upload response
      const filename = uploadResponse.data.filename;
      const imageUrl = `http://127.0.0.1:5000/uploads/${filename}`;
      
      // Step 3: Update user profile with the profile picture URL
      await updateUserProfile('personPic', filename);
      
      // Step 4: Update local state and refresh user data
      setProfilePic(imageUrl);
      setUser(prev => prev ? { ...prev, personPic: filename } : prev);
      
      // Step 5: Refresh user data to get latest from backend
      await fetchUserData();
      
      setSuccess("Profile picture uploaded and saved successfully!");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err.response?.data?.message || "Failed to upload profile picture");
      console.error("Upload error:", err);
    } finally {
      setUploading(false);
    }
  };

  const handleCoverPicUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!validateFile(file)) {
      return;
    }

    setUploading(true);
    setError("");
    setSuccess("");

    try {
      // Step 1: Upload the photo file
      const formData = new FormData();
      formData.append('photo', file);

      const token = localStorage.getItem("token");
      const uploadResponse = await axios.post(
        "http://127.0.0.1:5000/api/v1/upload-photo",
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      // Step 2: Get the filename from upload response
      const filename = uploadResponse.data.filename;
      const imageUrl = `http://127.0.0.1:5000/uploads/${filename}`;
      
      // Step 3: Update user profile with the cover picture URL
      await updateUserProfile('coverPic', filename);
      
      // Step 4: Update local state and refresh user data
      setCoverPic(imageUrl);
      setUser(prev => prev ? { ...prev, coverPic: filename } : prev);
      
      // Step 5: Refresh user data to get latest from backend
      await fetchUserData();
      
      setSuccess("Cover photo uploaded and saved successfully!");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err.response?.data?.message || "Failed to upload cover photo");
      console.error("Upload error:", err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <>
      <Topbar />
      <div className="profile">
        <Sidebar />
        <div className="profileRight">
          {/* Cover Photo Section */}
          <div className="profileCoverSection">
            <div className="profileCoverContainer">
              <img
                className="profileCoverImg"
                src={coverPic || "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200&h=400&fit=crop"}
                alt="Cover"
              />
              <div className="coverOverlay"></div>
              <label htmlFor="coverPicInput" className="coverPicUploadBtn">
                <Edit className="uploadIcon" />
                <span>Edit Cover Photo</span>
              </label>
              <input
                id="coverPicInput"
                type="file"
                accept="image/png,image/jpg,image/jpeg,image/gif,image/webp"
                onChange={handleCoverPicUpload}
                style={{ display: 'none' }}
                disabled={uploading}
              />
            </div>

            {/* Profile Picture Section */}
            <div className="profilePictureSection">
              <div className="profilePictureContainer">
                <img
                  className="profileUserImg"
                  src={profilePic || "https://via.placeholder.com/200"}
                  alt="Profile"
                />
                <label htmlFor="profilePicInput" className="profilePicUploadBtn">
                  <PermMedia className="uploadIcon" />
                </label>
                <input
                  id="profilePicInput"
                  type="file"
                  accept="image/png,image/jpg,image/jpeg,image/gif,image/webp"
                  onChange={handleProfilePicUpload}
                  style={{ display: 'none' }}
                  disabled={uploading}
                />
              </div>
            </div>
          </div>

          {/* User Info Section */}
          <div className="profileInfoSection">
            <div className="profileInfoContainer">
              <div className="profileInfoTop">
                <div className="profileInfoLeft">
                  <h2 className="profileInfoName">{user?.name || "User Name"}</h2>
                  <p className="profileInfoUsername">@{user?.username || "username"}</p>
                  <div className="profileInfoDetails">
                    <div className="infoItem">
                      <Email className="infoIcon" />
                      <span>{user?.email || "user@example.com"}</span>
                    </div>
                    {user?.location && (
                      <div className="infoItem">
                        <LocationOn className="infoIcon" />
                        <span>{user.location}</span>
                      </div>
                    )}
                    <div className="infoItem">
                      <CalendarToday className="infoIcon" />
                      <span>Joined {user?.date_created ? new Date(user.date_created).toLocaleDateString() : "Recently"}</span>
                    </div>
                  </div>
                </div>
                <div className="profileInfoRight">
                  <button className="editProfileBtn">
                    <Edit className="editIcon" />
                    <span>Edit Profile</span>
                  </button>
                </div>
              </div>

              {/* Status Messages */}
              {error && (
                <div className="messageContainer errorMessage">
                  <span>{error}</span>
                </div>
              )}
              {success && (
                <div className="messageContainer successMessage">
                  <span>{success}</span>
                </div>
              )}
              {uploading && (
                <div className="messageContainer uploadingMessage">
                  <span>Uploading...</span>
                </div>
              )}

              {/* Tabs */}
              <div className="profileTabs">
                <button 
                  className={`tabButton ${activeTab === "posts" ? "active" : ""}`}
                  onClick={() => setActiveTab("posts")}
                >
                  Posts
                </button>
                <button 
                  className={`tabButton ${activeTab === "about" ? "active" : ""}`}
                  onClick={() => setActiveTab("about")}
                >
                  About
                </button>
                <button 
                  className={`tabButton ${activeTab === "photos" ? "active" : ""}`}
                  onClick={() => setActiveTab("photos")}
                >
                  Photos
                </button>
              </div>
            </div>
          </div>

          {/* Content Section */}
          <div className="profileContentSection">
            {activeTab === "posts" && (
              <div className="profileContent">
                <Feed />
              </div>
            )}
            {activeTab === "about" && (
              <div className="profileContent aboutContent">
                <div className="aboutCard">
                  <h3>About</h3>
                  <p className="aboutText">
                    {user?.bio || "Welcome to my profile! This is where I share my thoughts and connect with friends."}
                  </p>
                </div>
                <div className="aboutCard">
                  <h3>Contact Information</h3>
                  <div className="contactInfo">
                    <div className="contactItem">
                      <Email className="contactIcon" />
                      <span>{user?.email || "user@example.com"}</span>
                    </div>
                    {user?.phone && (
                      <div className="contactItem">
                        <Person className="contactIcon" />
                        <span>{user.phone}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
            {activeTab === "photos" && (
              <div className="profileContent photosContent">
                <div className="photosGrid">
                  <div className="photoPlaceholder">
                    <PermMedia className="photoIcon" />
                    <p>No photos yet</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Sidebar */}
          <div className="profileRightSidebar">
            <Rightbar profile/>
          </div>
        </div>
      </div>
    </>
  );
}
