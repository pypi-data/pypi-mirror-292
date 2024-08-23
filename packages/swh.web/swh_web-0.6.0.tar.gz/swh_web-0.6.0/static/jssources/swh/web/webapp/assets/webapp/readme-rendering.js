/**
 * Copyright (C) 2018-2024  The Software Heritage developers
 * See the AUTHORS file at the top-level directory of this distribution
 * License: GNU Affero General Public License version 3, or any later version
 * See top-level LICENSE file for more information
 */

import {handleFetchError} from 'utils/functions';
import * as EmailValidator from 'email-validator';
import {resolve} from 'pathifist';
import * as showdownHighlight from 'showdown-highlight';

export function addReadmeHeadingAnchors() {
  swh.webapp.addHeadingAnchors('.swh-readme');
}

// replace showdown generated relative links to archived objects in readme HTML:
// from /browse.*/directory/<path>/.* to /browse.*/directory/?path=<path>.*
function fixSwhRelativeLinksInReadme(readmeHtml) {
  // parse readme HTML
  const parser = new DOMParser();
  const document = parser.parseFromString(readmeHtml, 'text/html');
  // iterate on all links
  const links = document.querySelectorAll('a');
  for (const link of links) {
    if (!link.href.startsWith(window.origin)) {
      // not a link to the archive, nothing to do
      continue;
    }
    // get raw href node value as link.href was already processed by showdown
    const hrefVal = decodeURIComponent(link.attributes.href.nodeValue);
    try {
      // check if href value is a relative link, URL parsing will fail
      new URL(hrefVal);
    } catch (TypeError) {
      if (hrefVal.startsWith('#')) {
        // anchor link, nothing to do
        continue;
      }
      let replacement;
      if (EmailValidator.validate(hrefVal)) {
        // generate mail link
        replacement = `mailto:${hrefVal}`;
      } else {
        // resolve relative path
        const url = new URL(window.location.href);
        const currentPath = url.searchParams.get('path') || '';
        const path = resolve(currentPath, hrefVal);
        if (path.startsWith('..')) {
          // such path is not resolvable by the archive webapp
          continue;
        }
        // generate replacement URL
        if (path) {
          url.searchParams.set('path', path);
        } else {
          url.searchParams.delete('path');
        }
        replacement = url.href.replace(window.location.origin, '');
      }
      link.href = replacement;
    }
  }
  return document.documentElement.innerHTML;
}

export async function renderMarkdown(domElt, markdownDocUrl) {

  const showdown = await import(/* webpackChunkName: "showdown" */ 'utils/showdown');
  await import(/* webpackChunkName: "highlightjs" */ 'utils/highlightjs');

  $(document).ready(async() => {
    const converter = new showdown.Converter({
      tables: true,
      extensions: [showdownHighlight({auto_detection: false})]
    });
    const url = new URL(window.location.href);
    if (url.searchParams.has('origin_url')) {
      try {
        const originUrl = new URL(url.searchParams.get('origin_url'));
        if (originUrl.hostname === 'github.com') {
          converter.setFlavor('github');
        }
      } catch (TypeError) {}
    }

    try {
      const response = await fetch(markdownDocUrl);
      handleFetchError(response);
      const data = await response.text();
      $(domElt).addClass('swh-showdown');
      let html = converter.makeHtml(data);
      const url = new URL(window.location.href);
      if (url.pathname.indexOf('/directory/') !== -1) {
        html = fixSwhRelativeLinksInReadme(html);
      }
      $(domElt).html(swh.webapp.filterXSS(html));
      addReadmeHeadingAnchors();
    } catch (_) {
      $(domElt).text('Readme bytes are not available');
    }
  });

}

export async function renderOrgData(domElt, orgDocData) {

  const org = await import(/* webpackChunkName: "org" */ 'utils/org');

  const parser = new org.Parser();
  const orgDocument = parser.parse(orgDocData, {toc: false});
  const orgHTMLDocument = orgDocument.convert(org.ConverterHTML, {});
  $(domElt).addClass('swh-org');
  $(domElt).html(swh.webapp.filterXSS(orgHTMLDocument.toString()));
  // remove toc and section numbers to get consistent
  // with other readme renderings
  $('.swh-org ul').first().remove();
  $('.section-number').remove();
}

export function renderOrg(domElt, orgDocUrl) {
  $(document).ready(async() => {
    try {
      const response = await fetch(orgDocUrl);
      handleFetchError(response);
      const data = await response.text();
      renderOrgData(domElt, data);
      addReadmeHeadingAnchors();
    } catch (_) {
      $(domElt).text('Readme bytes are not available');
    }
  });
}

export function renderTxt(domElt, txtDocUrl) {
  $(document).ready(async() => {
    try {
      const response = await fetch(txtDocUrl);
      handleFetchError(response);
      const data = await response.text();

      const orgMode = '-*- mode: org -*-';
      if (data.indexOf(orgMode) !== -1) {
        renderOrgData(domElt, data.replace(orgMode, ''));
      } else {
        $(domElt).addClass('swh-readme-txt');
        $(domElt)
            .html('')
            .append($('<pre></pre>').text(data));
      }
    } catch (_) {
      $(domElt).text('Readme bytes are not available');
    }
  });
}
