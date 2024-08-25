import React from 'react';
import axios from "axios";

export default function Page() {
  const data = window.DATA || {};

  console.log('Data from server:', data);  // Add this line for debugging

  const handleClick = () => {
    axios.post(`/analytics/click`, {
      button_name: 'hero#coming-soon',
    }).then(response => {
      console.log('Response:', response)
    }).catch(error => {
      console.error('Error:', error);
    }).finally(() => {
      console.log('Click finished.')
    })
  }

  return (
    <>
      <div className={"w-full min-h-screen"}>
        <section
          id={"hero"}
          className="flex flex-col min-w-full min-h-screen items-center justify-center"
        >
          <div className="flex flex-col absolute inset-0 z-10 items-center justify-center">
            <div className="flex mb-8 justify-center">
              <img
                src={"/public/logo512.png"}
                alt={"Pegasus"}
                width={512}
                height={512}
                className={"rounded-xl"}
              />
            </div>

            <button
              id={"coming-soon"}
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-full text-lg border-solid border-white transition duration-300"
              onClick={handleClick}
            >
              Get Started!
            </button>
          </div>
        </section>
      </div>
    </>
  );
};