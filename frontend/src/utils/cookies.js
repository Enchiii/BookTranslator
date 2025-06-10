export function setCookie(name, value, days = 365) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${encodeURIComponent(name)}=${encodeURIComponent(value)}; expires=${expires}; path=/`;
}

export function getCookie(name) {
  return document.cookie
    .split("; ")
    .find(row => row.startsWith(encodeURIComponent(name) + "="))
    ?.split("=")[1];
}
