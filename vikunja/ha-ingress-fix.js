(function () {
  // Detect HA ingress from the current URL.
  var match = location.pathname.match(
    /^(\/api\/hassio_ingress\/[^/]+)(\/.*)?$/
  );
  if (!match) return;

  var ingressBase = match[1];
  var cleanPath = match[2] || "/";
  var origin = location.origin;

  // -- 1) Inject <base> so all relative URLs (./assets/…) resolve through ingress.
  var base = document.createElement("base");
  base.href = origin + ingressBase + "/";
  // Insert into <head> immediately (before any link/script is parsed).
  if (document.head) {
    document.head.prepend(base);
  } else {
    document.addEventListener(
      "DOMContentLoaded",
      function () {
        document.head.prepend(base);
      },
      { once: true }
    );
  }

  // -- 2) Rewrite the visible URL so Vue Router matches its "/" routes.
  history.replaceState(
    history.state,
    "",
    cleanPath + location.search + location.hash
  );

  // -- 3) Patch pushState/replaceState so Vue Router navigation stays within ingress.
  var origPush = history.pushState;
  var origReplace = history.replaceState;

  function patchState(orig) {
    return function (state, title, url) {
      // Only intercept relative or absolute-path URLs (not full http URLs).
      if (typeof url === "string" && url.charAt(0) === "/" && url.indexOf(ingressBase) !== 0) {
        url = ingressBase + url;
      }
      return orig.call(this, state, title, url);
    };
  }
  // Don't patch yet — wait until after our own replaceState above has finished.
  // Patch on next microtask so our call above goes through unmodified.
  Promise.resolve().then(function () {
    history.pushState = patchState(origPush);
    history.replaceState = patchState(origReplace);
  });

  // -- 4) Helper: rewrite a URL to route through ingress.
  function rewriteUrl(url) {
    if (typeof url !== "string") return url;
    if (url.indexOf(ingressBase) !== -1) return url;
    if (url.charAt(0) === "/") return ingressBase + url;
    if (url.lastIndexOf(origin + "/", 0) === 0) {
      return origin + ingressBase + url.substring(origin.length);
    }
    return url;
  }

  // -- 5) Patch fetch.
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

  // -- 6) Patch XMLHttpRequest.open.
  var origOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function () {
    var args = Array.prototype.slice.call(arguments);
    if (typeof args[1] === "string") {
      args[1] = rewriteUrl(args[1]);
    }
    return origOpen.apply(this, args);
  };
})();
