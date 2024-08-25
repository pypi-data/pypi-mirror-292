import React from 'react';
import {createBrowserRouter} from "react-router-dom";
import {RouterProvider} from "react-router";
import Home from "./routes/Home";
import Error from "./routes/Error";

declare global {
  interface Window {
    DATA: any;
  }
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <Home/>,
    index: true,
    errorElement: <Error/>
  },
])

export default function App() {
  return (
    <RouterProvider router={router}/>
  )
}
