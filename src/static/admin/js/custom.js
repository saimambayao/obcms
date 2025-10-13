(function () {
  document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.obc-admin-button, .button, input[type="submit"], input[type="button"]');
    buttons.forEach(function (button) {
      button.addEventListener('mouseenter', function () {
        this.style.transform = 'translateY(-2px)';
      });
      button.addEventListener('mouseleave', function () {
        this.style.transform = 'translateY(0)';
      });
    });

    const messages = document.querySelectorAll('.messagelist li');
    messages.forEach(function (message) {
      message.classList.add('obc-fade-enter');
      setTimeout(function () {
        message.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        message.style.opacity = '0';
        message.style.transform = 'translateY(-8px)';
        setTimeout(function () {
          message.remove();
        }, 300);
      }, 6000);
    });

    const toggleFilters = document.getElementById('toggle-filters');
    const sidebar = document.getElementById('changelist-filter');
    if (toggleFilters && sidebar) {
      toggleFilters.addEventListener('click', function () {
        const icon = toggleFilters.querySelector('i');
        sidebar.hidden = !sidebar.hidden;
        toggleFilters.setAttribute('aria-expanded', (!sidebar.hidden).toString());
        if (icon) {
          icon.classList.toggle('fa-filter-circle-xmark', !sidebar.hidden);
          icon.classList.toggle('fa-filter', sidebar.hidden);
        }
      });
    }

    const selectAllCheckbox = document.querySelector('.action-select-all');
    const actionCheckboxes = document.querySelectorAll('.action-checkbox');
    if (selectAllCheckbox && actionCheckboxes.length) {
      selectAllCheckbox.addEventListener('change', function () {
        const checked = selectAllCheckbox.checked;
        actionCheckboxes.forEach(function (checkbox) {
          checkbox.checked = checked;
        });
      });

      actionCheckboxes.forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
          const checkedCount = document.querySelectorAll('.action-checkbox:checked').length;
          selectAllCheckbox.checked = checkedCount === actionCheckboxes.length;
          selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < actionCheckboxes.length;
        });
      });
    }

    const submitButtons = document.querySelectorAll('form button[type="submit"], form input[type="submit"]');
    submitButtons.forEach(function (submitButton) {
      submitButton.addEventListener('click', function () {
        const form = submitButton.closest('form');
        const originalText = submitButton.value || submitButton.innerText;
        submitButton.setAttribute('data-original-text', originalText);
        if (submitButton.tagName === 'INPUT') {
          submitButton.value = 'Processing…';
        } else {
          submitButton.innerText = 'Processing…';
        }
        submitButton.setAttribute('disabled', 'disabled');
        submitButton.classList.add('is-loading');
        if (form) {
          form.classList.add('obc-form-submitted');
        }
        setTimeout(function () {
          submitButton.removeAttribute('disabled');
          submitButton.classList.remove('is-loading');
          if (submitButton.tagName === 'INPUT') {
            submitButton.value = submitButton.getAttribute('data-original-text');
          } else {
            submitButton.innerText = submitButton.getAttribute('data-original-text');
          }
        }, 4000);
      });
    });

    const adminForms = document.querySelectorAll('form[id$="_form"], .change-list #changelist-form');
    adminForms.forEach(function (form) {
      const trackedInputs = form.querySelectorAll('input, select, textarea');
      let formDirty = false;

      trackedInputs.forEach(function (input) {
        input.addEventListener('focus', function () {
          const row = input.closest('.form-row');
          if (row) {
            row.classList.add('obc-form-row--focus');
          }
        });

        input.addEventListener('blur', function () {
          const row = input.closest('.form-row');
          if (row) {
            row.classList.remove('obc-form-row--focus');
          }
        });

        input.addEventListener('change', function () {
          formDirty = true;
        });

        input.addEventListener('input', function () {
          if (input.tagName === 'TEXTAREA') {
            input.style.height = 'auto';
            input.style.height = input.scrollHeight + 'px';
          }
        });

        if (input.tagName === 'TEXTAREA') {
          input.style.height = 'auto';
          input.style.height = input.scrollHeight + 'px';
        }
      });

      const fileInputs = form.querySelectorAll('input[type="file"]');
      fileInputs.forEach(function (input) {
        input.addEventListener('change', function () {
          var fileName = input.files && input.files[0] ? input.files[0].name : '';
          if (!fileName) {
            return;
          }
          var container = input.parentElement;
          if (!container) {
            return;
          }
          var label = container.querySelector('.obc-file-label');
          if (!label) {
            label = document.createElement('p');
            label.className = 'obc-file-label text-sm text-slate-500 mt-2';
            container.appendChild(label);
          }
          label.textContent = 'Selected: ' + fileName;
        });
      });

      form.addEventListener('submit', function () {
        formDirty = false;
      });

      window.addEventListener('beforeunload', function (event) {
        if (formDirty && !form.classList.contains('obc-form-submitted')) {
          event.preventDefault();
          event.returnValue = '';
        }
      });

      document.addEventListener('keydown', function (event) {
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
          const saveButton = form.querySelector('button[name="_save"], input[name="_save"]');
          if (saveButton) {
            event.preventDefault();
            saveButton.click();
          }
        }
        if (event.key === 'Escape') {
          const cancelLink = form.querySelector('a[href*="changelist"]');
          if (cancelLink) {
            window.location.href = cancelLink.href;
          }
        }
      });

    });

  const inlineQuickAddButtons = document.querySelectorAll('.obc-inline-card__add');
  inlineQuickAddButtons.forEach(function (button) {
    button.addEventListener('click', function (event) {
      event.preventDefault();
      const inlineGroup = button.closest('.obc-inline-group');
      if (!inlineGroup) {
        return;
      }
      const addRowLink = inlineGroup.querySelector('.add-row a');
      if (addRowLink) {
        addRowLink.click();
        return;
      }
      if (window.django && window.django.jQuery) {
        const $ = window.django.jQuery;
        const selector = '#' + button.dataset.inlinePrefix + '-group .add-row a';
        const $link = $(selector);
        if ($link.length) {
          $link.trigger('click');
        }
      }
    });
  });

  document.addEventListener('formset:added', function (event) {
    const element = event.target;
    if (!element || !element.classList) {
      return;
    }
    if (element.classList.contains('obc-inline-related')) {
      element.classList.add('obc-inline-related--new');
    } else if (element.tagName === 'TR') {
      element.classList.add('obc-inline-table__row--new');
    }
    setTimeout(function () {
      element.classList.remove('obc-inline-related--new');
      element.classList.remove('obc-inline-table__row--new');
    }, 600);
  });

    // ============================================================================
    // NAVIGATION BAR - Dropdown and Mobile Menu Functionality
    // ============================================================================

    /**
     * Toggle mobile navigation menu
     */
    window.toggleAdminMobileMenu = function() {
      const mobileMenu = document.getElementById('adminMobileMenu');
      const toggleButton = document.querySelector('button[onclick="toggleAdminMobileMenu()"]');

      if (mobileMenu) {
        const isHidden = mobileMenu.classList.contains('hidden');
        mobileMenu.classList.toggle('hidden');

        if (toggleButton) {
          toggleButton.setAttribute('aria-expanded', isHidden ? 'true' : 'false');
        }
      }
    };

    /**
     * Mobile submenu toggles
     */
    const mobileToggles = document.querySelectorAll('.admin-mobile-toggle');
    mobileToggles.forEach(function(toggle) {
      toggle.addEventListener('click', function() {
        const targetId = this.getAttribute('data-target');
        const submenu = document.getElementById(targetId);
        const chevron = this.querySelector('.fa-chevron-down');

        if (submenu) {
          const isHidden = submenu.classList.contains('hidden');
          submenu.classList.toggle('hidden');
          this.setAttribute('aria-expanded', isHidden ? 'true' : 'false');

          // Rotate chevron
          if (chevron) {
            if (isHidden) {
              chevron.style.transform = 'rotate(180deg)';
            } else {
              chevron.style.transform = 'rotate(0deg)';
            }
          }
        }
      });
    });

    /**
     * User dropdown toggle (fallback for non-hover devices)
     */
    const userDropdownButton = document.querySelector('.admin-user-dropdown button');
    const userDropdownMenu = document.querySelector('.admin-user-dropdown-menu');

    if (userDropdownButton && userDropdownMenu) {
      userDropdownButton.addEventListener('click', function(e) {
        e.stopPropagation();
        const isHidden = userDropdownMenu.classList.contains('hidden');
        userDropdownMenu.classList.toggle('hidden');
        this.setAttribute('aria-expanded', isHidden ? 'true' : 'false');
      });

      // Close dropdown when clicking outside
      document.addEventListener('click', function(e) {
        if (!userDropdownButton.contains(e.target) && !userDropdownMenu.contains(e.target)) {
          userDropdownMenu.classList.add('hidden');
          userDropdownButton.setAttribute('aria-expanded', 'false');
        }
      });
    }

    /**
     * Desktop dropdown keyboard navigation
     */
    const desktopDropdowns = document.querySelectorAll('.admin-nav-dropdown');
    desktopDropdowns.forEach(function(dropdown) {
      const button = dropdown.querySelector('button');
      const menu = dropdown.querySelector('.admin-dropdown-menu');

      if (button && menu) {
        button.addEventListener('keydown', function(e) {
          // Open on Enter or Space
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            const isHidden = menu.classList.contains('hidden');
            menu.classList.toggle('hidden');
            button.setAttribute('aria-expanded', isHidden ? 'true' : 'false');

            // Focus first link in menu
            if (isHidden) {
              const firstLink = menu.querySelector('a');
              if (firstLink) {
                setTimeout(function() { firstLink.focus(); }, 100);
              }
            }
          }

          // Close on Escape
          if (e.key === 'Escape') {
            menu.classList.add('hidden');
            button.setAttribute('aria-expanded', 'false');
            button.focus();
          }
        });

        // Trap focus within dropdown menu
        const menuLinks = menu.querySelectorAll('a');
        if (menuLinks.length > 0) {
          menuLinks[menuLinks.length - 1].addEventListener('keydown', function(e) {
            if (e.key === 'Tab' && !e.shiftKey) {
              e.preventDefault();
              menu.classList.add('hidden');
              button.setAttribute('aria-expanded', 'false');
              // Focus next dropdown or user menu
              const nextDropdown = dropdown.nextElementSibling;
              if (nextDropdown && nextDropdown.querySelector('button')) {
                nextDropdown.querySelector('button').focus();
              }
            }
          });
        }
      }
    });

    /**
     * Sticky header scroll effect
     */
    let lastScrollTop = 0;
    const header = document.getElementById('header');

    window.addEventListener('scroll', function() {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

      if (scrollTop > 50) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }

      lastScrollTop = scrollTop;
    });

    /**
     * Highlight active navigation item based on current URL
     */
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.admin-nav-item, .admin-dropdown-menu a');

    navLinks.forEach(function(link) {
      if (link.getAttribute('href') && currentPath.includes(link.getAttribute('href'))) {
        if (link.classList.contains('admin-nav-item')) {
          link.classList.add('active');
        } else {
          // Highlight parent dropdown if submenu item is active
          const dropdown = link.closest('.admin-nav-dropdown');
          if (dropdown) {
            const dropdownButton = dropdown.querySelector('button');
            if (dropdownButton) {
              dropdownButton.classList.add('active');
            }
          }
        }
      }
    });

    /**
     * Close mobile menu when window is resized to desktop
     */
    let resizeTimer;
    window.addEventListener('resize', function() {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function() {
        if (window.innerWidth >= 1024) {
          const mobileMenu = document.getElementById('adminMobileMenu');
          if (mobileMenu) {
            mobileMenu.classList.add('hidden');
          }
        }
      }, 250);
    });

    /**
     * ARIA live region announcements for dynamic updates
     */
    function announceToScreenReader(message) {
      const liveRegion = document.getElementById('aria-live-region');
      if (liveRegion) {
        liveRegion.textContent = message;
        setTimeout(function() {
          liveRegion.textContent = '';
        }, 1000);
      }
    }

    // Example: Announce when mobile menu is toggled
    const originalToggle = window.toggleAdminMobileMenu;
    window.toggleAdminMobileMenu = function() {
      originalToggle();
      const mobileMenu = document.getElementById('adminMobileMenu');
      if (mobileMenu) {
        const isHidden = mobileMenu.classList.contains('hidden');
        announceToScreenReader(isHidden ? 'Navigation menu closed' : 'Navigation menu opened');
      }
    };

  }); // END DOMContentLoaded

})();
