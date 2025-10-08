/**
 * Google Maps Integration for OOBC Application
 *
 * This provides an alternative to the default Leaflet/OpenStreetMap integration
 * with Google Maps for potentially better accuracy and familiar interface.
 *
 * Usage:
 * 1. Add Google Maps API key to Django settings: GOOGLE_MAPS_API_KEY
 * 2. Include this script after Google Maps JavaScript API
 * 3. Use data-google-map attribute instead of data-obc-map
 *
 * Note: Google Maps API has usage limits and costs beyond free tier.
 * See: https://developers.google.com/maps/pricing-and-plans
 */

(function () {
    "use strict";

    var DEFAULT_CENTER = {
        lat: 7.1907,
        lng: 125.4553,
        zoom: 6
    };

    var PHILIPPINES_BOUNDS = {
        north: 21.0,
        south: 4.0,
        west: 114.0,
        east: 127.0
    };

    function parseNumber(value) {
        if (value === null || value === undefined || value === "") {
            return null;
        }
        var parsed = Number(value);
        return Number.isFinite(parsed) ? parsed : null;
    }

    function formatCoord(value) {
        return value !== null && value !== undefined
            ? Number(value).toFixed(6)
            : "";
    }

    function parseJsonScript(scriptId) {
        if (!scriptId) {
            return null;
        }
        var script = document.getElementById(scriptId);
        if (!script) {
            console.warn("Google Maps initialization skipped; missing script", scriptId);
            return null;
        }
        try {
            return JSON.parse(script.textContent);
        } catch (error) {
            console.error("Failed to parse JSON script", scriptId, error);
            return null;
        }
    }

    function createMap(mapNode, dataset) {
        var lat = parseNumber(dataset.initialLat);
        if (lat === null) {
            lat = DEFAULT_CENTER.lat;
        }
        var lng = parseNumber(dataset.initialLng);
        if (lng === null) {
            lng = DEFAULT_CENTER.lng;
        }
        var zoom = parseNumber(dataset.initialZoom);
        if (zoom === null) {
            zoom = DEFAULT_CENTER.zoom;
        }

        var mapOptions = {
            center: { lat: lat, lng: lng },
            zoom: zoom,
            restriction: {
                latLngBounds: PHILIPPINES_BOUNDS,
                strictBounds: false
            },
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            mapTypeControl: true,
            mapTypeControlOptions: {
                style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
                position: google.maps.ControlPosition.TOP_CENTER
            },
            zoomControl: true,
            zoomControlOptions: {
                position: google.maps.ControlPosition.RIGHT_CENTER
            },
            scaleControl: true,
            streetViewControl: false,
            fullscreenControl: true
        };

        // Disable scroll wheel zoom for detail mode (read-only maps)
        if (dataset.mode === "detail") {
            mapOptions.scrollwheel = false;
            mapOptions.disableDoubleClickZoom = true;
        }

        return new google.maps.Map(mapNode, mapOptions);
    }

    function buildLookup(collection) {
        var lookup = new Map();
        if (!Array.isArray(collection)) {
            return lookup;
        }
        collection.forEach(function (item) {
            if (!item || item.id === undefined) {
                return;
            }
            lookup.set(String(item.id), item);
        });
        return lookup;
    }

    function findBestCoordinates(lookups, ids) {
        for (var i = 0; i < ids.length; i += 1) {
            var config = ids[i];
            if (!config || !config.id || !config.lookup) {
                continue;
            }
            var record = config.lookup.get(String(config.id));
            if (!record) {
                continue;
            }
            var lat = parseNumber(record.center_lat);
            var lng = parseNumber(record.center_lng);
            if (lat !== null && lng !== null) {
                return { lat: lat, lng: lng, zoom: config.zoom };
            }
        }
        return null;
    }

    function setupFormMap(container) {
        var mapNode = container.querySelector("[data-google-map-target]");
        if (!mapNode) {
            return;
        }

        var map = createMap(mapNode, container.dataset);
        var marker = null;
        var isManualMarker = false;
        var centroidUrl = container.dataset.centroidUrl || "";
        var centroidRequestId = 0;

        var latField = document.getElementById(container.dataset.latField || "");
        var lngField = document.getElementById(container.dataset.lngField || "");

        function currentLatLng() {
            return {
                lat: parseNumber(latField ? latField.value : null),
                lng: parseNumber(lngField ? lngField.value : null)
            };
        }

        function placeMarker(lat, lng, zoom, respectExisting) {
            if (lat === null || lng === null) {
                return;
            }

            if (respectExisting && isManualMarker) {
                return;
            }

            var position = { lat: lat, lng: lng };

            if (!marker) {
                marker = new google.maps.Marker({
                    position: position,
                    map: map,
                    title: "Selected Location",
                    draggable: true
                });

                // Handle marker drag
                marker.addListener('dragend', function() {
                    var pos = marker.getPosition();
                    if (latField) latField.value = formatCoord(pos.lat());
                    if (lngField) lngField.value = formatCoord(pos.lng());
                    isManualMarker = true;
                });
            } else {
                marker.setPosition(position);
            }

            map.setCenter(position);
            if (zoom) {
                map.setZoom(zoom);
            }

            // Update form fields if needed
            if (latField && lngField) {
                var shouldUpdateFields =
                    latField.value === "" ||
                    lngField.value === "" ||
                    !isManualMarker;

                if (shouldUpdateFields) {
                    latField.value = formatCoord(lat);
                    lngField.value = formatCoord(lng);
                    isManualMarker = false;
                }
            }
        }

        function updateMarkerFromFields() {
            if (!latField || !lngField) {
                return;
            }
            var coords = currentLatLng();
            if (coords.lat === null || coords.lng === null) {
                return;
            }
            isManualMarker = true;
            placeMarker(coords.lat, coords.lng, 14, false);
        }

        // Handle manual coordinate input
        if (latField && lngField) {
            var initial = currentLatLng();
            if (initial.lat !== null && initial.lng !== null) {
                placeMarker(initial.lat, initial.lng);
            }

            var syncField = function () {
                updateMarkerFromFields();
            };
            latField.addEventListener("change", syncField);
            lngField.addEventListener("change", syncField);
            latField.addEventListener("input", syncField);
            lngField.addEventListener("input", syncField);
        }

        // Handle map clicks
        map.addListener('click', function(event) {
            var lat = event.latLng.lat();
            var lng = event.latLng.lng();

            placeMarker(lat, lng, null, false);
            isManualMarker = true;

            if (latField) latField.value = formatCoord(lat);
            if (lngField) lngField.value = formatCoord(lng);
        });

        // Location lookup functionality
        var locationData = parseJsonScript(container.dataset.locationScript);
        var lookups = {
            regions: buildLookup(locationData && locationData.regions),
            provinces: buildLookup(locationData && locationData.provinces),
            municipalities: buildLookup(locationData && locationData.municipalities),
            barangays: buildLookup(locationData && locationData.barangays)
        };

        function fetchCentroid(level, id) {
            if (!centroidUrl || !level || !id) {
                return Promise.resolve(null);
            }

            var url = centroidUrl +
                "?level=" + encodeURIComponent(level) +
                "&id=" + encodeURIComponent(id);

            return fetch(url, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(function (response) {
                if (!response.ok) {
                    return null;
                }
                return response.json();
            })
            .catch(function () {
                return null;
            });
        }

        function recenterFromSelections(respectExisting) {
            var selectionHierarchy = [];
            var barangayField = document.getElementById(container.dataset.barangayField || "");
            var municipalityField = document.getElementById(container.dataset.municipalityField || "");
            var provinceField = document.getElementById(container.dataset.provinceField || "");
            var regionField = document.getElementById(container.dataset.regionField || "");

            selectionHierarchy.push({
                field: barangayField,
                level: "barangay",
                lookup: lookups.barangays,
                zoom: 15
            });
            selectionHierarchy.push({
                field: municipalityField,
                level: "municipality",
                lookup: lookups.municipalities,
                zoom: 12
            });
            selectionHierarchy.push({
                field: provinceField,
                level: "province",
                lookup: lookups.provinces,
                zoom: 9
            });
            selectionHierarchy.push({
                field: regionField,
                level: "region",
                lookup: lookups.regions,
                zoom: 7
            });

            var localBest = null;
            var fetchTarget = null;

            selectionHierarchy.forEach(function (entry) {
                if (!entry.field || !entry.field.value) {
                    return;
                }

                if (!fetchTarget) {
                    fetchTarget = {
                        level: entry.level,
                        id: entry.field.value,
                        zoom: entry.zoom
                    };
                }

                if (!localBest) {
                    var record = entry.lookup.get(String(entry.field.value));
                    var lat = record ? parseNumber(record.center_lat) : null;
                    var lng = record ? parseNumber(record.center_lng) : null;
                    if (lat !== null && lng !== null) {
                        localBest = { lat: lat, lng: lng, zoom: entry.zoom };
                    }
                }
            });

            if (localBest) {
                placeMarker(localBest.lat, localBest.lng, localBest.zoom, respectExisting);
            }

            if (fetchTarget) {
                centroidRequestId += 1;
                var requestToken = centroidRequestId;
                fetchCentroid(fetchTarget.level, fetchTarget.id).then(function (payload) {
                    if (requestToken !== centroidRequestId) {
                        return;
                    }
                    if (!payload || !payload.has_location) {
                        return;
                    }
                    placeMarker(payload.lat, payload.lng, fetchTarget.zoom, respectExisting);
                });
            }
        }

        // Attach selection change handlers
        ["regionField", "provinceField", "municipalityField", "barangayField"].forEach(function (key) {
            var fieldId = container.dataset[key];
            if (!fieldId) {
                return;
            }
            var field = document.getElementById(fieldId);
            if (!field) {
                return;
            }
            field.addEventListener("change", function () {
                recenterFromSelections(true);
            });
        });

        // Initial setup
        recenterFromSelections(false);
    }

    function setupDetailMap(container) {
        var mapNode = container.querySelector("[data-google-map-target]");
        if (!mapNode) {
            return;
        }

        var dataset = container.dataset;
        var hasLocation = dataset.hasLocation === "true";

        if (!dataset.initialLat || !dataset.initialLng) {
            var fallbackLat = parseNumber(dataset.fallbackLat);
            var fallbackLng = parseNumber(dataset.fallbackLng);
            var fallbackZoom = parseNumber(dataset.fallbackZoom);

            if (fallbackLat !== null && fallbackLng !== null) {
                dataset.initialLat = String(fallbackLat);
                dataset.initialLng = String(fallbackLng);
                if (fallbackZoom !== null) {
                    dataset.initialZoom = String(fallbackZoom);
                }
            }
        }

        if (parseNumber(dataset.initialLat) === null || parseNumber(dataset.initialLng) === null) {
            dataset.initialLat = String(DEFAULT_CENTER.lat);
            dataset.initialLng = String(DEFAULT_CENTER.lng);
            if (!dataset.initialZoom) {
                dataset.initialZoom = String(DEFAULT_CENTER.zoom);
            }
        }

        var map = createMap(mapNode, dataset);
        var lat = parseNumber(dataset.initialLat);
        var lng = parseNumber(dataset.initialLng);

        if (lat === null || lng === null || !hasLocation) {
            return;
        }

        var marker = new google.maps.Marker({
            position: { lat: lat, lng: lng },
            map: map,
            title: dataset.popupContent || "OBC Location"
        });

        if (dataset.popupContent) {
            var infoWindow = new google.maps.InfoWindow({
                content: dataset.popupContent
            });

            marker.addListener('click', function() {
                infoWindow.open(map, marker);
            });
        }
    }

    function setupMultiMap(container) {
        var mapNode = container.querySelector("[data-google-map-target]");
        if (!mapNode) {
            return;
        }

        var dataset = container.dataset;
        var map = createMap(mapNode, dataset);
        var markers = [];

        var selectionField = document.getElementById(dataset.selectionField || "");
        var communityData = parseJsonScript(dataset.source) || [];
        var communityLookup = buildLookup(communityData);

        var locationData = parseJsonScript(dataset.locationScript);
        var lookups = {
            regions: buildLookup(locationData && locationData.regions),
            provinces: buildLookup(locationData && locationData.provinces),
            municipalities: buildLookup(locationData && locationData.municipalities),
            barangays: buildLookup(locationData && locationData.barangays)
        };

        function determineCommunityCoordinates(record) {
            if (!record) {
                return null;
            }
            if (record.has_location === false && !record.barangay_id && !record.municipality_id && !record.province_id && !record.region_id) {
                return null;
            }

            var lat = parseNumber(record.latitude);
            var lng = parseNumber(record.longitude);
            if (lat !== null && lng !== null) {
                return { lat: lat, lng: lng, zoom: 14 };
            }

            return findBestCoordinates(lookups, [
                { id: record.barangay_id, lookup: lookups.barangays, zoom: 15 },
                { id: record.municipality_id, lookup: lookups.municipalities, zoom: 12 },
                { id: record.province_id, lookup: lookups.provinces, zoom: 9 },
                { id: record.region_id, lookup: lookups.regions, zoom: 7 }
            ]);
        }

        function renderSelectedCommunities() {
            // Clear existing markers
            markers.forEach(function(marker) {
                marker.setMap(null);
            });
            markers = [];

            if (!selectionField) {
                return;
            }

            var selectedOptions = Array.from(selectionField.options).filter(function (option) {
                return option.selected;
            });

            var bounds = new google.maps.LatLngBounds();
            var hasBounds = false;

            selectedOptions.forEach(function (option) {
                var record = communityLookup.get(option.value);
                var coords = determineCommunityCoordinates(record);
                if (!coords) {
                    return;
                }

                var position = { lat: coords.lat, lng: coords.lng };
                var marker = new google.maps.Marker({
                    position: position,
                    map: map,
                    title: record ? record.name : option.text
                });

                var infoContent = "<div style='font-size: 14px;'><strong>" +
                    (record ? record.name : option.text) +
                    "</strong><br/><span style='color: #666;'>" +
                    (record && record.full_path ? record.full_path : "Selected OBC location") +
                    "</span></div>";

                var infoWindow = new google.maps.InfoWindow({
                    content: infoContent
                });

                marker.addListener('click', function() {
                    infoWindow.open(map, marker);
                });

                markers.push(marker);
                bounds.extend(position);
                hasBounds = true;
            });

            if (hasBounds) {
                if (markers.length === 1) {
                    map.setCenter(markers[0].getPosition());
                    map.setZoom(14);
                } else {
                    map.fitBounds(bounds);
                }
            }
        }

        function recenterFromCoverage() {
            var ids = [];
            var barangayField = document.getElementById(container.dataset.barangayField || "");
            var municipalityField = document.getElementById(container.dataset.municipalityField || "");
            var provinceField = document.getElementById(container.dataset.provinceField || "");
            var regionField = document.getElementById(container.dataset.regionField || "");

            if (barangayField && barangayField.value) {
                ids.push({ id: barangayField.value, lookup: lookups.barangays, zoom: 15 });
            }
            if (municipalityField && municipalityField.value) {
                ids.push({ id: municipalityField.value, lookup: lookups.municipalities, zoom: 12 });
            }
            if (provinceField && provinceField.value) {
                ids.push({ id: provinceField.value, lookup: lookups.provinces, zoom: 9 });
            }
            if (regionField && regionField.value) {
                ids.push({ id: regionField.value, lookup: lookups.regions, zoom: 7 });
            }

            var best = findBestCoordinates(lookups, ids);
            if (best) {
                map.setCenter({ lat: best.lat, lng: best.lng });
                map.setZoom(best.zoom);
            }
        }

        if (selectionField) {
            selectionField.addEventListener("change", renderSelectedCommunities);
        }

        [
            document.getElementById(container.dataset.regionField || ""),
            document.getElementById(container.dataset.provinceField || ""),
            document.getElementById(container.dataset.municipalityField || ""),
            document.getElementById(container.dataset.barangayField || "")
        ]
        .filter(Boolean)
        .forEach(function (field) {
            field.addEventListener("change", function () {
                if (markers.length === 0) {
                    recenterFromCoverage();
                }
            });
        });

        // Initial setup
        recenterFromCoverage();
        renderSelectedCommunities();
    }

    function initialize() {
        if (typeof google === "undefined" || !google.maps) {
            console.warn("Google Maps JavaScript API not loaded; skipping Google Maps initialization.");
            return;
        }

        var containers = document.querySelectorAll("[data-google-map]");
        containers.forEach(function (container) {
            var mode = container.dataset.mode || "detail";
            if (mode === "form") {
                setupFormMap(container);
            } else if (mode === "multi") {
                setupMultiMap(container);
            } else {
                setupDetailMap(container);
            }
        });
    }

    // Initialize when Google Maps API is ready
    if (typeof google !== "undefined" && google.maps) {
        google.maps.event.addDomListener(window, 'load', initialize);
    } else {
        document.addEventListener("DOMContentLoaded", function() {
            // Wait a bit for Google Maps to load
            setTimeout(initialize, 1000);
        });
    }

})();