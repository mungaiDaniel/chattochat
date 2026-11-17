import "./comments.css";
import { Link, useSearchParams } from "react-router-dom";
import Topbar from "../../components/topbar/Topbar";
import ShareComments from "../../components/shareComments/ShareComments";
import OnePost from "./OnePost";
import useFetch from "../../hooks/useFetch";
import { api } from "../../api";
import { formatDate, imageSrc } from "../../utils/media";

const Comments = () => {
  const [params] = useSearchParams();
  const postId = params.get("id");
  const { data: post, error, loading, reload } = useFetch(() => api.getPost(postId), [postId]);

  return (
    <>
      <Topbar />
      <div className="container mt-3">
        <Link to="/home">&larr; Back to feed</Link>
      </div>
      {loading && <h2>Loading...</h2>}
      {error && <div className="alert alert-danger m-3">{error}</div>}
      {post && (
        <>
          <OnePost post={post} />
          <ShareComments postId={postId} onPosted={reload} />
          {post.comments.map((comment) => (
            <div className="post" key={comment.id}>
              <div className="postWrapper">
                <div className="postTop">
                  <div className="postTopLeft">
                    <img className="postProfileImg" src={imageSrc(comment.author.personPic)} alt="" />
                    <span className="postUsername">{comment.author.name}</span>
                    <span className="postDate">{formatDate(comment.date_created)}</span>
                  </div>
                </div>
                <div className="postCenter">
                  <span className="postText">{comment.body}</span>
                </div>
              </div>
            </div>
          ))}
        </>
      )}
    </>
  );
};

export default Comments;
