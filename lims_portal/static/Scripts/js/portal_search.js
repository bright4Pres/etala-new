(function () {
  function escapeRegex(text) {
    return String(text || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text == null ? '' : String(text);
    return div.innerHTML;
  }

  function highlightMatch(text, query) {
    if (!text) return '';
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    return escapeHtml(text).replace(regex, '<span class="suggestion-match">$1</span>');
  }

  function buildMatches(book, queryLower, query) {
    const matches = [];

    function pushIf(label, value) {
      if (!value) return;
      const valueStr = String(value);
      if (valueStr.toLowerCase().includes(queryLower)) {
        matches.push(`<span class="suggestion-match">${label}</span>: ${highlightMatch(valueStr, query)}`);
      }
    }

    pushIf('Title', book.Title);
    pushIf('Author', book.mainAuthor);
    pushIf('Co-Author', book.coAuthor);
    pushIf('Call Number', book.callNumber);
    pushIf('Publisher', book.Publisher);
    pushIf('Edition', book.Edition);
    pushIf('Language', book.Language);
    pushIf('Type', book.Type);
    pushIf('Place', book.placeofPublication);
    pushIf('Editors', book.Editors);
    pushIf('Acquisition', book.acquisitionStatus);
    pushIf('Published', book.publicationDate);
    pushIf('Copyright', book.copyrightDate);

    if (book.copies && Array.isArray(book.copies)) {
      book.copies.forEach((copy) => {
        pushIf('Accession', copy && copy.accessionNumber);
        pushIf('Location', copy && copy.Location);
        pushIf('Status', copy && copy.status);
        pushIf('Borrower', copy && copy.borrowed_by);
      });
    }

    return matches;
  }

  function displaySuggestions(container, books, query) {
    if (!books || books.length === 0) {
      container.innerHTML = '<div class="no-results">No books found</div>';
      container.classList.add('show');
      return;
    }

    const queryLower = query.toLowerCase();
    const safeQueryEncoded = encodeURIComponent(query);

    const html = books.slice(0, 8).map((book) => {
      const matches = buildMatches(book, queryLower, query);
      const matchDetails = matches.length > 0 ? matches.slice(0, 3).join(' • ') : 'Match found';

      const title = escapeHtml(book && book.Title ? book.Title : 'Untitled');
      const available = book && typeof book.available_copies !== 'undefined' ? book.available_copies : 0;
      const total = book && typeof book.total_copies !== 'undefined' ? book.total_copies : 0;

      return (
        `<div class="search-suggestion-item" data-q="${safeQueryEncoded}">` +
        `<div class="suggestion-title">${title}</div>` +
        `<div class="suggestion-details">${matchDetails}<br>Available: <strong>${available}/${total}</strong> copies</div>` +
        `</div>`
      );
    }).join('');

    container.innerHTML = html;
    container.classList.add('show');

    // Delegate click to navigate to records
    container.querySelectorAll('.search-suggestion-item').forEach((el) => {
      el.addEventListener('click', () => {
        const q = el.getAttribute('data-q') || safeQueryEncoded;
        window.location.href = `/records/?search=${q}`;
      });
    });
  }

  window.initPortalSearch = function initPortalSearch(opts) {
    const inputId = (opts && opts.inputId) || 'portalSearchInput';
    const suggestionsId = (opts && opts.suggestionsId) || 'portalSearchSuggestions';

    const searchInput = document.getElementById(inputId);
    const suggestionsContainer = document.getElementById(suggestionsId);
    if (!searchInput || !suggestionsContainer) return;

    let searchTimeout;

    function fetchSearchSuggestions(query) {
      fetch(`/records/?search=${encodeURIComponent(query)}`, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json'
        }
      })
        .then((response) => response.json())
        .then((data) => {
          displaySuggestions(suggestionsContainer, data && data.books ? data.books : [], query);
        })
        .catch((error) => {
          // Fail closed: hide suggestions if backend errors
          console.error('Search error:', error);
          suggestionsContainer.classList.remove('show');
        });
    }

    searchInput.addEventListener('input', function () {
      const query = this.value.trim();
      clearTimeout(searchTimeout);

      if (query.length < 2) {
        suggestionsContainer.classList.remove('show');
        return;
      }

      searchTimeout = setTimeout(() => {
        fetchSearchSuggestions(query);
      }, 300);
    });

    searchInput.addEventListener('keypress', function (event) {
      if (event.key === 'Enter') {
        event.preventDefault();
        const query = this.value.trim();
        if (query) {
          window.location.href = `/records/?search=${encodeURIComponent(query)}`;
        }
      }
    });

    document.addEventListener('click', function (event) {
      if (!event.target.closest('.search-wrapper')) {
        suggestionsContainer.classList.remove('show');
      }
    });
  };
})();
