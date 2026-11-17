import "../login/login.css";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { IconButton, InputAdornment, TextField } from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import logo from "../login/logo.jpg";
import Topbar from "../../components/topbar/Topbar";
import { api } from "../../api";

const initialState = { name: "", username: "", email: "", password: "" };

const Register = () => {
  const [form, setForm] = useState(initialState);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.register(form);
      setSuccess(true);
      setForm(initialState);
      setTimeout(() => navigate("/login"), 1200);
    } catch (err) {
      setSuccess(false);
      setError(err.message);
    }
  };

  const field = (name, placeholder, type = "text", extra = {}) => (
    <TextField
      placeholder={placeholder}
      type={type}
      className="loginInput"
      name={name}
      value={form[name]}
      onChange={handleChange}
      required
      {...extra}
    />
  );

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
            <form className="loginBox" style={{ height: "auto", minHeight: "400px" }} onSubmit={handleSubmit}>
              {field("name", "Name")}
              {field("username", "Username")}
              {field("email", "Email", "email")}
              {field("password", "Password (min. 8 characters)", showPassword ? "text" : "password", {
                inputProps: { minLength: 8 },
                InputProps: {
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
                },
              })}
              <button className="loginButton" type="submit">
                Register
              </button>
              <div style={{ marginTop: "12px", textAlign: "center" }}>
                <Link to="/login">Already have an account? Login</Link>
                {error && <div style={{ color: "red", marginTop: "10px" }}>{error}</div>}
                {success && <div style={{ color: "green", marginTop: "10px" }}>Registration successful!</div>}
              </div>
            </form>
          </div>
        </div>
      </div>
    </>
  );
};

export default Register;
