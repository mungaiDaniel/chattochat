import React, { useState, useEffect } from 'react'
import axios from 'axios'
import Topbar from '../../components/topbar/Topbar'
import jwt_decode from 'jwt-decode'
import './follow.css'

const Follow = () => {
    const [users, setUsers] = useState([])
    const [isLoading, setIsLoading] = useState(true)
    const [currentUserId, setCurrentUserId] = useState(null)
    const [following, setFollowing] = useState({}) // { userId: true/false }

    useEffect(() => {
        // Fetch all users
        axios.get("http://127.0.0.1:5000/api/v1/user")
            .then((response) => {
                setUsers(response.data.data)
                setIsLoading(false)
            })

        // Decode JWT to get current user's id
        const token = localStorage.getItem("token")
        if (token) {
            try {
                const decoded = jwt_decode(token)
                setCurrentUserId(decoded.sub || decoded.id || decoded.user_id || decoded.identity)
            } catch {
                setCurrentUserId(null)
            }
        }
    }, [])

    const handleFollow = async (userId) => {
        const token = localStorage.getItem("token")
        try {
            await axios.post(
                `http://127.0.0.1:5000/api/v1/follow/${userId}`,
                {},
                { headers: { Authorization: `Bearer ${token}` } }
            )
            setFollowing(prev => ({ ...prev, [userId]: true }))
        } catch (err) {
            alert(err.response?.data?.message || "Failed to follow user")
        }
    }

    const handleUnfollow = async (userId) => {
        const token = localStorage.getItem("token")
        try {
            await axios.post(
                `http://127.0.0.1:5000/api/v1/unfollow/${userId}`,
                {},
                { headers: { Authorization: `Bearer ${token}` } }
            )
            setFollowing(prev => ({ ...prev, [userId]: false }))
        } catch (err) {
            alert(err.response?.data?.message || "Failed to unfollow user")
        }
    }

    if (isLoading) {
        return <h2>Loading....</h2>
    }

    return (
        <>
            <Topbar />
            {users.map((user) => {
                // Hide follow/unfollow button for self
                if (currentUserId && user.id === currentUserId) {
                    return null
                }
                const isFollowing = following[user.id] || false
                return (
                    <div className='postr container' key={user.id}>
                        <div className="postTopr">
                            <div className="postTopLeftr">
                                <img
                                    className="postProfileImgr"
                                    src={user.personPic || "https://via.placeholder.com/150"}
                                    alt=""
                                />
                                <span className="postUsernamer">
                                    {user.name}
                                </span>
                                <span className="postDater">{user.date_created}</span>
                            </div>
                            <div className="postTopRightr">
                                {isFollowing ? (
                                    <button className="btn" onClick={() => handleUnfollow(user.id)}>
                                        Unfollow
                                    </button>
                                ) : (
                                    <button className="btn" onClick={() => handleFollow(user.id)}>
                                        Follow
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                )
            })}
        </>
    )
}

export default Follow