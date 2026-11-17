import "./payrol.css";
import { useState } from "react";
import { Navigate } from "react-router-dom";
import Topbar from "../topbar/Topbar";
import { api } from "../../api";
import { useAuth } from "../../context/AuthContext";

// Simulated plan change: the API flips the role directly, no real payment is taken.
const Payrol = () => {
  const { user, ready, refresh } = useAuth();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ text: "", error: false });

  if (!ready) return <h2>Loading...</h2>;
  if (!user) return <Navigate to="/login" replace />;

  const isPremium = user.user_role === "premium";

  const change = async () => {
    setLoading(true);
    setMessage({ text: "", error: false });
    try {
      await api.upgradeRole(isPremium ? "user" : "premium");
      await refresh();
      setMessage({ text: isPremium ? "Switched back to the free plan." : "You are now a premium user!", error: false });
    } catch (err) {
      setMessage({ text: err.message, error: true });
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Topbar />
      <div className="container payrol">
        <h2 className="h2">Plan: {isPremium ? "Premium" : "Free"}</h2>
        <p>This is a simulated upgrade. No payment details are collected.</p>
        {message.text && <p style={{ color: message.error ? "#c62828" : "#2e7d32" }}>{message.text}</p>}
        <button className="btn" onClick={change} disabled={loading}>
          {loading ? "Processing..." : isPremium ? "Downgrade" : "Upgrade now"}
        </button>
      </div>
    </>
  );
};

export default Payrol;
