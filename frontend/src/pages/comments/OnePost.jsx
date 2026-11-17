import "./comments.css";
import { formatDate, imageSrc } from "../../utils/media";

// The post a comment thread belongs to.
const OnePost = ({ post }) => (
  <div className="post">
    <div className="postWrapper">
      <div className="postTop">
        <div className="postTopLeft">
          <img className="postProfileImg" src={imageSrc(post.author.personPic)} alt="" />
          <span className="postUsername">{post.author.name}</span>
          <span className="postDate">{formatDate(post.date_created)}</span>
        </div>
      </div>
      <div className="postCenter">
        <span className="postText">{post.body}</span>
        {post.postpic && <img className="postImg" src={imageSrc(post.postpic)} alt="" />}
      </div>
    </div>
  </div>
);

export default OnePost;
