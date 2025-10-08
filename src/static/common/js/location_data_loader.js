(function () {
    "use strict";

    if (typeof window === "undefined") {
        return;
    }

    window.OBC = window.OBC || {};

    if (typeof window.OBC.fetchLocationData === "function") {
        return;
    }

    var cache = new Map();

    function normaliseBoolean(value, fallback) {
        if (value === undefined || value === null || value === "") {
            return fallback;
        }
        if (typeof value === "boolean") {
            return value;
        }
        var normalised = String(value).toLowerCase();
        if (normalised === "false" || normalised === "0" || normalised === "no") {
            return false;
        }
        if (normalised === "true" || normalised === "1" || normalised === "yes") {
            return true;
        }
        return fallback;
    }

    function buildCacheKey(apiUrl, includeBarangays) {
        return apiUrl + "::" + (includeBarangays ? "with" : "without");
    }

    function extractApiUrl(container) {
        if (container && container.dataset && container.dataset.locationApi) {
            return container.dataset.locationApi;
        }
        var body = document.body || null;
        if (body && body.dataset && body.dataset.locationApi) {
            return body.dataset.locationApi;
        }
        if (typeof window.OBCLocationApi === "string") {
            return window.OBCLocationApi;
        }
        return null;
    }

    function requestLocationData(apiUrl, includeBarangays) {
        var cacheKey = buildCacheKey(apiUrl, includeBarangays);
        if (cache.has(cacheKey)) {
            return cache.get(cacheKey);
        }

        var url;
        try {
            url = new URL(apiUrl, window.location.origin);
        } catch (error) {
            console.error("Invalid location-data API URL", apiUrl, error);
            return Promise.resolve(null);
        }

        url.searchParams.set("include_barangays", includeBarangays ? "1" : "0");

        var promise = fetch(url.toString(), {
            method: "GET",
            credentials: "same-origin",
            headers: {
                "Accept": "application/json",
            },
        })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("Location-data API returned status " + response.status);
                }
                return response.json();
            })
            .catch(function (error) {
                console.error("Failed to fetch location data", error);
                return null;
            });

        cache.set(cacheKey, promise);
        return promise;
    }

    function parseInlineScript(container) {
        if (!container || !container.dataset || !container.dataset.locationScript) {
            return null;
        }
        var script = document.getElementById(container.dataset.locationScript);
        if (!script) {
            return null;
        }
        try {
            return JSON.parse(script.textContent || "null");
        } catch (error) {
            console.error("Failed to parse inline location data", error);
            return null;
        }
    }

    function fetchLocationData(options) {
        options = options || {};
        var container = options.container || null;
        var includeBarangays = normaliseBoolean(options.includeBarangays, true);

        var inlineData = parseInlineScript(container);
        if (inlineData) {
            return Promise.resolve(inlineData);
        }

        var apiUrl = extractApiUrl(container);
        if (!apiUrl) {
            console.warn("No location-data API endpoint configured.");
            return Promise.resolve(null);
        }

        return requestLocationData(apiUrl, includeBarangays);
    }

    window.OBC.fetchLocationData = fetchLocationData;
})();
