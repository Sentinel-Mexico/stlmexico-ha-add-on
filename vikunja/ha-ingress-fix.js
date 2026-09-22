(function () {
  var match = location.pathname.match(
    /^(\/api\/hassio_ingress\/[^/]+)(\/.*)?$/
  );
  if (!match) return;

  var ingressBase = match[1];
  var cleanPath = match[2] || "/";

  // Strip the ingress prefix from the URL so Vue Router sees "/" and
  // matches its routes instead of showing a blank page.
  history.replaceState(
    history.state,
    "",
    cleanPath + location.search + location.hash
  );

  // Patch fetch — API calls like fetch("/api/v1/info") must go through
  // the ingress proxy, not straight to the origin.
  var origFetch = window.fetch;
  window.fetch = function (input, init) {
    if (typeof input === "string" && input.startsWith("/")) {
      input = ingressBase + input;
    }
    return origFetch.call(this, input, init);
  };

  // Patch XMLHttpRequest.open for the same reason.
  var origOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function () {
    var args = Array.prototype.slice.call(arguments);
    if (typeof args[1] === "string" && args[1].startsWith("/")) {
      args[1] = ingressBase + args[1];
    }
    return origOpen.apply(this, args);
  };
})();
