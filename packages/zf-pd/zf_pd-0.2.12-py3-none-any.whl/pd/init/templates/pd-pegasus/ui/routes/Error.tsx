import React from "react";
import {useRouteError} from "react-router-dom";

export default function Page() {
  const error: any = useRouteError();
  console.error(error);

  return (
    <div
      id="error-page"
      className={"flex flex-col items-center justify-center min-h-screen text-center"}
    >
      <img src="/public/lost.gif" alt="404" width={500} height={251}/>
      <a
        href="/"
        className="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-6 rounded-full text-lg transition duration-300 mt-8"
      >
        Take me back
      </a>
    </div>
  );
}