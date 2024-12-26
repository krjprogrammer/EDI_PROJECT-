import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import Cookies from "js-cookie";
import Login from "../Authentication/Login";

const PrivateRoute = ({children}) => {
  const isAuthenticated = Cookies.get("editoken"); // Adjust based on your authentication mechanism
// console.log("isAuthenticated", isAuthenticated);
  if (isAuthenticated !== undefined) {
    return children;
  }

  return <Navigate to="/login" />;
};

export default PrivateRoute;
