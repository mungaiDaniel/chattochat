import "./login.css";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { IconButton, InputAdornment, TextField } from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import logo from "./logo.jpg";
import Topbar from "../../components/topbar/Topbar";
import { api, DEMO_MODE } from "../../api";
import { useAuth } from "../../context/AuthContext";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { signIn } = useAuth();
  const navigate = useNavigate();

  const run = async (request) => {
    setBusy(true);
    setError("");
    try {
      await signIn(await request());
      navigate("/home");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const onSubmit = (e) => {
    e.preventDefault();
    run(() => api.login({ username, password }));
  };

  return (
    <>
      <Topbar />
      <div className="login">
        <div className="loginWrapper container">
          <div className="loginLeft">
            <img src={logo} alt="" className="logopic" />
            <h3 className="loginLogo">Chat to Chats</h3>
            <span className="loginDesc">Chat to chat with your friends</span>
          </div>
          <div className="loginRight">
            <form className="loginBox" onSubmit={onSubmit}>
              <TextField
                placeholder="Username or email"
                className="loginInput"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
                required
              />
              <TextField
                placeholder="Password"
                type={showPassword ? "text" : "password"}
                className="loginInput"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="Toggle password visibility"
                        onClick={() => setShowPassword((prev) => !prev)}
                      >
                        {showPassword ? <Visibility /> : <VisibilityOff />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              <button className="loginButton" type="submit" disabled={busy}>
                Log In
              </button>
              {DEMO_MODE && (
                <button
                  className="loginButton"
                  type="button"
                  disabled={busy}
                  style={{ background: "#2e9e6b" }}
                  onClick={() => run(() => api.demoLogin())}
                >
                  Try Demo
                </button>
              )}
              <div style={{ marginTop: "12px", textAlign: "center" }}>
                <Link to="/register">Don't have an account? Register</Link>
                {error && <div style={{ color: "red", marginTop: "10px" }}>{error}</div>}
              </div>
            </form>
          </div>
        </div>
      </div>
    </>
  );
}
