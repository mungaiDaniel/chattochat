import React, { useState } from "react";
import axios from "axios";
import "../login/login.css";
import logo from "../login/logo.jpg";
import { Icon } from "@iconify/react";
import { Link } from "react-router-dom";
import {
  IconButton,
  InputAdornment,
  TextField
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import Topbar from "../../components/topbar/Topbar";

const initialState = {
  name: "",
  username: "",
  email: "",
  password: ""
};

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
    setSuccess(false);
    try {
      const res = await axios.post("http://127.0.0.1:5000/api/v1/register", form);
      setSuccess(true);
      setForm(initialState);
      alert("Registration successful!");
      setTimeout(() => {
        navigate("/login");
      }, 1500);
    } catch (err) {
      setError(
        err.response?.data?.message ||
        "Registration failed. Please check your input."
      );
      setSuccess(false);
    }
  };

  return (
    <>
      <Topbar/>
      <div className="login">
        <div className="loginWrapper container">
          <div className="loginLeft">
            <img src={logo} alt="" className="logopic"/>
            <h3 className="loginLogo">Chat to Chats</h3>
            <span className="loginDesc">
              Chat to chat with your friends
            </span>
          </div>
          <div className="loginRight">
            <div className="loginBox" style={{ height: "400px" }}>
              <TextField 
                placeholder="Name"
                type="text"
                className="loginInput"
                name="name"
                value={form.name}
                onChange={handleChange}
                required
              />
              <TextField 
                placeholder="Username"
                type="text"
                className="loginInput"
                name="username"
                value={form.username}
                onChange={handleChange}
                required
              />
              <TextField 
                placeholder="Email"
                type="email"
                className="loginInput"
                name="email"
                value={form.email}
                onChange={handleChange}
                required
              />
              <TextField 
                placeholder="Password" 
                type={showPassword ? "text" : "password"}
                className="loginInput"
                name="password"
                value={form.password}
                onChange={handleChange}
                required
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword((prev) => !prev)}
                      >
                        {showPassword ? (
                          <Icon icon="eva:eye-fill" />
                        ) : (
                          <Icon icon="eva:eye-off-fill" />
                        )}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              <button className="loginButton" type="submit" onClick={handleSubmit}>
                Register
              </button>
              <div style={{ marginTop: "12px", textAlign: "center" }}>
                <Link to="/login">Already have an account? Login</Link>
                {error && <div style={{color: "red", marginBottom: "10px", marginTop: "10px"}}>{error}</div>}
                {success && <div style={{color: "green", marginBottom: "10px", marginTop: "10px"}}>Registration successful!</div>}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Register;