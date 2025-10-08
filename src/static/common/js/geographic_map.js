(function () {
    function parseJsonScript(scriptId) {
        if (!scriptId) {
            return null;
        }
        var script = document.getElementById(scriptId);
        if (!script) {
            console.warn('Could not find JSON script with id', scriptId);
            return null;
        }
        try {
            return JSON.parse(script.textContent);
        } catch (error) {
            console.error('Failed to parse JSON payload for map', error);
            return null;
        }
    }

    function toLeafletColor(payload) {
        var styles = payload.style || {};
        if (styles.color) {
            return styles.color;
        }
        switch (payload.layer_type) {
            case 'line':
                return '#2563eb';
            case 'polygon':
                return '#10b981';
            case 'heatmap':
                return '#f97316';
            case 'cluster':
                return '#6366f1';
            default:
                return '#7c3aed';
        }
    }

    function getLayerOptions(payload) {
        var color = toLeafletColor(payload);
        var styles = payload.style || {};
        var opacity = typeof payload.opacity === 'number' ? payload.opacity : 0.85;
        opacity = Math.min(1, Math.max(0.05, opacity));

        return {
            style: function () {
                return {
                    color: styles.color || color,
                    weight: styles.weight || (payload.layer_type === 'line' ? 3 : 1.5),
                    dashArray: styles.dashArray || null,
                    fill: payload.layer_type !== 'line',
                    fillColor: styles.fillColor || styles.color || color,
                    fillOpacity: styles.fillOpacity || Math.min(0.75, Math.max(0.35, opacity)),
                    opacity: styles.opacity || opacity,
                };
            },
            pointToLayer: function (feature, latLng) {
                var radius = styles.radius || 8;
                return window.L.circleMarker(latLng, {
                    radius: radius,
                    color: styles.color || color,
                    weight: styles.weight || 2,
                    fillColor: styles.fillColor || color,
                    fillOpacity: styles.fillOpacity || Math.min(0.8, Math.max(0.45, opacity)),
                    opacity: styles.opacity || opacity,
                });
            },
            onEachFeature: function (feature, layer) {
                if (feature && feature.properties) {
                    var props = feature.properties;
                    var rows = Object.keys(props)
                        .filter(function (key) { return props[key] !== null && props[key] !== undefined; })
                        .map(function (key) {
                            return '<tr><th>' + key + '</th><td>' + props[key] + '</td></tr>';
                        });
                    if (rows.length) {
                        var html = '<div class="text-sm"><h3 class="font-semibold mb-2">' +
                            (payload.name || 'Feature details') +
                            '</h3><table class="table-auto text-xs">' + rows.join('') + '</table></div>';
                        layer.bindPopup(html);
                    }
                }
            },
        };
    }

    function updateStatus(node, message, state) {
        if (!node) {
            return;
        }
        node.textContent = message;
        node.dataset.state = state || 'idle';
    }

    function formatTileCount(status) {
        if (!status || typeof status.storagesize !== 'number') {
            return 'No tiles cached yet';
        }
        if (!status.storagesize) {
            return 'No tiles cached yet';
        }
        var count = status.storagesize;
        return count + ' cached tile' + (count === 1 ? '' : 's');
    }

    function initGeographicMap(container) {
        if (typeof window.L === 'undefined') {
            console.warn('Leaflet not available; skipping map initialisation');
            return;
        }

        var mapTargetId = container.dataset.mapTarget;
        var layersScriptId = container.dataset.layersId;
        var configScriptId = container.dataset.configId;
        var mapRoot = document.getElementById(mapTargetId);

        if (!mapRoot) {
            console.warn('Unable to locate map element:', mapTargetId);
            return;
        }

        var layerPayloads = parseJsonScript(layersScriptId) || [];
        var mapConfig = parseJsonScript(configScriptId) || {};
        if (!mapConfig.tile_url) {
            mapConfig.tile_url = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
        }

        var map = window.L.map(mapRoot, {
            zoomControl: true,
            preferCanvas: true,
        });

        var tileOptions = {
            minZoom: mapConfig.min_zoom || 3,
            maxZoom: mapConfig.max_zoom || 18,
            attribution: mapConfig.tile_attribution || ''
        };

        if (mapConfig.tile_subdomains) {
            tileOptions.subdomains = mapConfig.tile_subdomains;
        }
        tileOptions.crossOrigin = true;

        var baseLayer;
        if (window.L.tileLayer && window.L.tileLayer.offline) {
            baseLayer = window.L.tileLayer.offline(mapConfig.tile_url, tileOptions);
        } else {
            baseLayer = window.L.tileLayer(mapConfig.tile_url, tileOptions);
        }

        baseLayer.addTo(map);

        var offlineControl = null;
        var statusNode = container.querySelector('[data-map-status]');

        if (window.L.control && typeof window.L.control.savetiles === 'function' && baseLayer) {
            var offlineOptions = mapConfig.offline || {};
            offlineControl = window.L.control.savetiles(baseLayer, {
                position: 'topright',
                saveText: '<i class="fas fa-download"></i>',
                rmText: '<i class="fas fa-trash"></i>',
                maxZoom: offlineOptions.max_zoom || (mapConfig.max_zoom || 18),
                saveWhatYouSee: offlineOptions.save_what_you_see !== false,
                parallel: offlineOptions.max_parallel_downloads || 6,
            });
            offlineControl.addTo(map);

            updateStatus(statusNode, 'Preparing offline map…');

            baseLayer.on('storagesize', function (status) {
                updateStatus(statusNode, formatTileCount(status));
            });
            baseLayer.on('savestart', function () {
                updateStatus(statusNode, 'Caching tiles…', 'saving');
            });
            baseLayer.on('saveend', function (status) {
                updateStatus(statusNode, 'Cached ' + (status.lengthSaved || 0) + ' tiles', 'success');
                offlineControl.setStorageSize();
            });
            baseLayer.on('loadtileend', function (status) {
                updateStatus(statusNode, 'Downloading tiles: ' + status.lengthLoaded + ' / ' + status.lengthToBeSaved, 'saving');
            });
            baseLayer.on('tilesremoved', function () {
                updateStatus(statusNode, 'Cache cleared');
            });
            baseLayer.on('error', function () {
                updateStatus(statusNode, 'Tile caching failed', 'error');
            });
            if (typeof offlineControl.setStorageSize === 'function') {
                offlineControl.setStorageSize();
            }
        } else {
            updateStatus(statusNode, 'Offline caching unavailable');
        }

        var overlayMap = {};

        layerPayloads.forEach(function (payload) {
            if (!payload || !payload.geojson) {
                return;
            }
            try {
                var options = getLayerOptions(payload);
                var layer = window.L.geoJSON(payload.geojson, options);
                if (payload.opacity !== undefined && typeof layer.setStyle === 'function') {
                    layer.setStyle({ opacity: payload.opacity, fillOpacity: Math.min(0.9, Math.max(0.3, payload.opacity)) });
                }
                if (payload.is_visible !== false) {
                    layer.addTo(map);
                }
                overlayMap[payload.name || ('Layer ' + payload.id)] = layer;
            } catch (error) {
                console.error('Failed to render layer', payload, error);
            }
        });

        window.L.control.layers({
            'OpenStreetMap': baseLayer,
        }, overlayMap, {
            collapsed: false,
        }).addTo(map);

        if (mapConfig.bounds) {
            map.fitBounds(mapConfig.bounds, { padding: [20, 20] });
        } else if (mapConfig.default_center) {
            var defaultCenter = mapConfig.default_center;
            map.setView(defaultCenter, mapConfig.default_zoom || 7);
        } else {
            map.setView([7.1907, 124.2197], 7);
        }

        var prefetchButton = container.querySelector('button[data-action="prefetch"]');
        if (prefetchButton && offlineControl) {
            prefetchButton.addEventListener('click', function () {
                try {
                    offlineControl._saveTiles();
                } catch (error) {
                    console.error('Failed to cache tiles', error);
                    updateStatus(statusNode, 'Could not cache tiles for offline use', 'error');
                }
            });
        }

        var clearButton = container.querySelector('button[data-action="clear"]');
        if (clearButton && offlineControl) {
            clearButton.addEventListener('click', function () {
                try {
                    offlineControl._rmTiles();
                } catch (error) {
                    console.error('Failed to clear cached tiles', error);
                    updateStatus(statusNode, 'Could not clear cached tiles', 'error');
                }
            });
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        var containers = document.querySelectorAll('[data-geographic-map]');
        containers.forEach(function (container) {
            initGeographicMap(container);
        });
    });
})();
