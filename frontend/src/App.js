import { Navigate, Route, Routes } from "react-router-dom";
import DemoBanner from "./components/demoBanner/DemoBanner";
import Payrol from "./components/payrol/Payrol";
import Comments from "./pages/comments/Comments";
import Follow from "./pages/follow/Follow";
import Home from "./pages/home/Home";
import Login from "./pages/login/Login";
import MyPost from "./pages/myPost/MyPost";
import Profile from "./pages/profile/Profile";
import Register from "./pages/register/Register";

function App() {
  return (
    <>
      <DemoBanner />
      <Routes>
        <Route path="/" element={<Navigate to="/home" replace />} />
        <Route path="/home" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/mypost" element={<MyPost />} />
        <Route path="/follow" element={<Follow />} />
        <Route path="/comments" element={<Comments />} />
        <Route path="/upgrade" element={<Payrol />} />
        <Route path="*" element={<Navigate to="/home" replace />} />
      </Routes>
    </>
  );
}

export default App;
