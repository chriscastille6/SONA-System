/**
 * Same-origin CSRF helper for JSON fetch to Django views.
 * Prefers <meta name="csrf-token"> (works with CSRF_COOKIE_HTTPONLY=True).
 */
(function (global) {
  function getCsrfToken() {
    if (typeof global.CSRF_TOKEN === 'string' && global.CSRF_TOKEN) {
      return global.CSRF_TOKEN;
    }
    var meta = document.querySelector('meta[name="csrf-token"]');
    if (meta && meta.content) {
      return meta.content;
    }
    var input = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (input && input.value) {
      return input.value;
    }
    return '';
  }

  function csrfHeaders(extra) {
    var headers = Object.assign({ 'Content-Type': 'application/json' }, extra || {});
    var token = getCsrfToken();
    if (token) {
      headers['X-CSRFToken'] = token;
    }
    return headers;
  }

  global.getCsrfToken = getCsrfToken;
  global.csrfHeaders = csrfHeaders;
})(typeof window !== 'undefined' ? window : this);
