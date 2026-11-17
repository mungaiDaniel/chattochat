import "./rightbar.css";
import { Users } from "../../helperData";
import Online from "../online/Online";
import { Cake } from "@material-ui/icons";
import React, { useState , useEffect } from 'react'
import axios from 'axios'

export default function Rightbar({ profile }) {

  const[users, setUser] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
      axios.get("http://127.0.0.1:5000/api/v1/user")
      .then((response) =>{
      setUser(response.data.data)
      setIsLoading(false)
      })
  }, [])
  if (isLoading){
    return <h2>Loading....</h2>
}
  const HomeRightbar = () => {
    return (
      <>
        <div className="birthdayContainer">
          <Cake className="birthdayImg" />
          <span className="birthdayText">
            <b>Pola Foster</b> and <b>3 other friends</b> have a birhday today.
          </span>
        </div>
        <img className="rightbarAd" src="assets/ad.png" alt="" />
        <h4 className="rightbarTitle">Online Friends</h4>
        <ul className="rightbarFriendList">
          {users.map((u) => (
            <Online key={u.id} user={u} />
          ))}
        </ul>
      </>
    );
  };

  const ProfileRightbar = () => {
    const getImageUrl = (imagePath) => {
      if (!imagePath) return "https://via.placeholder.com/150";
      // If it's already a full URL, return it
      if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
        return imagePath;
      }
      // If it's a filename, construct the full URL
      if (imagePath.startsWith('uploads/') || !imagePath.includes('/')) {
        return `http://127.0.0.1:5000/uploads/${imagePath.replace('uploads/', '')}`;
      }
      return imagePath;
    };

    return (
      <>
        <h4 className="rightbarTitle">User friends</h4>
        <div className="rightbarFollowings">
          {
            users.map((user) =>{
              return  <div key={user.id} className="rightbarFollowing">
              <img
                src={getImageUrl(user.personPic)}
                alt={user.name || "User"}
                className="rightbarFollowingImg"
                onError={(e) => {
                  e.target.src = "https://via.placeholder.com/150";
                }}
              />
              <span className="rightbarFollowingName">{user.name || user.username || "User"}</span>
            </div>
          
            })
          }
          </div>
         
      </>
    );
  };
  return (
    <div className="rightbar">
      <div className="rightbarWrapper">
        {profile ? <ProfileRightbar /> : <HomeRightbar />}
      </div>
    </div>
  );
}