(function () {
  // Detect HA ingress from the current URL.
  var match = location.pathname.match(
    /^(\/api\/hassio_ingress\/[^/]+)(\/.*)?$/
  );
  if (!match) return;

  var ingressBase = match[1];
  var cleanPath = match[2] || "/";

  // -- 1) Strip the ingress prefix from the URL so Vue Router sees "/".
  //    Vue Router inspects location.pathname at boot; it must see the
  //    app-root "/" (or "/login", etc.), not the ingress prefix.
  history.replaceState(history.state, "", cleanPath + location.search + location.hash);

  // -- 2) Patch pushState / replaceState so Vue Router navigation
  //    adds the ingress prefix back (the browser needs it to route
  //    through HA's ingress proxy).
  var origPush = history.pushState;
  var origReplace = history.replaceState;

  function patchState(orig) {
    return function (state, title, url) {
      if (typeof url === "string" && url.charAt(0) === "/" && url.indexOf(ingressBase) !== 0) {
        url = ingressBase + url;
      }
      return orig.call(this, state, title, url);
    };
  }

  // Defer to next microtask so our own replaceState above goes through unmodified.
  Promise.resolve().then(function () {
    history.pushState = patchState(origPush);
    history.replaceState = patchState(origReplace);
  });

  // -- 3) Helper: prepend the ingress prefix to absolute paths.
  function rewriteUrl(url) {
    if (typeof url !== "string") return url;
    // Already has the ingress prefix — leave it alone.
    if (url.indexOf(ingressBase) !== -1) return url;
    // Absolute path: prepend ingress base.
    if (url.charAt(0) === "/") return ingressBase + url;
    // Full origin URL: insert ingress base after origin.
    if (url.lastIndexOf(location.origin + "/", 0) === 0) {
      return location.origin + ingressBase + url.substring(location.origin.length);
    }
    return url;
  }

  // -- 4) Patch fetch so API calls go through ingress.
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

  // -- 5) Patch XMLHttpRequest.open so XHR calls go through ingress.
  var origOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function () {
    var args = Array.prototype.slice.call(arguments);
    if (typeof args[1] === "string") {
      args[1] = rewriteUrl(args[1]);
    }
    return origOpen.apply(this, args);
  };
})();
