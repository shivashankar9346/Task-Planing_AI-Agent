import React from "react";
import { Link } from "react-router-dom";
import "./Home.css";

const Home = () => {
  return (
    <div className="home-container">
      <nav className="home-nav">
        <div className="home-logo">
          TASK PLANING AI AGENT</div>
        <div className="home-nav-links">
          <Link to="/login" className="primary-btn">Login</Link>
          <Link to="/register" className="primary-btn">
            Register
          </Link>
        </div>
      </nav>

      <div className="home-content">
        <h1>Do you want to plan any goals?</h1>

        <div className="home-actions">
          <Link to="/register" className="primary-btn">
            Create Account
          </Link>
          <Link to="/login" className="secondary-btn">
            Login
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home;
