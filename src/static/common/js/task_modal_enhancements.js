(function (global) {
    const COLOR_CONFIG = {
        status: {
            removeSelect: [
                'bg-white',
                'text-gray-700',
                'border-gray-200',
                'bg-emerald-50',
                'text-emerald-700',
                'border-emerald-200',
                'bg-blue-50',
                'text-blue-700',
                'border-blue-200',
                'bg-amber-50',
                'text-amber-700',
                'border-amber-200',
                'bg-rose-50',
                'text-rose-700',
                'border-rose-200',
                'bg-slate-100',
                'text-slate-600',
                'border-slate-200',
            ],
            removePill: [
                'bg-emerald-100',
                'text-emerald-700',
                'border-emerald-200',
                'bg-blue-100',
                'text-blue-700',
                'border-blue-200',
                'bg-amber-100',
                'text-amber-700',
                'border-amber-200',
                'bg-rose-100',
                'text-rose-700',
                'border-rose-200',
                'bg-slate-100',
                'text-slate-600',
                'border-slate-200',
            ],
            map: {
                completed: {
                    select: ['bg-emerald-50', 'text-emerald-700', 'border-emerald-200'],
                    pill: ['bg-emerald-100', 'text-emerald-700', 'border-emerald-200'],
                },
                at_risk: {
                    select: ['bg-rose-50', 'text-rose-700', 'border-rose-200'],
                    pill: ['bg-rose-100', 'text-rose-700', 'border-rose-200'],
                },
                in_progress: {
                    select: ['bg-blue-50', 'text-blue-700', 'border-blue-200'],
                    pill: ['bg-blue-100', 'text-blue-700', 'border-blue-200'],
                },
                not_started: {
                    select: ['bg-amber-50', 'text-amber-700', 'border-amber-200'],
                    pill: ['bg-amber-100', 'text-amber-700', 'border-amber-200'],
                },
                default: {
                    select: ['bg-white', 'text-gray-700', 'border-gray-200'],
                    pill: ['bg-slate-100', 'text-slate-600', 'border-slate-200'],
                },
            },
        },
        priority: {
            removeSelect: [
                'bg-white',
                'text-gray-700',
                'border-gray-200',
                'bg-emerald-50',
                'text-emerald-700',
                'border-emerald-200',
                'bg-blue-50',
                'text-blue-700',
                'border-blue-200',
                'bg-amber-50',
                'text-amber-700',
                'border-amber-200',
                'bg-rose-50',
                'text-rose-700',
                'border-rose-200',
                'bg-slate-100',
                'text-slate-600',
                'border-slate-200',
            ],
            removePill: [
                'bg-emerald-100',
                'text-emerald-700',
                'border-emerald-200',
                'bg-blue-100',
                'text-blue-700',
                'border-blue-200',
                'bg-amber-100',
                'text-amber-700',
                'border-amber-200',
                'bg-rose-100',
                'text-rose-700',
                'border-rose-200',
                'bg-slate-100',
                'text-slate-600',
                'border-slate-200',
            ],
            map: {
                critical: {
                    select: ['bg-rose-50', 'text-rose-700', 'border-rose-200'],
                    pill: ['bg-rose-100', 'text-rose-700', 'border-rose-200'],
                },
                high: {
                    select: ['bg-amber-50', 'text-amber-700', 'border-amber-200'],
                    pill: ['bg-amber-100', 'text-amber-700', 'border-amber-200'],
                },
                medium: {
                    select: ['bg-blue-50', 'text-blue-700', 'border-blue-200'],
                    pill: ['bg-blue-100', 'text-blue-700', 'border-blue-200'],
                },
                low: {
                    select: ['bg-slate-100', 'text-slate-600', 'border-slate-200'],
                    pill: ['bg-slate-100', 'text-slate-600', 'border-slate-200'],
                },
                default: {
                    select: ['bg-white', 'text-gray-700', 'border-gray-200'],
                    pill: ['bg-slate-100', 'text-slate-600', 'border-slate-200'],
                },
            },
        },
    };

    const choicesCallbacks = [];
    let choicesLoading = false;

    function swapClasses(element, removeClasses, addClasses) {
        if (!element) {
            return;
        }
        removeClasses.forEach(cls => element.classList.remove(cls));
        addClasses.forEach(cls => element.classList.add(cls));
    }

    function updateColorSelect(select) {
        const variant = select.dataset.colorSelect;
        const config = COLOR_CONFIG[variant];
        if (!config) {
            return;
        }

        const selectedOption = select.options[select.selectedIndex];
        const value = (selectedOption && selectedOption.value) || 'default';
        const style = config.map[value] || config.map.default;

        swapClasses(select, config.removeSelect, style.select);

        const group = select.closest('[data-select-group]');
        const pill = group ? group.querySelector('[data-select-pill]') : null;
        const labelTarget = pill ? pill.querySelector('[data-pill-label]') || pill : null;
        if (pill) {
            swapClasses(pill, config.removePill, style.pill);
        }
        if (labelTarget && selectedOption) {
            labelTarget.textContent = selectedOption.text.trim();
        }
    }

    function bindColorSelect(select) {
        if (select.dataset.colorSelectBound === 'true') {
            updateColorSelect(select);
            return;
        }
        select.addEventListener('change', function () {
            updateColorSelect(select);
        });
        updateColorSelect(select);
        select.dataset.colorSelectBound = 'true';
    }

    function ensureChoicesAssets(callback) {
        if (typeof global.Choices === 'function') {
            callback();
            return;
        }

        choicesCallbacks.push(callback);
        if (choicesLoading) {
            return;
        }
        choicesLoading = true;

        if (!document.querySelector('link[data-choices-asset]')) {
            const stylesheet = document.createElement('link');
            stylesheet.rel = 'stylesheet';
            stylesheet.href = 'https://cdn.jsdelivr.net/npm/choices.js@10.2.0/public/assets/styles/choices.min.css';
            stylesheet.dataset.choicesAsset = 'true';
            document.head.appendChild(stylesheet);
        }

        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/choices.js@10.2.0/public/assets/scripts/choices.min.js';
        script.async = true;
        script.dataset.choicesAsset = 'true';
        script.addEventListener('load', function () {
            const callbacks = choicesCallbacks.splice(0, choicesCallbacks.length);
            callbacks.forEach(fn => {
                try {
                    fn();
                } catch (error) {
                    console.warn('Choices callback failed', error);
                }
            });
        });
        document.head.appendChild(script);
    }

    function updateSelectedCount(select) {
        const group = select.closest('[data-multiselect-group]');
        if (!group) {
            return;
        }
        const counter = group.querySelector('[data-selected-count]');
        if (!counter) {
            return;
        }
        const singular = select.dataset.singularLabel || 'item';
        const plural = select.dataset.pluralLabel || (singular.endsWith('s') ? singular : singular + 's');
        const emptyLabel = select.dataset.emptyLabel || 'None selected';
        const count = select.selectedOptions ? select.selectedOptions.length : 0;

        if (!count) {
            counter.textContent = emptyLabel;
            return;
        }

        const label = count === 1 ? singular : plural;
        counter.textContent = `${count} ${label}`;
    }

    function enhanceMultiselect(select) {
        const initialise = function () {
            if (select.dataset.choicesInitialized === 'true') {
                updateSelectedCount(select);
                return;
            }

            const instance = new global.Choices(select, {
                removeItemButton: true,
                shouldSort: false,
                placeholder: true,
                placeholderValue: select.dataset.placeholder || 'Select options',
                searchPlaceholderValue: select.dataset.searchPlaceholder || 'Search...',
                itemSelectText: '',
                classNames: {
                    containerOuter: 'choices task-modal-choices',
                },
            });

            select.dataset.choicesInitialized = 'true';
            select.choicesInstance = instance;

            const handleSelectionChange = function () {
                updateSelectedCount(select);
            };

            select.addEventListener('change', handleSelectionChange);
            select.addEventListener('addItem', handleSelectionChange);
            select.addEventListener('removeItem', handleSelectionChange);

            updateSelectedCount(select);
        };

        ensureChoicesAssets(initialise);
    }

    function setupColorSelects(root) {
        const selects = root.querySelectorAll('[data-color-select]');
        selects.forEach(bindColorSelect);
    }

    function setupMultiselects(root) {
        const selects = root.querySelectorAll('[data-enhanced-multiselect]');
        selects.forEach(enhanceMultiselect);
    }

    function setupDeleteButton(root) {
        const deleteTrigger = root.querySelector('[data-delete-trigger]');
        const deleteConfirm = root.querySelector('[data-delete-confirm]');
        const deleteCancel = root.querySelector('[data-delete-cancel]');

        if (!deleteTrigger || !deleteConfirm) {
            return;
        }

        // Show delete confirmation when Delete button is clicked
        deleteTrigger.addEventListener('click', function (e) {
            e.preventDefault();
            deleteConfirm.classList.remove('hidden');
            deleteTrigger.classList.add('hidden');
        });

        // Hide delete confirmation when Cancel is clicked
        if (deleteCancel) {
            deleteCancel.addEventListener('click', function (e) {
                e.preventDefault();
                deleteConfirm.classList.add('hidden');
                deleteTrigger.classList.remove('hidden');
            });
        }
    }

    function init(root) {
        const container = root || document.getElementById('taskModalContent');
        if (!container) {
            return;
        }
        setupColorSelects(container);
        setupMultiselects(container);
        setupDeleteButton(container);
    }

    global.taskModalEnhancer = global.taskModalEnhancer || {};
    global.taskModalEnhancer.init = init;
    global.taskModalEnhancer.refresh = init;
})(window);
