import React from "react";
import { FaEye } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

const Participants = ({ dashboardData }) => {
  const navigate = useNavigate();
  const token = sessionStorage.getItem("auth_token");
  const filterWhereStatusNotZero = dashboardData.filter(
    (item) => item[1] !== 0 && item[4] === "participant"
  );

  const renderTable = (filteredData) => (
    <div className="overflow-x-auto justify-center">
      <p className="py-5 text-center text-2xl font-semibold">Participants</p>
      <table className="min-w-full border border-gray-300 text-left text-sm ">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-4 py-2 border-b border-gray-300">Name</th>
            <th className="px-4 py-2 border-b border-gray-300">Email</th>
            <th className="px-4 py-2 border-b border-gray-300">Phone</th>
            <th className="px-4 py-2 border-b border-gray-300">Role</th>
            <th className="px-4 py-2 border-b border-gray-300">
              View Performance
            </th>
          </tr>
        </thead>
        <tbody>
          {filteredData.map((item) => (
            <tr key={item[0]} className="hover:bg-gray-50">
              <td className="px-4 py-2 border-b border-gray-300">{item[3]}</td>
              <td className="px-4 py-2 border-b border-gray-300">{item[0]}</td>
              <td className="px-4 py-2 border-b border-gray-300">{item[2]}</td>
              <td className="px-4 py-2 border-b border-gray-300">{item[4]}</td>
              <td className="px-4 py-2 border-b border-gray-300">
                <button
                  onClick={() =>
                    navigate(`/dashboard/user-performance/${token}/${item[0]}`)
                  }
                >
                  <FaEye />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
  return (
    <div>
      <div className="p-5 flex flex-row-reverse">
        {" "}
        <button
          className="flex flex-row justify-center items-center border-2 border-primary text-primary hover:bg-primary hover:text-slate-100 rounded transition-all"
          onClick={() => navigate(`/dashboard/all-users-performance/`)}
        >
          <span className="font-semibold w-2/3 pr-2">
            View insights of all users
          </span>
          <FaEye />
        </button>
      </div>
      <div>{renderTable(filterWhereStatusNotZero)}</div>
    </div>
  );
};

export default Participants;
