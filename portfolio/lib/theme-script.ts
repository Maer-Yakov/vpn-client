/**
 * Ставит класс темы до первой отрисовки.
 * Тёмная тема по умолчанию. Светлая включается только если в localStorage лежит "light".
 */
export const themeInitScript = `(function(){try{var dark=localStorage.getItem("theme")!=="light";var root=document.documentElement;root.classList.toggle("dark",dark);root.style.colorScheme=dark?"dark":"light";}catch(e){}})();`;
