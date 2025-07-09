import React, { useEffect, useState } from "react";
import logo from "../assests/256 icon.png";
import { useParams, useNavigate } from "react-router-dom";
import { CgProfile } from "react-icons/cg";
import courseBanner from "../assests/coursebanner.png";

const CourseContent = () => {
  const token = sessionStorage.getItem("auth_token");
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [courseDetails, setCourseDetails] = useState(null);
  const [modules, setModules] = useState(null);
  const { courseid } = useParams();
  const [percentage, setPercentage] = useState("0");
  const fetchCourseContent = async (courseid) => {
    try {
      const response = await fetch(
        `http://localhost:8080/api/user_course_progress/courses/${courseid}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token }),
        }
      );
      const data = await response.json();
      if (response.ok) {
        // console.log("module:", data.modules);
        // console.log(data.courseDetails);
        setModules(data.modules);
        // console.log(data.modules);

        setCourseDetails(data.courseDetails);
        // setPercentage(data.percentage);
        setName(data.name);
        if (data.modules && data.modules.length > 0) {
          const totalPercentage = data.modules.reduce((sum, module) => {
            return sum + (module[3] || 0); // Add module percentage if not null
          }, 0);
          const totalModules = data.modules.length; // Use data.modules.length
          const coursePercentage = (totalPercentage / totalModules).toFixed(2);
          setPercentage(coursePercentage);
          console.log(coursePercentage, "percentage da");
        }
      } else {
        alert("try again");
      }
    } catch (error) {
      console.log(error, "msg:", error.message);
    }
  };
  useEffect(() => {
    if (courseid) {
      fetchCourseContent(courseid);
    }
    // eslint-disable-next-line
  }, [courseid]);

  const handleLogout = async () => {
    const token = sessionStorage.getItem("auth_token");
    const response = await fetch(
      "http://localhost:8080/api/authentication/logout",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token }),
        credentials: "include", // Include cookies with requests
      }
    );
    if (response.ok) {
      navigate("/");
      sessionStorage.removeItem("auth_token");
    } else {
      alert("try again");
    }
  };
  return (
    <div className="flex flex-col justify-center">
      <header className="flex flex-row justify-around items-center pt-10">
        <div className="flex flex-row items-center">
          <img src={logo} alt="" srcSet="" className="size-16 m-2" />
          <div className="flex flex-col p-2 font-koulen">
            <p className="flex items-end text-4xl  text-primary">UPSKILL</p>
            <p className="flex items-start text-2xl  text-red-500">vision</p>
          </div>
        </div>
        <div className="flex flex-row">
          {" "}
          <div className="flex flex-row items-center">
            <p className="font-koulen text-xl">{name}</p>
            <CgProfile className="size-9 px-1" />
          </div>
          <button
            onClick={handleLogout}
            className="m-2 text-lg text-red-500 border-2 border-red-500 hover:text-white hover:bg-red-500 transition-all duration-300 h-max px-2 py-1 rounded-lg"
          >
            Logout
          </button>
        </div>
      </header>
      <main className="flex flex-col text-justify w-3/5 items-center justify-center self-center py-20">
        <div className="flex flex-col text-left self-start pb-10">
          <p className="font-bold text-blue-700 text-xl">Hii, {name} Welcome</p>
          <p className="text-primary">Lets learn something new today</p>
        </div>
        <div className="flex flex-col">
          {courseDetails && (
            <>
              <p>
                <span className="text-primary">Course Name:</span>
                {courseDetails[1]}
              </p>
              <p>
                <span className="text-primary">Instructor:</span>
                {courseDetails[3]}
              </p>
              <p>
                <span className="text-primary">Description:</span>
                {courseDetails[2]}
              </p>
              <p className="flex flex-row">
                <span className="text-primary">Introduction:</span>
                <span>{courseDetails[7]}</span>
              </p>
              <div className="flex flex-row">
                <p className="text-primary">Course Duration:</p>
                <div>
                  <p>
                    <span>Start Date:</span>
                    {courseDetails[4]}
                  </p>
                  <p>
                    <span>End Date:</span>
                    {courseDetails[5]}
                  </p>
                  <p>
                    <span>Duration:</span>
                    {courseDetails[6]} days
                  </p>
                </div>
              </div>
              <div className="flex flex-row items-center">
                <p className="text-primary">Progress :</p>

                <div className="w-3/5 h-2 bg-gray-200 rounded-lg overflow-hidden relative border border-gray-300 mx-2">
                  <div
                    className="h-full bg-green-500"
                    style={{ width: `${percentage}%` }} // Hardcoded 50% for testing
                  ></div>
                </div>
                <p>{percentage} %</p>
              </div>
            </>
          )}
        </div>
        <div className="flex flex-row p-3">
          {modules &&
            modules.map((item, index) => (
              <div
                key={index}
                className="w-1/3 m-2 p-2 border-2 shadow-xl rounded-xl relative cursor-pointer"
                onClick={() =>
                  window.open(
                    `http://localhost:3000/dashboard/view-module/${courseDetails[0]}?id=${item[0]}&t=${token}`,
                    "_blank"
                  )
                }
              >
                <img src={courseBanner} alt="" srcSet="" />
                <p className="bg-gray-300 text-white shadow-lg rounded-full text-center w-2/5 absolute left-5 ">
                  Lectures
                </p>
                <p className="pt-6">
                  <strong>Title:</strong>
                  {item[1]}
                </p>
                <p>
                  <strong>Status:</strong> {item[4] || "Not Started"}
                </p>
                <p>
                  <strong>Progress:</strong> {item[3] || 0}%
                </p>
                <div className="w-full bg-gray-200 rounded-full h-2 relative my-2">
                  <div
                    className="bg-primary h-full rounded-full transition-all duration-500 ease-in-out"
                    style={{ width: `${item[3] || 0}%` }}
                  ></div>
                </div>
              </div>
            ))}
        </div>
      </main>
    </div>
  );
};

export default CourseContent;
