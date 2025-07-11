import React, { useState } from "react";
// import { IoMdSearch } from "react-icons/io";
import { CgProfile } from "react-icons/cg";
import { MdMenu } from "react-icons/md";
import { AiOutlineClose } from "react-icons/ai";
import MainDashboard from "./sunComponents/MainDashboard";
import Employees from "./sunComponents/Employees";
import Participants from "./sunComponents/Participants";
// import Settings from "./sunComponents/♦Settings";
import { IoMdAddCircleOutline } from "react-icons/io";
import AvailableCourses from "./sunComponents/AvailableCourses";
import AuditPage from "./sunComponents/AuditPage";

const HradminDashboard = ({
  handleLogout,
  logo,
  name,
  dashboardData,
  setDashboardData,
}) => {
  const [open, setOpen] = useState(false);
  const [page, setPage] = useState("dashboard");
  const [formView, setFormView] = useState(false);
  return (
    <>
      {" "}
      <div className="flex flex-row bg-slate-50 w-full">
        <div className="md:flex flex-col min-w-fit w-1/4 h-screen hidden shadow-xl bg-white">
          <div className="flex flex-row justify-center items-center">
            <img src={logo} alt="" srcSet="" className="size-16 m-2" />
            <div className="flex flex-col p-2 font-koulen">
              <p className="flex items-end text-4xl  text-primary">UPSKILL</p>
              <p className="flex items-start text-2xl  text-red-500">vision</p>
            </div>
          </div>
          <div className="flex flex-col font-koulen h-full items-center justify-center sticky">
            <div className="text-left flex flex-col">
              <button
                onClick={() => setPage("dashboard")}
                type="button"
                className="hover:text-primary focus:text-primary transition-all duration-300 text-2xl text-left cursor-pointer"
              >
                Dashboard
              </button>
              <button
                onClick={() => setPage("employees")}
                type="button"
                className="hover:text-primary focus:text-primary transition-all duration-300 text-2xl text-left cursor-pointer"
              >
                Employees
              </button>
              <button
                onClick={() => setPage("participants")}
                type="button"
                className="hover:text-primary focus:text-primary transition-all duration-300 text-2xl text-left cursor-pointer"
              >
                Participants
              </button>
              <button
                onClick={() => setPage("courses")}
                type="button"
                className="hover:text-primary focus:text-primary transition-all duration-300 text-2xl text-left cursor-pointer"
              >
                Courses
              </button>
              <button
                onClick={() => setPage("audit")}
                type="button"
                className="hover:text-primary focus:text-primary transition-all duration-300 text-2xl text-left cursor-pointer"
              >
                Audit Trail
              </button>
              {/* <button
                onClick={() => setPage("settings")}
                type="button"
                className="hover:text-primary focus:text-primary transition-all duration-300 text-2xl text-left cursor-pointer"
              >
                Settings
              </button> */}
            </div>
          </div>
        </div>
        <div
          className="md:hidden flex p-3 items-center h-max"
          onClick={() => (open ? setOpen(false) : setOpen(true))}
        >
          {!open && <MdMenu className="text-4xl" />}
          {open && <AiOutlineClose className="text-4xl" />}
        </div>
        {open && (
          <div className="md:hidden flex-col min-w-fit w-3/5 h-max absolute rounded-lg bg-slate-50 shadow-xl p-5 top-36 sm:left-1/4 left-5">
            <div className="flex flex-wrap justify-around items-center">
              <div className="flex flex-row justify-center items-center">
                <img src={logo} alt="" srcSet="" className="size-16 m-2" />
                <div className="flex flex-col p-2 font-koulen">
                  <p className="flex items-end text-4xl  text-primary">
                    UPSKILL
                  </p>
                  <p className="flex items-start text-2xl  text-red-500">
                    vision
                  </p>
                </div>
              </div>
              <div className="flex flex-col font-koulen h-full items-center justify-center">
                <div className="text-left flex flex-col">
                  <button
                    onClick={() => {
                      setPage("dashboard");
                      setOpen(false);
                    }}
                    type="button"
                    className="hover:text-primary focus:text-primary transition-all duration-300 text-2xl text-left cursor-pointer"
                  >
                    Dashboard
                  </button>
                  <button
                    onClick={() => {
                      setPage("employees");
                      setOpen(false);
                    }}
                    type="button"
                    className="hover:text-primary focus:text-primary transition-all duration-300 text-2xl text-left cursor-pointer"
                  >
                    Employees
                  </button>
                  <button
                    onClick={() => {
                      setPage("participants");
                      setOpen(false);
                    }}
                    type="button"
                    className="hover:text-primary focus:text-primary transition-all duration-300 text-2xl text-left cursor-pointer"
                  >
                    Participants
                  </button>
                  <button
                    onClick={() => {
                      setPage("courses");
                      setOpen(false);
                    }}
                    type="button"
                    className="hover:text-primary focus:text-primary transition-all duration-300 text-2xl text-left cursor-pointer"
                  >
                    Courses
                  </button>
                  <button
                    onClick={() => {
                      setPage("audit");
                      setOpen(false);
                    }}
                    type="button"
                    className="hover:text-primary focus:text-primary transition-all duration-300 text-2xl text-left cursor-pointer"
                  >
                    Audit Trail
                  </button>
                  {/* <button
                    onClick={() => {
                      setPage("settings");
                      setOpen(false);
                    }}
                    type="button"
                    className="hover:text-primary focus:text-primary transition-all duration-300 text-2xl text-left cursor-pointer"
                  >
                    Settings
                  </button> */}
                </div>
              </div>
            </div>
          </div>
        )}
        <div className="flex flex-col w-4/5 overflow-x-auto h-screen">
          <div className="flex flex-row flex-wrap items-center justify-around  h-max p-5 ">
            {/* <div className="flex  w-96 rounded-full inner-shadow h-max p-1 items-center m-2">
              <div className="flex flex-row items-center">
                <IoMdSearch className="text-gray-500 size-9 px-2" />
                <p className="text-gray-500">Search here...</p>
              </div>
            </div> */}
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
          <div className="flex flex-col justify-center items-center font-bold text-4xl uppercase h-max">
            <p className="text-primary">HR Admin Dashboard</p>
          </div>{" "}
          {/*  Center part content to be added  */}
          <div className="flex flex-col h-max">
            {page === "dashboard" ? (
              <>
                <div className="flex justify-end w-full px-10">
                  <button
                    type="button"
                    onClick={() => setFormView(true)}
                    className="text-green-600 flex-row flex items-center border-2 border-green-500 rounded-lg p-2 m-2 hover:text-white hover:bg-green-500 transition-all duration-300"
                  >
                    <IoMdAddCircleOutline />
                    <span>Add New Course</span>
                  </button>
                </div>
                <MainDashboard
                  dashboardData={dashboardData}
                  formView={formView}
                  setFormView={setFormView}
                  setDashboardData={setDashboardData}
                />
              </>
            ) : page === "employees" ? (
              <Employees
                dashboardData={dashboardData}
                setDashboardData={setDashboardData}
              />
            ) : page === "participants" ? (
              <Participants dashboardData={dashboardData} />
            ) : page === "courses" ? (
              <AvailableCourses dashboardData={dashboardData} />
            ) : page === "audit" ? (
              <AuditPage />
            ) : (
              <>Some Error Occured</>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default HradminDashboard;
