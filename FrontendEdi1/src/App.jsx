// App.js
import React from "react";
import { Routes, Route } from "react-router-dom";
import Home from "./Components/Home";
import Login from "./Authentication/Login";
import Dashboard from "./Components/Dashboard";
import Navbar from "./Components/Navbar";
import PrivateRoute from "./Components/PrivateRoute";
import Archived from "./Components/Archived";
import Cookies from 'js-cookie';

function App() {
  const isAuthenticated = Cookies.get("editoken");
  return (
    <>
    {isAuthenticated && <Navbar/>}
    
    <Routes>
      <Route path="/" element={<><Home /></>} />
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={<><Dashboard /></>} />
      <Route path="/archived" element={<><Archived /></>} />


    </Routes>
    </>
  );
}

export default App;
