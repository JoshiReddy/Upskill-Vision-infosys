import React, { useEffect, useState } from "react";
import Swal from "sweetalert2";

const AuditPage = () => {
  const [audit, setAudit] = useState(null);
  const fetchAuditDetails = async () => {
    try {
      const response = await fetch(
        "http://localhost:8080/api/audit_trial/fetch-audit",
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      if (response.ok) {
        const data = await response.json();
        // console.log(data.content);

        setAudit(data.content);
      } else {
        const errorData = await response.json();
        Swal.fire({
          title: "Error Fetching Courses",
          text: errorData.message || "Failed to fetch data.",
          icon: "error",
        });
        console.error("Error Response:", errorData);
      }
    } catch (error) {
      alert(error || error.message);
    }
  };
  useEffect(() => {
    fetchAuditDetails();
  }, []);
  return (
    <div>
      {audit && (
        <div className="min-h-screen p-5">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-2xl font-bold text-center mb-5 text-gray-800">
              Audit Trail Data
            </h1>
            <div className="overflow-x-auto">
              <table className="w-full table-auto bg-white shadow-md rounded-lg">
                <thead>
                  <tr className="bg-gray-200 text-gray-700 uppercase text-sm leading-normal">
                    <th className="py-3 px-6 text-left">ID</th>
                    <th className="py-3 px-6 text-left">Code</th>
                    <th className="py-3 px-6 text-left">Email</th>
                    <th className="py-3 px-6 text-left">Name</th>
                    <th className="py-3 px-6 text-left">Date</th>
                    <th className="py-3 px-6 text-left">Action</th>
                  </tr>
                </thead>
                <tbody className="text-gray-600 text-sm font-light">
                  {audit.map((row, index) => (
                    <tr
                      key={index}
                      className="border-b border-gray-200 hover:bg-gray-100"
                    >
                      <td className="py-3 px-6">{row[0]}</td>
                      <td className="py-3 px-6">{row[1]}</td>
                      <td className="py-3 px-6">{row[2]}</td>
                      <td className="py-3 px-6">{row[3]}</td>
                      <td className="py-3 px-6">{row[4]}</td>
                      <td className="py-3 px-6">{row[5]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AuditPage;
