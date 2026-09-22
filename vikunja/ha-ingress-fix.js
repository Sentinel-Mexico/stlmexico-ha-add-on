(function () {
  var match = location.pathname.match(
    /^(\/api\/hassio_ingress\/[^/]+)(\/.*)?$/
  );
  if (!match) return;

  var ingressBase = match[1];
  var cleanPath = match[2] || "/";

  // -- 1) Patch pushState / replaceState IMMEDIATELY so Vue Router
  //    navigations stay within the ingress prefix.
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

  history.pushState = patchState(origPush);
  history.replaceState = patchState(origReplace);

  // -- 2) Strip the ingress prefix AFTER the full page has loaded.
  //    We must NOT do this synchronously because it changes document.URL,
  //    which would break relative path resolution for assets still being
  //    parsed in the HTML (src="./assets/..." would resolve against "/"
  //    instead of the ingress prefix).
  window.addEventListener("DOMContentLoaded", function () {
    origReplace.call(history, history.state, "", cleanPath + location.search + location.hash);
  });

  // -- 3) Helper: prepend the ingress prefix to absolute paths.
  function rewriteUrl(url) {
    if (typeof url !== "string") return url;
    if (url.indexOf(ingressBase) !== -1) return url;
    if (url.charAt(0) === "/") return ingressBase + url;
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

  // -- 6) Patch window.open so links opened from JS go through ingress.
  var origWindowOpen = window.open;
  window.open = function (url) {
    var args = Array.prototype.slice.call(arguments);
    if (typeof args[0] === "string") {
      args[0] = rewriteUrl(args[0]);
    }
    return origWindowOpen.apply(this, args);
  };
})();
