import React, { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import "./login.css";

export default function Login() {
  const [form, setForm] = useState({
    username: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    // 🔒 Frontend validation
    if (!form.username || !form.password) {
      alert("Please enter username and password");
      return;
    }

    try {
      setLoading(true);

      const res = await axios.post(
        "http://localhost:8000/login",
        form,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      console.log("LOGIN RESPONSE:", res.data);

      // ✅ Must exist
      if (!res.data.access_token) {
        throw new Error("Token missing in response");
      }

      localStorage.setItem("token", res.data.access_token);
      navigate("/chat");

    } catch (err) {
      console.error("LOGIN ERROR:", err.response || err);

      alert(
        err.response?.data?.detail ||
        err.message ||
        "Login failed"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleLogin} className="login-card">
        <h2 className="login-title">Login</h2>

        <input
          className="login-input"
          placeholder="Username"
          value={form.username}
          onChange={(e) =>
            setForm({ ...form, username: e.target.value })
          }
          required
        />

        <input
          className="login-input"
          type="password"
          placeholder="Password"
          value={form.password}
          onChange={(e) =>
            setForm({ ...form, password: e.target.value })
          }
          required
        />

        <button
          type="submit"
          className="login-button"
          disabled={loading}
        >
          {loading ? "Logging in..." : "Login"}
        </button>

        <p className="login-footer">
          New here?{" "}
          <Link to="/register" className="login-link">
            Register
          </Link>
        </p>
      </form>
    </div>
  );
}
