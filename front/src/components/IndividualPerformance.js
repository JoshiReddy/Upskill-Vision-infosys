import React, { useState, useEffect } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
// import { Line } from "react-chartjs-2";
import { useParams } from "react-router-dom";
const IndividualPerformance = () => {
  const [selectedCourse, setSelectedCourse] = useState({});
  const { token, userId } = useParams();
  //   console.log(token, userId);

  //   const [progressData, setProgressData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
  );
  const [resData, setResData] = useState({});
  //   const options = {
  //     responsive: true,
  //     plugins: {
  //       legend: {
  //         display: false,
  //       },
  //       title: {
  //         display: true,
  //         text: "Quiz Performance",
  //       },
  //     },
  //   };

  //   const labels = ["Quiz 1", "Quiz 2", "Quiz 3", "Quiz 4"];
  //   const data = {
  //     labels,
  //     datasets: [
  //       {
  //         label: "Marks",
  //         data: [45, 78, 65, 89], // Example data for Marks
  //         borderColor: "rgb(75, 192, 192)",
  //         backgroundColor: "rgba(75, 192, 192, 0.5)",
  //         pointStyle: "circle",
  //         pointRadius: 8,
  //         pointHoverRadius: 10,
  //       },
  //     ],
  //   };
  useEffect(() => {
    // Fetch progress data from the Flask API
    const fetchProgressData = async () => {
      try {
        const response = await fetch(
          "http://localhost:8080/api/all_users_list/user-progress",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              token: token,
              userId: userId,
            }),
          }
        );
        if (!response.ok) {
          throw new Error("Failed to fetch data");
        }
        const data = await response.json();
        // console.log(data);
        setResData(data);
        // setProgressData(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchProgressData();
  }, [token, userId]);
  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  const PerformanceOverview = ({ resData }) => {
    const calculateOverallPercentage = (completedModules, totalModules) => {
      if (totalModules === 0) {
        return 0;
      }
      return (completedModules / totalModules) * 100;
    };
    const totalPercentage = resData.reduce((acc, course) => {
      return (
        acc +
        calculateOverallPercentage(
          parseInt(course.completed_modules),
          parseInt(course.total_modules)
        )
      );
    }, 0);

    const percentage = parseInt(totalPercentage) / parseInt(resData.length);
    // const  = 10; // Use overall completion for the circle chart
    const strokeDasharray = `${percentage}, 100`; // Dynamic progress

    return (
      <div className="w-full mx-auto bg-white shadow-lg rounded-2xl">
        <div className="bg-blue-500 text-white text-center py-4 rounded-b-full">
          <h1 className="text-3xl font-bold py-2">
            Individual Performance Overview
          </h1>
        </div>

        <div className="flex justify-around py-6">
          <div
            // key={index}
            className="w-2/12 text-center bg-gray-100 p-4 rounded-xl shadow-md items-center"
          >
            <p className="text-gray-600">Courses Enrolled</p>
            <h2 className="text-4xl font-bold text-gray-800">
              {resData.length}
            </h2>
          </div>
          <div
            // key={index}
            className="w-2/12 text-center bg-gray-100 p-4 rounded-xl shadow-md items-center"
          >
            <p className="text-gray-600">Active Courses</p>
            <h2 className="text-4xl font-bold text-gray-800">
              {resData.length}
            </h2>
          </div>
          <div
            // key={index}
            className="w-2/12 text-center bg-gray-100 p-4 rounded-xl shadow-md items-center"
          >
            <p className="text-gray-600">Completed Courses</p>
            <h2 className="text-4xl font-bold text-gray-800">
              {resData &&
                resData.filter(
                  (course) =>
                    course.completed_modules === course.total_modules &&
                    course.completed_modules !== 0
                ).length}
            </h2>
          </div>

          <div className="flex flex-row w-2/12 text-center bg-gray-100 p-4 rounded-xl shadow-md  items-center">
            <div className="relative w-24 h-24 pr-2">
              <svg viewBox="0 0 36 36" className="rotate-[-90deg]">
                <circle
                  className="text-gray-300"
                  cx="18"
                  cy="18"
                  r="16"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3.8"
                />
                <circle
                  className="text-blue-500"
                  cx="18"
                  cy="18"
                  r="16"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3.8"
                  strokeDasharray={strokeDasharray}
                  strokeDashoffset="0"
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xl font-semibold text-gray-700">
                  {percentage}%
                </span>
              </div>
            </div>
            <div className="flex flex-col">
              <div className="flex items-center">
                <div className="rounded-full bg-primary w-5 h-5"></div>{" "}
                <p className="pl-2"> Completed</p>
              </div>
              <div className="flex items-center">
                <div className="rounded-full bg-gray-300 w-5 h-5"></div>{" "}
                <p>To be completed</p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-around py-6">
          <div className="w-1/3 pr-4">
            <h3 className="text-lg font-bold mb-4">Enrolled Courses</h3>
            {resData.map((course, index) => (
              <div key={index} className="mb-4">
                <p>
                  {course.course_name} ({"Active"})
                </p>
                <div className="w-full bg-gray-300 h-2 rounded-full">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{
                      width: `${calculateOverallPercentage(
                        course.completed_modules,
                        course.total_modules
                      )}%`,
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>

          <div className="flex flex-col">
            <div className="w-3/5 bg-gray-100 p-4 rounded-xl shadow-md m-1 justify-center items-center text-center">
              <p>Total Quiz Completed</p>
              <h2 className="text-2xl font-bold text-gray-800">
                {resData.reduce(
                  (acc, course) => acc + parseInt(course.quizzes_completed),
                  0
                )}
              </h2>
            </div>
            <div className="w-3/5 bg-gray-100 p-4 rounded-xl shadow-md m-1 justify-center items-center text-center">
              <p>Total Lessons Completed</p>
              <h2 className="text-2xl font-bold text-gray-800">
                {resData.reduce(
                  (acc, course) => acc + parseInt(course.lessons_completed),
                  0
                )}
              </h2>
            </div>
          </div>
          <div>{/* <Line options={options} data={data} /> */}</div>
        </div>
        <div className="flex flex-row justify-around items-center">
          <div className="py-4 w-2/5">
            <h3 className="text-lg font-bold mb-4">All Enrolled Courses</h3>
            <ul>
              {resData.map((course, index) => (
                <li
                  key={index}
                  className="bg-gray-100 p-4 mb-2 rounded-xl flex justify-between items-center shadow-md"
                >
                  <span>{course.course_name}</span>
                  <button
                    className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
                    onClick={() => setSelectedCourse(course)}
                  >
                    View Report
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {selectedCourse && (
            <div className="py-4 w-1/3">
              <h2 className="font-bold text-2xl">Course Details</h2>
              <div>
                <p>
                  <strong>Course Name:</strong> {selectedCourse.course_name}
                </p>
                <p>
                  <strong>Course ID:</strong> {selectedCourse.courseid}
                </p>
                <p>
                  <strong>Total Modules:</strong> {selectedCourse.total_modules}
                </p>
                <p>
                  <strong>Completed Modules:</strong>{" "}
                  {selectedCourse.completed_modules}
                </p>
                <p>
                  <strong>Quizzes Completed:</strong>{" "}
                  {selectedCourse.quizzes_completed}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="">
      {resData && <PerformanceOverview resData={resData} />}
    </div>
  );
};

export default IndividualPerformance;
