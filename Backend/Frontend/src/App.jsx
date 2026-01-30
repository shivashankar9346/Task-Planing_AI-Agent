import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Home from './Pages/Home'
import Register from './Pages/Register';
import Login from './Pages/Login';
import Chat from './Components/Chat';

function App() {
  // We keep this check for the Protected Route
  const isAuthenticated = () => !!localStorage.getItem("token");

  return (
    <Router>
      <Routes>
        {/* 1. Default Route is now the Home Page */}
        <Route path="/" element={<Home />} />

        {/* 2. Authentication Routes */}
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />

        {/* 3. Protected Chat Route */}
        <Route
          path="/chat"
          element={localStorage.getItem("token") ? <Chat /> : <Navigate to="/login" />}
        />

        {/* 4. Catch-all: Redirect unknown paths to Home */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;