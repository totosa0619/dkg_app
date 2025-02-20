/* global config csv2geojson turf Assembly $ */
"use strict";

const render = (originalData) => {
  mapboxgl.accessToken = config.accessToken;
  const columnHeaders = originalData?.sideBarInfo;

  let geojsonData = {};
  const filteredGeojson = {
    type: "FeatureCollection",
    features: [],
  };

  const buildingData = originalData?.buildingData;
  const otherBuildingColor = originalData?.otherBuildingColor || "#aaa";

  const buildingIdsToColor = [];
  const buildingColors = {};

  buildingData.forEach((building) => {
    buildingIdsToColor.push(building.buildingId);
    buildingColors[building.buildingId] = building.color;
  });

  const map = new mapboxgl.Map({
    container: "map",
    style: "mapbox://styles/mapbox/light-v10",
    center: originalData?.center,
    zoom: originalData?.zoom,
    pitch: originalData?.pitch,
    bearing: originalData?.bearing,
    transformRequest: transformRequest,
  });

  function flyToLocation(currentFeature) {
    map.flyTo({
      center: currentFeature,
      zoom: 15.5,
    });
  }

  function createPopup(currentFeature) {
    const popups = document.getElementsByClassName("mapboxgl-popup");
    /** Check if there is already a popup on the map and if so, remove it */
    if (popups[0]) popups[0].remove();
    new mapboxgl.Popup({ closeOnClick: true })
      .setLngLat(currentFeature.geometry.coordinates)
      .setHTML(
        "<h3>" + currentFeature.properties[originalData?.popupInfo] + "</h3>"
      )
      .addTo(map);
  }

  function buildLocationList(locationData) {
    /* Add a new listing section to the sidebar. */
    const listings = document.getElementById("listings");
    listings.innerHTML = "";
    locationData.features.forEach((location, i) => {
      const prop = location.properties;

      const listing = listings.appendChild(document.createElement("div"));
      /* Assign a unique `id` to the listing. */
      listing.id = "listing-" + prop.id;

      /* Assign the `item` class to each listing for styling. */
      listing.className = "item";

      /* Add the link to the individual listing created above. */
      const link = listing.appendChild(document.createElement("button"));
      link.className = "title";
      link.id = "link-" + prop.id;
      link.innerHTML =
        '<p style="line-height: 1.25">' + prop[columnHeaders[0]] + "</p>";

      /* Add details to the individual listing. */
      const details = listing.appendChild(document.createElement("div"));
      details.className = "content";

      for (let i = 1; i < columnHeaders.length; i++) {
        const div = document.createElement("div");
        div.innerText += prop[columnHeaders[i]];
        div.className;
        details.appendChild(div);
      }

      link.addEventListener("click", function () {
        const clickedListing = location.geometry.coordinates;
        flyToLocation(clickedListing);
        createPopup(location);

        const activeItem = document.getElementsByClassName("active");
        if (activeItem[0]) {
          activeItem[0].classList.remove("active");
        }
        this.parentNode.classList.add("active");

        const divList = document.querySelectorAll(".content");
        const divCount = divList.length;
        for (i = 0; i < divCount; i++) {
          divList[i].style.maxHeight = null;
        }

        for (let i = 0; i < geojsonData.features.length; i++) {
          this.parentNode.classList.remove("active");
          this.classList.toggle("active");
          const content = this.nextElementSibling;
          if (content.style.maxHeight) {
            content.style.maxHeight = null;
          } else {
            content.style.maxHeight = content.scrollHeight + "px";
          }
        }
      });
    });
  }

  // Build dropdown list function
  // title - the name or 'category' of the selection e.g. 'Languages: '
  // defaultValue - the default option for the dropdown list
  // listItems - the array of filter items

  function buildDropDownList(title, listItems) {
    const filtersDiv = document.getElementById("filters");
    const mainDiv = document.createElement("div");
    const filterTitle = document.createElement("h3");
    filterTitle.innerText = title;
    filterTitle.classList.add("py12", "txt-bold");
    mainDiv.appendChild(filterTitle);

    const selectContainer = document.createElement("div");
    selectContainer.classList.add("select-container", "center");

    const dropDown = document.createElement("select");
    dropDown.classList.add("select", "filter-option");

    const selectArrow = document.createElement("div");
    selectArrow.classList.add("select-arrow");

    const firstOption = document.createElement("option");

    dropDown.appendChild(firstOption);
    selectContainer.appendChild(dropDown);
    selectContainer.appendChild(selectArrow);
    mainDiv.appendChild(selectContainer);

    for (let i = 0; i < listItems.length; i++) {
      const opt = listItems[i];
      const el1 = document.createElement("option");
      el1.textContent = opt;
      el1.value = opt;
      dropDown.appendChild(el1);
    }
    filtersDiv.appendChild(mainDiv);
  }

  // Build checkbox function
  // title - the name or 'category' of the selection e.g. 'Languages: '
  // listItems - the array of filter items
  // To DO: Clean up code - for every third checkbox, create a div and append new checkboxes to it

  function buildCheckbox(title, listItems) {
    const filtersDiv = document.getElementById("filters");
    const mainDiv = document.createElement("div");
    const filterTitle = document.createElement("div");
    const formatcontainer = document.createElement("div");
    filterTitle.classList.add("center", "flex-parent", "py12", "txt-bold");
    formatcontainer.classList.add(
      "center",
      "flex-parent",
      "flex-parent--column",
      "px3",
      "flex-parent--space-between-main"
    );
    const secondLine = document.createElement("div");
    secondLine.classList.add(
      "center",
      "flex-parent",
      "py12",
      "px3",
      "flex-parent--space-between-main"
    );
    filterTitle.innerText = title;
    mainDiv.appendChild(filterTitle);
    mainDiv.appendChild(formatcontainer);

    for (let i = 0; i < listItems.length; i++) {
      const container = document.createElement("label");

      container.classList.add("checkbox-container");

      const input = document.createElement("input");
      input.classList.add("px12", "filter-option");
      input.setAttribute("type", "checkbox");
      input.setAttribute("id", listItems[i]);
      input.setAttribute("value", listItems[i]);

      const checkboxDiv = document.createElement("div");
      const inputValue = document.createElement("p");
      inputValue.innerText = listItems[i];
      checkboxDiv.classList.add("checkbox", "mr6");
      checkboxDiv.appendChild(Assembly.createIcon("check"));

      container.appendChild(input);
      container.appendChild(checkboxDiv);
      container.appendChild(inputValue);

      formatcontainer.appendChild(container);
    }
    filtersDiv.appendChild(mainDiv);
  }

  const selectFilters = [];
  const checkboxFilters = [];

  function createFilterObject(filterSettings) {
    filterSettings.forEach((filter) => {
      if (filter.type === "checkbox") {
        const keyValues = {};
        Object.assign(keyValues, {
          header: filter.columnHeader,
          value: filter.listItems,
        });
        checkboxFilters.push(keyValues);
      }
      if (filter.type === "dropdown") {
        const keyValues = {};
        Object.assign(keyValues, {
          header: filter.columnHeader,
          value: filter.listItems,
        });
        selectFilters.push(keyValues);
      }
    });
  }

  function applyFilters() {
    const filterForm = document.getElementById("filters");

    filterForm.addEventListener("change", function () {
      const filterOptionHTML = this.getElementsByClassName("filter-option");
      const filterOption = [].slice.call(filterOptionHTML);

      const geojSelectFilters = [];
      const geojCheckboxFilters = [];

      filteredGeojson.features = [];
      // const filteredFeatures = [];
      // filteredGeojson.features = [];

      filterOption.forEach((filter) => {
        if (filter.type === "checkbox" && filter.checked) {
          checkboxFilters.forEach((objs) => {
            Object.entries(objs).forEach(([, value]) => {
              if (value.includes(filter.value)) {
                const geojFilter = [objs.header, filter.value];
                geojCheckboxFilters.push(geojFilter);
              }
            });
          });
        }
        if (filter.type === "select-one" && filter.value) {
          selectFilters.forEach((objs) => {
            Object.entries(objs).forEach(([, value]) => {
              if (value.includes(filter.value)) {
                const geojFilter = [objs.header, filter.value];
                geojSelectFilters.push(geojFilter);
              }
            });
          });
        }
      });

      if (geojCheckboxFilters.length === 0 && geojSelectFilters.length === 0) {
        geojsonData.features.forEach((feature) => {
          filteredGeojson.features.push(feature);
        });
      } else if (geojCheckboxFilters.length > 0) {
        geojCheckboxFilters.forEach((filter) => {
          geojsonData.features.forEach((feature) => {
            if (feature.properties[filter[0]].includes(filter[1])) {
              if (
                filteredGeojson.features.filter(
                  (f) => f.properties.id === feature.properties.id
                ).length === 0
              ) {
                filteredGeojson.features.push(feature);
              }
            }
          });
        });
        if (geojSelectFilters.length > 0) {
          const removeIds = [];
          filteredGeojson.features.forEach((feature) => {
            let selected = true;
            geojSelectFilters.forEach((filter) => {
              if (
                feature.properties[filter[0]].indexOf(filter[1]) < 0 &&
                selected === true
              ) {
                selected = false;
                removeIds.push(feature.properties.id);
              } else if (selected === false) {
                removeIds.push(feature.properties.id);
              }
            });
          });
          let uniqueRemoveIds = [...new Set(removeIds)];
          uniqueRemoveIds.forEach(function (id) {
            const idx = filteredGeojson.features.findIndex(
              (f) => f.properties.id === id
            );
            filteredGeojson.features.splice(idx, 1);
          });
        }
      } else {
        geojsonData.features.forEach((feature) => {
          let selected = true;
          geojSelectFilters.forEach((filter) => {
            if (
              !feature.properties[filter[0]].includes(filter[1]) &&
              selected === true
            ) {
              selected = false;
            }
          });
          if (
            selected === true &&
            filteredGeojson.features.filter(
              (f) => f.properties.id === feature.properties.id
            ).length === 0
          ) {
            filteredGeojson.features.push(feature);
          }
        });
      }

      map.getSource("locationData").setData(filteredGeojson);
      buildLocationList(filteredGeojson);
    });
  }

  function filters(filterSettings) {
    filterSettings.forEach((filter) => {
      if (filter.type === "checkbox") {
        buildCheckbox(filter.title, filter.listItems);
      } else if (filter.type === "dropdown") {
        buildDropDownList(filter.title, filter.listItems);
      }
    });
  }

  function removeFilters() {
    const input = document.getElementsByTagName("input");
    const select = document.getElementsByTagName("select");
    const selectOption = [].slice.call(select);
    const checkboxOption = [].slice.call(input);
    filteredGeojson.features = [];
    checkboxOption.forEach((checkbox) => {
      if (checkbox.type === "checkbox" && checkbox.checked === true) {
        checkbox.checked = false;
      }
    });

    selectOption.forEach((option) => {
      option.selectedIndex = 0;
    });

    map.getSource("locationData").setData(geojsonData);
    buildLocationList(geojsonData);
  }

  function removeFiltersButton() {
    const removeFilter = document.getElementById("removeFilters");
    removeFilter.addEventListener("click", () => {
      removeFilters();
    });
  }

  createFilterObject(originalData?.filters);
  applyFilters();
  filters(originalData?.filters);
  removeFiltersButton();

  const geocoder = new MapboxGeocoder({
    accessToken: mapboxgl.accessToken, // Set the access token
    mapboxgl: mapboxgl, // Set the mapbox-gl instance
    marker: true, // Use the geocoder's default marker style
    zoom: 11,
  });

  function sortByDistance(selectedPoint) {
    const options = { units: "miles" };
    let data;
    if (filteredGeojson.features.length > 0) {
      data = filteredGeojson;
    } else {
      data = geojsonData;
    }
    data.features.forEach((data) => {
      Object.defineProperty(data.properties, "distance", {
        value: turf.distance(selectedPoint, data.geometry, options),
        writable: true,
        enumerable: true,
        configurable: true,
      });
    });

    data.features.sort((a, b) => {
      if (a.properties.distance > b.properties.distance) {
        return 1;
      }
      if (a.properties.distance < b.properties.distance) {
        return -1;
      }
      return 0; // a must be equal to b
    });
    const listings = document.getElementById("listings");
    while (listings.firstChild) {
      listings.removeChild(listings.firstChild);
    }
    buildLocationList(data);
  }

  geocoder.on("result", (ev) => {
    const searchResult = ev.result.geometry;
    sortByDistance(searchResult);
  });

  map.on("load", () => {
    map.addLayer({
      id: "3d-buildings",
      source: "composite",
      "source-layer": "building",
      type: "fill-extrusion",
      minzoom: 14,
      paint: {
        "fill-extrusion-color": [
          "match",
          ["id"],
          ...buildingIdsToColor.reduce((acc, id) => {
            acc.push(id);
            acc.push(buildingColors[id]);
            return acc;
          }, []),
          otherBuildingColor,
        ],
        "fill-extrusion-height": [
          "interpolate",
          ["linear"],
          ["zoom"],
          15,
          0,
          15.05,
          ["get", "height"],
        ],
        "fill-extrusion-base": [
          "interpolate",
          ["linear"],
          ["zoom"],
          15,
          0,
          15.05,
          ["get", "min_height"],
        ],
        "fill-extrusion-opacity": 1,
      },
    });
    map.addControl(geocoder, "top-right");

    // csv2geojson - following the Sheet Mapper tutorial https://www.mapbox.com/impact-tools/sheet-mapper
    console.log("loaded");
    $(document).ready(() => {
      console.log("ready");
      $.ajax({
        type: "GET",
        url: originalData?.spreadSheetLink,
        dataType: "text",
        success: function (csvData) {
          makeGeoJSON(csvData);
        },
        error: function (request, status, error) {
          console.log(request);
          console.log(status);
          console.log(error);
        },
      });
    });

    function makeGeoJSON(csvData) {
      csv2geojson.csv2geojson(
        csvData,
        {
          latfield: "Latitude",
          lonfield: "Longitude",
          delimiter: ",",
        },
        (err, data) => {
          data.features.forEach((data, i) => {
            data.properties.id = i;
          });

          geojsonData = data;
          // Add the the layer to the map
          console.log(originalData?.markerImageUrl);
          map.loadImage(originalData?.markerImageUrl, function (error, image) {
            if (error) {
              console.error(error);
              return;
            }
            map.addImage(originalData?.markerImageName, image);
            map.addLayer({
              id: "locationData",
              type: "symbol",
              source: {
                type: "geojson",
                data: geojsonData,
              },
              layout: {
                "icon-image": originalData?.markerImageName,
                "icon-size": originalData?.markerImageSize,
              },
            });
          });
        }
      );

      map.on("click", function (e) {
        let features = map.queryRenderedFeatures(e.point, {
          layers: ["3d-buildings"],
        });
        console.log(features[0].id);
      });

      map.on("click", "locationData", (e) => {
        const features = map.queryRenderedFeatures(e.point, {
          layers: ["locationData"],
        });
        const clickedPoint = features[0].geometry.coordinates;
        flyToLocation(clickedPoint);
        sortByDistance(clickedPoint);
        createPopup(features[0]);
      });

      map.on("mouseenter", "locationData", () => {
        map.getCanvas().style.cursor = "pointer";
      });

      map.on("mouseleave", "locationData", () => {
        map.getCanvas().style.cursor = "";
      });
      buildLocationList(geojsonData);
    }
  });

  // Modal - popup for filtering results
  const filterResults = document.getElementById("filterResults");
  const exitButton = document.getElementById("exitButton");
  const modal = document.getElementById("modal");

  filterResults.addEventListener("click", () => {
    modal.classList.remove("hide-visually");
    modal.classList.add("z5");
  });

  exitButton.addEventListener("click", () => {
    modal.classList.add("hide-visually");
  });

  const title = document.getElementById("title");
  title.innerText = originalData?.title;
  const description = document.getElementById("description");
  description.innerText = originalData?.description;

  function transformRequest(url) {
    const isMapboxRequest =
      url.slice(8, 22) === "api.mapbox.com" ||
      url.slice(10, 26) === "tiles.mapbox.com";
    return {
      url: isMapboxRequest ? url.replace("?", "?pluginName=finder&") : url,
    };
  }
};

const apiUrl = "/api/diagrams";
const params = new URLSearchParams(window.location.search);
const KEY = "slug";

window.onmessage = (e) => {
  if (e.data?.name === "parentMessage") {
    if (e.data.data?.originalData) {
      render(e.data.data.originalData);
    }
  }
};

if (params.has(KEY)) {
  const key = params.get(KEY);
  let url = `${apiUrl}/${key}`;

  if (key.includes("demo_example")) {
    const type = key.split("?")[1];

    url = `/diagrams/${type}/data.json`;
  }
  const fetchData = async () => {
    try {
      const response = await fetch(url);
      const data = await response.json();
      if (data?.originalData) {
        render(data.originalData);
      }
      if (data?.source?.originalData) {
        render(data.source.originalData);
      }
    } catch (error) {
      console.error(error);
    }
  };
  fetchData();
}
