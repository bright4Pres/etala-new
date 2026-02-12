window.showView = function (viewName) {
  var borrowedView = document.getElementById('borrowed-view');
  var checkoutView = document.getElementById('checkout-view');
  var returnView = document.getElementById('return-view');

  if (borrowedView) borrowedView.style.display = 'none';
  if (checkoutView) checkoutView.style.display = 'none';
  if (returnView) returnView.style.display = 'none';

  var booksSection = document.getElementById('sidebar-books');
  var usersSection = document.getElementById('sidebar-users');
  if (booksSection) booksSection.style.display = 'none';
  if (usersSection) usersSection.style.display = 'none';

  var selectedView = document.getElementById(viewName + '-view');
  if (selectedView) selectedView.style.display = 'block';

  document.querySelectorAll('.app-sidebar-link').forEach(function (link) {
    link.classList.remove('active');
  });

  var activeLink = document.querySelector('[data-view="' + viewName + '"]');
  if (activeLink) activeLink.classList.add('active');

  if (viewName === 'checkout') {
    setTimeout(function () {
      var checkoutInput = document.getElementById('checkout-barcode-input');
      if (checkoutInput) {
        checkoutInput.focus();
        checkoutInput.select();
      }
    }, 100);
  } else if (viewName === 'return') {
    setTimeout(function () {
      var barcodeInput = document.getElementById('barcode-input');
      if (barcodeInput) {
        barcodeInput.focus();
        barcodeInput.select();
      }
    }, 100);
  }
};

window.toggleSidebarSection = function (sectionName) {
  var booksSection = document.getElementById('sidebar-books');
  var usersSection = document.getElementById('sidebar-users');
  if (!booksSection || !usersSection) return;

  if (sectionName === 'books') {
    if (booksSection.style.display === 'none' || booksSection.style.display === '') {
      booksSection.style.display = 'block';
      usersSection.style.display = 'none';
    } else {
      booksSection.style.display = 'none';
    }
  } else if (sectionName === 'users') {
    if (usersSection.style.display === 'none' || usersSection.style.display === '') {
      usersSection.style.display = 'block';
      booksSection.style.display = 'none';
    } else {
      usersSection.style.display = 'none';
    }
  }
};

document.addEventListener('DOMContentLoaded', function () {
  var modeSwitch = document.querySelector('.mode-switch');

  if (modeSwitch) {
    modeSwitch.addEventListener('click', function () {
      if (document.documentElement.classList.contains('dark')) {
        document.documentElement.classList.remove('dark');
        document.documentElement.classList.add('light');
        localStorage.setItem('theme', 'light');
      } else {
        document.documentElement.classList.remove('light');
        document.documentElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
      }
      modeSwitch.classList.toggle('active');
    });
  }
  
  var listView = document.querySelector('.list-view');
  var gridView = document.querySelector('.grid-view');
  var projectsList = document.querySelector('.project-boxes');

  if (listView && gridView && projectsList) {
    listView.addEventListener('click', function () {
      gridView.classList.remove('active');
      listView.classList.add('active');
      projectsList.classList.remove('jsGridView');
      projectsList.classList.add('jsListView');
    });

    gridView.addEventListener('click', function () {
      gridView.classList.add('active');
      listView.classList.remove('active');
      projectsList.classList.remove('jsListView');
      projectsList.classList.add('jsGridView');
    });
  }

  var messagesBtn = document.querySelector('.messages-btn');
  var messagesClose = document.querySelector('.messages-close');
  var messagesSection = document.querySelector('.messages-section');

  if (messagesBtn && messagesSection) {
    messagesBtn.addEventListener('click', function () {
      messagesSection.classList.add('show');
    });
  }

  if (messagesClose && messagesSection) {
    messagesClose.addEventListener('click', function () {
      messagesSection.classList.remove('show');
    });
  }
});