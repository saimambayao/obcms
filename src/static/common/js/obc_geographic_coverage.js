(function () {
document.addEventListener('DOMContentLoaded', () => {
    const locationDataElement = document.getElementById('location-data');
    const communityDataElement = document.getElementById('community-locations');
    const coverageRowsContainer = document.getElementById('coverage-rows');
    if (!locationDataElement || !communityDataElement || !coverageRowsContainer) {
        return;
    }

    let locationData;
    try {
        locationData = JSON.parse(locationDataElement.textContent);
    } catch (error) {
        console.error('Unable to parse location data for coverage selectors.', error);
        return;
    }

    let communityData = [];
    try {
        communityData = JSON.parse(communityDataElement.textContent) || [];
    } catch (error) {
        console.warn('Unable to parse community lookup data.', error);
    }

    const mapByKey = (items, keyFn) => {
        const map = new Map();
        (items || []).forEach(item => {
            const key = String(keyFn(item));
            if (!map.has(key)) {
                map.set(key, []);
            }
            map.get(key).push(item);
        });
        return map;
    };

    const provincesByRegion = mapByKey(locationData.provinces, province => province.region_id);
    const municipalitiesByProvince = mapByKey(locationData.municipalities, municipality => municipality.province_id);
    const barangaysByMunicipality = mapByKey(locationData.barangays, barangay => barangay.municipality_id);

    const toStringId = value => (value === null || value === undefined ? '' : String(value));

    const autoMunicipalityByProvince = new Map();
    (locationData.provinces || []).forEach(province => {
        const provinceKey = toStringId(province.id);
        if (!provinceKey) {
            return;
        }
        const autoMunicipalityId = province.auto_municipality_id;
        const isPseudo = Boolean(province.is_pseudo_province) || Boolean(autoMunicipalityId);
        if (!isPseudo) {
            return;
        }
        if (autoMunicipalityId !== null && autoMunicipalityId !== undefined) {
            autoMunicipalityByProvince.set(provinceKey, toStringId(autoMunicipalityId));
            return;
        }
        const options = municipalitiesByProvince.get(provinceKey) || [];
        if (!options.length) {
            return;
        }
        const independentCity = options.find(
            municipality => municipality.municipality_type === 'independent_city'
        );
        const target = independentCity || options[0];
        if (target && target.id !== undefined && target.id !== null) {
            autoMunicipalityByProvince.set(provinceKey, toStringId(target.id));
        }
    });

    const setOptions = (select, options, placeholder, selectedValue, labelFn) => {
        if (!select) {
            return;
        }

        const desired = toStringId(selectedValue);
        const fragment = document.createDocumentFragment();

        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = placeholder;
        fragment.appendChild(placeholderOption);

        (options || []).forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = String(option.id);
            optionElement.textContent = labelFn ? labelFn(option) : option.name;
            if (Object.prototype.hasOwnProperty.call(option, 'code') && option.code) {
                optionElement.dataset.code = option.code;
            }
            if (
                Object.prototype.hasOwnProperty.call(option, 'is_pseudo_province') &&
                option.is_pseudo_province
            ) {
                optionElement.dataset.isPseudoProvince = 'true';
            }
            if (
                Object.prototype.hasOwnProperty.call(option, 'municipality_type') &&
                option.municipality_type
            ) {
                optionElement.dataset.municipalityType = option.municipality_type;
            }
            fragment.appendChild(optionElement);
        });

        select.innerHTML = '';
        select.appendChild(fragment);

        const hasDesired = (options || []).some(option => String(option.id) === desired);
        select.value = hasDesired ? desired : '';
    };

    const communitiesSelect = document.getElementById('id_communities');
    const communityById = new Map();
    const communityByBarangay = new Map();
    const municipalityCommunityById = new Map();

    communityData.forEach(community => {
        const id = String(community.id);
        communityById.set(id, community);
        if (community.type === 'community' && community.barangay_id) {
            communityByBarangay.set(String(community.barangay_id), community);
        }
        if (community.type === 'municipality' && community.municipality_id) {
            municipalityCommunityById.set(String(community.municipality_id), community);
        }
    });

    const buildCommunityLabel = community => {
        const locationBits = [];
        if (community.barangay_name) {
            locationBits.push(community.barangay_name);
        }
        if (community.municipality_name) {
            locationBits.push(community.municipality_name);
        }
        if (community.province_name) {
            locationBits.push(community.province_name);
        }
        return locationBits.length ? `${community.name} • ${locationBits.join(', ')}` : community.name;
    };

    const ensureCommunityOption = community => {
        if (!communitiesSelect || !community) {
            return null;
        }
        let option = Array.from(communitiesSelect.options).find(opt => opt.value === String(community.id));
        if (option) {
            option.textContent = option.textContent || buildCommunityLabel(community);
            return option;
        }
        option = document.createElement('option');
        option.value = String(community.id);
        option.textContent = buildCommunityLabel(community);
        option.dataset.regionName = community.region_name || '';
        option.dataset.provinceName = community.province_name || '';
        option.dataset.municipalityName = community.municipality_name || '';
        option.dataset.barangayName = community.barangay_name || '';
        communitiesSelect.appendChild(option);
        return option;
    };

    const setCommunitySelected = (communityId, shouldSelect, community) => {
        if (!communitiesSelect || !communityId) {
            return;
        }
        const details = community || communityById.get(String(communityId));
        if (!details) {
            return;
        }
        const option = ensureCommunityOption(details);
        if (option) {
            option.selected = shouldSelect;
        }
    };

    const communitySelectionCounts = new Map();

    const adjustCommunitySelection = (communityId, delta, community) => {
        if (!communityId || delta === 0) {
            return;
        }
        const current = communitySelectionCounts.get(communityId) || 0;
        const next = current + delta;
        if (next <= 0) {
            communitySelectionCounts.delete(communityId);
            setCommunitySelected(communityId, false, community);
        } else {
            communitySelectionCounts.set(communityId, next);
            setCommunitySelected(communityId, true, community);
        }
    };

    const dispatchCommunityChange = () => {
        if (!communitiesSelect) {
            return;
        }
        communitiesSelect.dispatchEvent(new Event('change', { bubbles: true }));
    };

    const activateCoverageMap = (mapContainer, selectors) => {
        if (!mapContainer || typeof window === 'undefined' || !window.OBCMaps) {
            return;
        }
        const mapAPI = window.OBCMaps;
        if (selectors) {
            mapAPI.initCoverageMap(mapContainer, selectors);
        } else {
            mapAPI.initContainer(mapContainer);
        }
        if (typeof mapAPI.refreshCoverage === 'function') {
            mapAPI.refreshCoverage(mapContainer);
        }
    };

    const setupLocationSelectors = (selects, initial = {}) => {
        const { regionSelect, provinceSelect, municipalitySelect, barangaySelect } = selects;
        if (!regionSelect) {
            return;
        }

        const getPlaceholder = (element, fallback) =>
            element && element.dataset && element.dataset.placeholder ? element.dataset.placeholder : fallback;

        const regionPlaceholder = getPlaceholder(regionSelect, 'Select region...');
        const provincePlaceholder = getPlaceholder(provinceSelect, 'Select province...');
        const municipalityPlaceholder = getPlaceholder(municipalitySelect, 'Select municipality / city...');
        const barangayPlaceholder = getPlaceholder(barangaySelect, 'Select barangay...');

        const regionLabel = region => (region && region.code ? `Region ${region.code} - ${region.name}` : region.name);

        const initialRegion = toStringId(initial.region || (regionSelect.dataset.initial || regionSelect.value));
        const initialProvince = toStringId(initial.province || (provinceSelect && (provinceSelect.dataset.initial || provinceSelect.value)));
        const initialMunicipality = toStringId(initial.municipality || (municipalitySelect && (municipalitySelect.dataset.initial || municipalitySelect.value)));
        const initialBarangay = toStringId(initial.barangay || (barangaySelect && (barangaySelect.dataset.initial || barangaySelect.value)));

        const updateProvinceOptions = (regionId, selectedValue) => {
            const options = regionId ? provincesByRegion.get(toStringId(regionId)) || [] : [];
            setOptions(provinceSelect, options, provincePlaceholder, selectedValue);
        };

        const updateMunicipalityOptions = (provinceId, selectedValue) => {
            const options = provinceId ? municipalitiesByProvince.get(toStringId(provinceId)) || [] : [];
            setOptions(municipalitySelect, options, municipalityPlaceholder, selectedValue);
        };

        const updateBarangayOptions = (municipalityId, selectedValue) => {
            const options = municipalityId ? barangaysByMunicipality.get(toStringId(municipalityId)) || [] : [];
            setOptions(barangaySelect, options, barangayPlaceholder, selectedValue);
        };

        const autoSelectMunicipalityForProvince = (shouldDispatch = true) => {
            if (!provinceSelect || !municipalitySelect) {
                return false;
            }
            const provinceId = toStringId(provinceSelect.value);
            if (!provinceId) {
                return false;
            }
            const targetMunicipalityId = autoMunicipalityByProvince.get(provinceId);
            if (!targetMunicipalityId) {
                return false;
            }
            const hasOption = Array.from(municipalitySelect.options || []).some(
                option => option.value === targetMunicipalityId
            );
            if (!hasOption) {
                return false;
            }
            if (municipalitySelect.value !== targetMunicipalityId) {
                municipalitySelect.value = targetMunicipalityId;
            }
            if (shouldDispatch) {
                municipalitySelect.dispatchEvent(new Event('change'));
            }
            return true;
        };

        setOptions(regionSelect, locationData.regions || [], regionPlaceholder, initialRegion, regionLabel);
        updateProvinceOptions(initialRegion, initialProvince);
        updateMunicipalityOptions(initialProvince, initialMunicipality);
        updateBarangayOptions(initialMunicipality, initialBarangay);

        regionSelect.addEventListener('change', () => {
            updateProvinceOptions(regionSelect.value, '');
            updateMunicipalityOptions('', '');
            updateBarangayOptions('', '');
        });

        if (provinceSelect) {
            provinceSelect.addEventListener('change', () => {
                updateMunicipalityOptions(provinceSelect.value, '');
                const autoHandled = autoSelectMunicipalityForProvince();
                if (!autoHandled) {
                    updateBarangayOptions('', '');
                }
            });
        }

        if (municipalitySelect) {
            municipalitySelect.addEventListener('change', () => {
                updateBarangayOptions(municipalitySelect.value, '');
            });
        }

        if (!initialMunicipality) {
            autoSelectMunicipalityForProvince();
        }
    };

    const updateRowCommunity = (rowState, barangayId, municipalityId) => {
        if (rowState.communityId) {
            adjustCommunitySelection(rowState.communityId, -1);
            rowState.communityId = '';
        }
        if (!barangayId && !municipalityId) {
            return;
        }
        if (barangayId) {
            const community = communityByBarangay.get(String(barangayId));
            if (community) {
                const communityId = String(community.id);
                adjustCommunitySelection(communityId, 1, community);
                rowState.communityId = communityId;
                return;
            }
        }
        if (municipalityId) {
            const municipalityRecord = municipalityCommunityById.get(String(municipalityId));
            if (municipalityRecord) {
                const municipalityKey = String(municipalityRecord.id);
                adjustCommunitySelection(municipalityKey, 1, municipalityRecord);
                rowState.communityId = municipalityKey;
            }
        }
    };

    const bindLocationListeners = (regionSelect, provinceSelect, municipalitySelect, barangaySelect, rowState) => {
        const handleChange = () => {
            updateRowCommunity(rowState, barangaySelect ? barangaySelect.value : '', municipalitySelect ? municipalitySelect.value : '');
            dispatchCommunityChange();
        };

        [regionSelect, provinceSelect, municipalitySelect, barangaySelect]
            .filter(Boolean)
            .forEach(select => {
                select.addEventListener('change', handleChange);
            });

        handleChange();
    };

    const primaryRegion = document.getElementById('id_coverage_region');
    const primaryProvince = document.getElementById('id_coverage_province');
    const primaryMunicipality = document.getElementById('id_coverage_municipality');
    const primaryBarangay = document.getElementById('id_coverage_barangay');
    const primaryMapContainer = document.querySelector('[data-coverage-map="primary"]');

    const initialCommunities = communitiesSelect
        ? Array.from(communitiesSelect.options)
              .filter(option => option.selected)
              .map(option => communityById.get(String(option.value)))
              .filter(Boolean)
        : [];

    if (initialCommunities.length && primaryBarangay && !primaryBarangay.value) {
        const firstCommunity = initialCommunities[0];
        if (firstCommunity) {
            if (primaryRegion && !primaryRegion.value && firstCommunity.region_id) {
                primaryRegion.dataset.initial = firstCommunity.region_id;
            }
            if (primaryProvince && !primaryProvince.value && firstCommunity.province_id) {
                primaryProvince.dataset.initial = firstCommunity.province_id;
            }
            if (primaryMunicipality && !primaryMunicipality.value && firstCommunity.municipality_id) {
                primaryMunicipality.dataset.initial = firstCommunity.municipality_id;
            }
            if (primaryBarangay && !primaryBarangay.value && firstCommunity.barangay_id) {
                primaryBarangay.dataset.initial = firstCommunity.barangay_id;
            }
        }
    }

    setupLocationSelectors({
        regionSelect: primaryRegion,
        provinceSelect: primaryProvince,
        municipalitySelect: primaryMunicipality,
        barangaySelect: primaryBarangay,
    });

    const primaryRowState = { communityId: '' };
    bindLocationListeners(primaryRegion, primaryProvince, primaryMunicipality, primaryBarangay, primaryRowState);
    activateCoverageMap(primaryMapContainer);

    const template = document.getElementById('coverage-row-template');
    const additionalRowsContainer = document.getElementById('additional-coverage-rows');
    const addRowButton = document.getElementById('add-coverage-row');
    if (!additionalRowsContainer) {
        return;
    }
    const minRowsRaw = additionalRowsContainer.dataset.minRows;
    const MIN_ROWS = Math.max(1, parseInt(minRowsRaw || '1', 10));

    const totalRows = () => 1 + additionalRowsContainer.querySelectorAll('[data-coverage-row]').length;

    const enforceRemovalState = () => {
        const removable = totalRows() > MIN_ROWS;
        additionalRowsContainer.querySelectorAll('[data-action="remove-row"]').forEach(button => {
            button.disabled = !removable;
            button.classList.toggle('opacity-50', !removable);
            button.classList.toggle('cursor-not-allowed', !removable);
        });
    };

    const removeCoverageRow = (row, rowState) => {
        if (totalRows() <= MIN_ROWS) {
            return;
        }
        updateRowCommunity(rowState, '');
        row.remove();
        enforceRemovalState();
        dispatchCommunityChange();
    };

    const createCoverageRow = initialCommunity => {
        if (!template || !additionalRowsContainer) {
            return null;
        }
        const fragment = template.content.cloneNode(true);
        const row = fragment.querySelector('[data-coverage-row]');
        const regionSelect = row.querySelector('[data-field="region"]');
        const provinceSelect = row.querySelector('[data-field="province"]');
        const municipalitySelect = row.querySelector('[data-field="municipality"]');
        const barangaySelect = row.querySelector('[data-field="barangay"]');

        const initials = initialCommunity
            ? {
                  region: initialCommunity.region_id,
                  province: initialCommunity.province_id,
                  municipality: initialCommunity.municipality_id,
                  barangay: initialCommunity.barangay_id,
              }
            : {};

        setupLocationSelectors({
            regionSelect,
            provinceSelect,
            municipalitySelect,
            barangaySelect,
        }, initials);

        const rowState = { communityId: '' };
        bindLocationListeners(regionSelect, provinceSelect, municipalitySelect, barangaySelect, rowState);

        const mapContainer = row.querySelector('[data-coverage-map]');

        additionalRowsContainer.appendChild(row);

        activateCoverageMap(mapContainer, {
            regionSelect,
            provinceSelect,
            municipalitySelect,
            barangaySelect,
        });

        if (initialCommunity && initialCommunity.barangay_id) {
            barangaySelect.value = toStringId(initialCommunity.barangay_id);
            barangaySelect.dispatchEvent(new Event('change'));
        } else if (initialCommunity && initialCommunity.municipality_id) {
            municipalitySelect.value = toStringId(initialCommunity.municipality_id);
            municipalitySelect.dispatchEvent(new Event('change'));
        }

        const removeButton = row.querySelector('[data-action="remove-row"]');
        if (removeButton) {
            removeButton.addEventListener('click', () => removeCoverageRow(row, rowState));
        }

        enforceRemovalState();
        return row;
    };

    const extraRowsNeeded = Math.max(MIN_ROWS - 1, initialCommunities.length - 1);
    for (let index = 0; index < extraRowsNeeded; index += 1) {
        const community = initialCommunities[index + 1] || null;
        createCoverageRow(community);
    }

    if (addRowButton) {
        addRowButton.addEventListener('click', () => {
            const newRow = createCoverageRow(null);
            if (newRow) {
                const firstSelect = newRow.querySelector('[data-field="region"]');
                if (firstSelect) {
                    firstSelect.focus();
                }
            }
        });
    }

    enforceRemovalState();
    dispatchCommunityChange();

    const saveLocationsButton = document.getElementById('save-obc-locations');
    if (saveLocationsButton) {
        saveLocationsButton.addEventListener('click', () => {
            saveLocationsButton.classList.add('bg-emerald-700');
            setTimeout(() => saveLocationsButton.classList.remove('bg-emerald-700'), 600);
        });
    }

    const formElement = document.querySelector('.obc-form');
    if (formElement && communitiesSelect) {
        formElement.addEventListener('submit', () => {
            Array.from(communitiesSelect.options)
                .filter(option => option.value.startsWith('municipality-'))
                .forEach(option => {
                    option.selected = false;
                });
        });
    }
});
})();
