!function(){try{var e="undefined"!=typeof window?window:"undefined"!=typeof global?global:"undefined"!=typeof self?self:{},n=(new Error).stack;n&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[n]="4884d5bd-fc54-4883-9403-e64b80aea937",e._sentryDebugIdIdentifier="sentry-dbid-4884d5bd-fc54-4883-9403-e64b80aea937")}catch(e){}}();var _global="undefined"!=typeof window?window:"undefined"!=typeof global?global:"undefined"!=typeof self?self:{};_global.SENTRY_RELEASE={id:"0.6.0"},function(e,n){"object"==typeof exports&&"object"==typeof module?module.exports=n():"function"==typeof define&&define.amd?define([],n):"object"==typeof exports?exports.swh=n():(e.swh=e.swh||{},e.swh.badges=n())}(self,(function(){return function(){"use strict";var e={d:function(n,o){for(var t in o)e.o(o,t)&&!e.o(n,t)&&Object.defineProperty(n,t,{enumerable:!0,get:o[t]})},o:function(e,n){return Object.prototype.hasOwnProperty.call(e,n)},r:function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})}},n={};function o(e,n){var o,t,d=n;if("origin"===e)o=Urls.swh_badge(e,n),t=Urls.browse_origin()+"?origin_url="+n;else{var r=n.indexOf(";");-1!==r?(d=n.slice(0,r),o=Urls.swh_badge_swhid(d),$(".swhid").each((function(e,n){n.id===d&&(t=n.pathname)}))):(o=Urls.swh_badge_swhid(n),t=Urls.browse_swhid(n))}var i=""+window.location.origin+o,a=""+window.location.origin+t,l='\n  <a href="'+a+'">\n    <img class="swh-badge" src="'+i+'" alt="Archived | '+n+'"/>\n  </a>\n  <div>\n    <label>HTML</label>\n    <pre><code class="swh-badge-html html">&lt;a href="'+a+'"&gt;\n    &lt;img src="'+i+'" alt="Archived | '+d+'"/&gt;\n&lt;/a&gt;</code></pre>\n  </div>\n  <div>\n    <label>Markdown</label>\n    <pre><code class="swh-badge-md markdown">[![SWH]('+i+")]("+a+')</code></pre>\n  </div>\n  <div>\n    <label>reStructuredText</label>\n    <pre class="swh-badge-rst">.. image:: '+i+"\n    :target: "+a+"</pre>\n  </div>";swh.webapp.showModalHtml("Software Heritage badge integration",l),swh.webapp.highlightCode(!1,".swh-badge-html"),swh.webapp.highlightCode(!1,".swh-badge-md")}return e.r(n),e.d(n,{showBadgeInfoModal:function(){return o}}),n}()}));
//# sourceMappingURL=badges.c31e2114ec3d53fcef97.js.map