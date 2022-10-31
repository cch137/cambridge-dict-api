const cookies = {
  getItem: function (sKey) {
    return decodeURIComponent(document.cookie.replace(new RegExp("(?:(?:^|.*;)\\s*" + encodeURIComponent(sKey).replace(/[-.+*]/g, "\\$&") + "\\s*\\=\\s*([^;]*).*$)|^.*$"), "$1")) || null;
  },
  setItem: function (sKey, sValue, vEnd, sPath, sDomain, bSecure) {
    if (!sKey || /^(?:expires|max\-age|path|domain|secure)$/i.test(sKey)) { return false; }
    var sExpires = "";
    if (vEnd) {
    switch (vEnd.constructor) {
      case Number:
      sExpires = vEnd === Infinity ? "; expires=Fri, 31 Dec 9999 23:59:59 GMT" : "; max-age=" + vEnd;
      break;
      case String:
      sExpires = "; expires=" + vEnd;
      break;
      case Date:
      sExpires = "; expires=" + vEnd.toUTCString();
      break;
    }
    }
    document.cookie = encodeURIComponent(sKey) + "=" + encodeURIComponent(sValue) + sExpires + (sDomain ? "; domain=" + sDomain : "") + (sPath ? "; path=" + sPath : "") + (bSecure ? "; secure" : "");
    return true;
  },
  removeItem: function (sKey, sPath, sDomain) {
    if (!sKey || !this.hasItem(sKey)) { return false; }
    document.cookie = encodeURIComponent(sKey) + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT" + ( sDomain ? "; domain=" + sDomain : "") + ( sPath ? "; path=" + sPath : "");
    return true;
  },
  hasItem: function (sKey) {
    return (new RegExp("(?:^|;\\s*)" + encodeURIComponent(sKey).replace(/[-.+*]/g, "\\$&") + "\\s*\\=")).test(document.cookie);
  },
  keys: /* optional method: you can safely remove it! */ function () {
    var aKeys = document.cookie.replace(/((?:^|\s*;)[^\=]+)(?=;|$)|^\s*|\s*(?:\=[^;]*)?(?:\1|$)/g, "").split(/\s*(?:\=[^;]*)?;\s*/);
    for (var nIdx = 0; nIdx < aKeys.length; nIdx++) { aKeys[nIdx] = decodeURIComponent(aKeys[nIdx]); }
    return aKeys;
  }
};

function newEl (s, attb={}, text='', children=[]) {
  const el = document.createElement(s);
  for (const i in attb) if(attb != null && attb != undefined) el.setAttribute(i, attb[i]);
  if (text) el.innerText = text;
  if (!(children instanceof Array)) children = [children];
  el.append(...children);
  return el;
};

function newElW3 (s, attb={}, children=[]) {
  const el = document.createElementNS('http:\/\/www.w3.org/2000/svg', s);
  for (const i in attb) if(attb != null && attb != undefined) el.setAttribute(i, attb[i]);
  if (!children instanceof Array) children = [children];
  el.append(...[children]);
  return el;
};

function post_xhr(url, form='', async=true) {
  const xhr = new XMLHttpRequest;
  xhr.open('POST', url, async);
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
  xhr.send(form);
  return xhr;
};

function countdown_str(time) {
  let s = Math.round(+time / 1000);
  let m = Math.floor(s / 60);
  if (m <= 0) return s + `s`;
  s = s % 60;
  let h = Math.floor(m / 60);
  if (h <= 0) return m + `min`;
  m = m % 60;
  let d = Math.floor(h / 24);
  if (d <= 0) return h + `hr`;
  else return d + `day${d>1?'s':''}`;
  return _s;
};