import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const AllUsersPerformance = () => {
  const navigate = useNavigate();
  const token = sessionStorage.getItem("auth_token");
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredUsers, setFilteredUsers] = useState({});

  const handleReq = async () => {
    try {
      const response = await fetch(
        "http://localhost:8080/api/all_users_list/all-users-progress",
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      if (!response.ok) {
        throw new Error("Failed to fetch data");
      }
      const data = await response.json();
      //   console.log(data);
      // Filter users based on search query (user's name or email)
      const filteredUser = data.filter(
        (user) =>
          user.userName.toLowerCase().includes(searchQuery.toLowerCase()) ||
          user.email.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredUsers(filteredUser);
    } catch (err) {
      console.error(err);
    }
  };
  useEffect(() => {
    handleReq();
    // eslint-disable-next-line
  }, []);
  return (
    <div className="flex flex-col items-center h-screen">
      <div className="bg-blue-500 text-white text-center py-4 rounded-b-full w-full">
        <h1 className="text-3xl font-bold py-2">Admin Performance Dashboard</h1>
      </div>

      {/* Search Bar */}
      <div className="w-2/5 py-4">
        <input
          type="text"
          placeholder="🔍 Search Users"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full p-2 rounded-lg border border-gray-300"
        />
      </div>

      {/* Display filtered users */}
      {filteredUsers.length > 0 ? (
        filteredUsers.map((user, index) => (
          <div
            key={index}
            className="w-4/5 bg-white p-6 shadow-lg rounded-2xl mb-6"
          >
            <h2 className="text-2xl font-semibold">{user.userName}</h2>
            <p className="text-gray-600">{user.email}</p>

            <div className="py-3">
              <div className="w-full flex justify-around mb-4">
                <div className="bg-gray-100 p-4 rounded-xl shadow-md text-center w-1/5 ">
                  <p>
                    <strong>Total Courses Enrolled:</strong>
                  </p>
                  <h3 className="text-2xl font-bold">{user.totalCourses}</h3>
                </div>

                <div className="bg-gray-100 p-4 rounded-xl shadow-md text-center w-1/5">
                  <p>
                    <strong>Overall Performance:</strong>
                  </p>
                  <h3 className="text-2xl font-bold">
                    {user.overallPerformance}%
                  </h3>
                </div>
                <div className="text-center flex items-center justify-center">
                  <button
                    onClick={() =>
                      navigate(
                        `/dashboard/user-performance/${token}/${user.email}`
                      )
                    }
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg"
                  >
                    View Details
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))
      ) : (
        <p className="text-center text-xl text-gray-600">No users found</p>
      )}
    </div>
  );
};

export default AllUsersPerformance;
