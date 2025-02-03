"use strict";

// eslint-disable-next-line no-unused-vars
const config = {
  style: "mapbox://styles/mapbox/light-v10",
  accessToken:
    "pk.eyJ1IjoiZGtnLTI0IiwiYSI6ImNsc3VsNTd6eDF4c2oybG5zM2RmcjJ6Z3EifQ.XKL22ONswQ5EZiNiq-zLSg",
  CSV: "https://docs.google.com/spreadsheets/d/1xIZKHpTUhlOLs8Lr9LQR8UTw4ReYxh7zRb_CwSvpCY8/gviz/tq?tqx=out:csv&sheet=sample_spreadsheet",
  center: [-120.234, 47.398],
  zoom: 6,
  title: "Replace with your title",
  description:
    "Replace with information about your application. Ex. You can search by address to sort the list below by distance. You can also filter the list by language support options, which days a location is open, and whether they have devices to use to complete the survey by phone or online.",
  sideBarInfo: ["Location_Name", "Address", "Phone"],
  popupInfo: ["Location_Name"],
  filters: [
    {
      type: "dropdown",
      title: "Languages supported: ",
      columnHeader: "Languages",
      listItems: [
        "Amharic",
        "ASL",
        "Cambodian",
        "Chinese",
        "Danish",
        "English",
        "French",
        "German",
        "Greek",
        "Hindi",
        "Italian",
        "Japanese",
        "Korean",
        "Language Line Services",
        "Norwegian",
        "Oriya",
        "Portuguese",
        "Punjabi",
        "Russian",
        "Somali",
        "Spanish",
        "Swedish",
        "Tagalog",
        "Thai",
        "Tigrinya",
        "Tongan",
        "Vietnamese",
        "Ukranian",
      ],
    },
    {
      type: "checkbox",
      title: "Devices available: ",
      columnHeader: "Devices_available", // Case sensitive - must match spreadsheet entry
      listItems: ["Computer", "Wi-Fi", "Adaptive Laptops"], // Case sensitive - must match spreadsheet entry; This will take up to six inputs but is best used with a maximum of three;
    },
    {
      type: "dropdown",
      title: "Clients: ",
      columnHeader: "Clients",
      listItems: [
        "Adults",
        "Disabled",
        "Homeless",
        "Immigrants/Refugees",
        "Low Income",
        "Seniors",
        "Youth: Pre-teen",
        "Youth: Teen",
      ],
    },
  ],
};
