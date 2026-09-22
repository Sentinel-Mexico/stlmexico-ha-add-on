(function () {
  var match = location.pathname.match(
    /^(\/api\/hassio_ingress\/[^/]+)(\/.*)?$/
  );
  if (!match) return;

  var ingressBase = match[1];
  var cleanPath = match[2] || "/";
  var origin = location.origin;

  // Strip the ingress prefix from the URL so Vue Router sees "/" and
  // matches its routes instead of showing a blank page.
  history.replaceState(
    history.state,
    "",
    cleanPath + location.search + location.hash
  );

  // Rewrite a URL so it routes through the HA ingress proxy.
  function rewriteUrl(url) {
    if (typeof url !== "string") return url;
    // Already has the ingress prefix — leave it alone.
    if (url.indexOf(ingressBase) !== -1) return url;
    // Absolute path: /api/v1/info → /ingress-base/api/v1/info
    if (url.charAt(0) === "/") return ingressBase + url;
    // Full same-origin URL: https://host/api/v1/… → https://host/ingress-base/api/v1/…
    if (url.lastIndexOf(origin + "/", 0) === 0) {
      return origin + ingressBase + url.substring(origin.length);
    }
    return url;
  }

  // --- Patch fetch (handles both string URLs and Request objects) ---
  var origFetch = window.fetch;
  window.fetch = function (input, init) {
    if (typeof input === "string") {
      input = rewriteUrl(input);
    } else if (input instanceof Request) {
      var newUrl = rewriteUrl(input.url);
      if (newUrl !== input.url) {
        input = new Request(newUrl, input);
      }
    }
    return origFetch.call(this, input, init);
  };

  // --- Patch XMLHttpRequest.open ---
  var origOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function () {
    var args = Array.prototype.slice.call(arguments);
    if (typeof args[1] === "string") {
      args[1] = rewriteUrl(args[1]);
    }
    return origOpen.apply(this, args);
  };
})();
