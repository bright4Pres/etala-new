document.addEventListener("DOMContentLoaded", () => {
  const navItems = document.querySelectorAll('.nav-item');
  const toggleSiblingClass = (items, index, offset, className, add) => {
    const sibling = items[index + offset];
    if (sibling) {
      sibling.classList.toggle(className, add);
    }
  };
  navItems.forEach((item, index) => {
    item.addEventListener('mouseenter', () => {
      item.classList.add('hover'); 
      toggleSiblingClass(navItems, index, -1, 'sibling-close', true); // previous sibling
      toggleSiblingClass(navItems, index, 1, 'sibling-close', true);  // next sibling
      toggleSiblingClass(navItems, index, -2, 'sibling-far', true);   // oreivous-previous sibling
      toggleSiblingClass(navItems, index, 2, 'sibling-far', true);    // next-next sibling
    });
    item.addEventListener('mouseleave', () => {
      item.classList.remove('hover');
      // Toggle classes for siblings
      toggleSiblingClass(navItems, index, -1, 'sibling-close', false); // previous sibling
      toggleSiblingClass(navItems, index, 1, 'sibling-close', false);  // next sibling
      toggleSiblingClass(navItems, index, -2, 'sibling-far', false);   // previous previous sibling
      toggleSiblingClass(navItems, index, 2, 'sibling-far', false);    // next enxt sibling
    });
  });
});