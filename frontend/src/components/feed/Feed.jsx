import "./feed.css"
import Post from "../post/Post"
import Share from "../share/Share"
import { Posts } from "../../helperData"
import { useState } from 'react'

export default function Feed() {
  const [posters] = useState(Posts)
  const [newPost, setNewPost] = useState('')
  const [image, setImage] = useState(null)

  const handlePostSubmit = (e) => {
    e.preventDefault()
    if (!newPost.trim() && !image) return
    
    const newPostObj = {
      id: posters.length + 1,
      desc: newPost,
      photo: image || '',
      date: new Date().toISOString().split('T')[0],
      userId: 1,
      like: 0,
      comment: 0,
      share: 0,
    }
    
    posters.unshift(newPostObj)
    setNewPost('')
    setImage(null)
  }

  return (
    <div className="feed">
      <div className="feedWrapper">
        <div className="share">
          <div className="shareWrapper">
            <div className="shareTop">
              <img 
                className="shareProfileImg" 
                src="https://randomuser.me/api/portraits/men/1.jpg" 
                alt="" 
              />
              <input
                placeholder="What's on your mind?"
                className="shareInput"
                value={newPost}
                onChange={(e) => setNewPost(e.target.value)}
              />
            </div>
            <hr className="shareHr" />
            <div className="shareBottom">
              <div className="shareOptions">
                <label htmlFor="file" className="shareOption">
                  <i className="fas fa-image shareIcon"></i>
                  <span className="shareOptionText">Photo</span>
                  <input
                    style={{ display: 'none' }}
                    type="file"
                    id="file"
                    accept=".png,.jpeg,.jpg"
                    onChange={(e) => {
                      const file = e.target.files[0]
                      const reader = new FileReader()
                      reader.onloadend = () => {
                        setImage(reader.result)
                      }
                      if (file) {
                        reader.readAsDataURL(file)
                      }
                    }}
                  />
                </label>
              </div>
              <button className="shareButton" onClick={handlePostSubmit}>
                Share
              </button>
            </div>
            {image && (
              <div className="shareImgContainer">
                <img className="shareImg" src={image} alt="" />
                <span className="shareCancelImg" onClick={() => setImage(null)}>
                  ✕
                </span>
              </div>
            )}
          </div>
        </div>
        
        {posters.map((p) => (
            <Post key={p.id} post={p} />
          ))}
        </div>
      </div>
    );
  }