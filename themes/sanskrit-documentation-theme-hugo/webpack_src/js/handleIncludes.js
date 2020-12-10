import * as main from "./main";

import urljoin from 'url-join';

/*
Example: absoluteUrl("../subfolder1/divaspari/", "../images/forest-fire.jpg") == "../subfolder1/images/forest-fire.jpg"
WARNING NOTE: won't work with say base = "http://google.com" since it does not end with /. 
 */
function absoluteUrl(base, relative) {
    // console.debug(base.toString(), relative.toString());
    // console.debug(base, relative);
    if (relative.startsWith("http") || relative.startsWith("file")) {
        return relative;
    }
    if (relative.startsWith("/") && !base.startsWith("http") && !base.startsWith("file")) {
        return relative;
    }
    let baseWithoutIntraPageLink = base.toString().split("#")[0];
    var baseDirStack = baseWithoutIntraPageLink.toString().split("/");
    baseDirStack.pop(); // remove current file name (or empty string)
    // (omit if "base" is the current folder without trailing slash)
    if (baseDirStack.length === 0) {
        return relative;
    }
    // console.debug(baseDirStack);
    return urljoin(baseDirStack.join("/"), relative.toString());
}

// WHen you include html from one page within another, you need to fix image urls, anchor urls etc..
function fixIncludedHtml(includedPageRelativeUrl, html, newLevelForH1) {
    // We want to use jquery to parse html, but without loading images. Hence this.
    // Tip from: https://stackoverflow.com/questions/15113910/jquery-parse-html-without-loading-images
    var virtualDocument = document.implementation.createHTMLDocument('virtual');
    // The surrounding divs are eliminated when the jqueryElement is created.
    var jqueryElement = $(main.setInlineComments(`<div>${html}</div>`), virtualDocument);

    // console.debug(jqueryElement.html());
    // Remove some tags.
    jqueryElement.find("script").remove();
    jqueryElement.find("footer").remove();
    jqueryElement.find("#disqus_thread").remove();
    jqueryElement.find("#toc").remove();
    jqueryElement.find("#toc_header").remove();
    jqueryElement.find(".back-to-top").remove();

    jqueryElement.find('.js_include').each(function() {
        let includerUrl = includedPageRelativeUrl.replace("index.html", "");

        $(this).attr("url", absoluteUrl(includerUrl, $(this).attr("url")));
        if (newLevelForH1 < 1) {
            console.error("Ignoring invalid newLevelForH1: %d, using 6", newLevelForH1);
            newLevelForH1 = 6;
        }
        var includedPageNewLevelForH2 = parseInt($(this).attr("newLevelForH1"));
        if (includedPageNewLevelForH2 === undefined) {
            includedPageNewLevelForH2 = 6;
        }
        includedPageNewLevelForH2 = Math.min(6, ((includedPageNewLevelForH2 - 2) + newLevelForH1));
        $(this).attr("newLevelForH1", includedPageNewLevelForH2);
    });


    /*
    Fix headers in the included html so as to not mess up the table of contents
    of the including page.
    Adjusting the heading levels to retain substructure seems more complicated -
    getting the heading "under" which jsIncludeJqueryElement falls seems non-trivial.
     */
    var headers = jqueryElement.find(":header");
    if (headers.length > 0) {
        var id_prefix = includedPageRelativeUrl.replace("/", "_");
        headers.replaceWith(function() {
            var headerElement = $(this);
            // console.debug(headerElement);
            var hLevel = parseInt(headerElement.prop("tagName").substring(1));
            var hLevelNew = Math.min(6, newLevelForH1 - 1 + hLevel);
            var newId = id_prefix + "_" + headerElement[0].id;
            return $("<h" + hLevelNew +" id='" + newId + "'/>").append(headerElement.contents());
        });
    }


    // Fix image urls.
    jqueryElement.find("img").each(function() {
        console.log(includedPageRelativeUrl, $(this).attr("src"), absoluteUrl(includedPageRelativeUrl, $(this).attr("src")));
        // console.log($(this).attr("src"))
        $(this).attr("src", absoluteUrl(includedPageRelativeUrl, $(this).attr("src")));
        // console.log($(this).attr("src"))
    });

    // Fix links.
    jqueryElement.find("a").each(function() {
        // console.debug($(this).html());
        var href = $(this).attr("href");
        if (href.startsWith("#")) {
            var headers = jqueryElement.find(":header");
            var new_href = href;
            if (headers.length > 0) {
                var id_prefix = headers[0].id;
                new_href = id_prefix + "_" + href.substr(1);
                // console.debug(new_href, id_prefix, href);
                jqueryElement.find(href).each(function () {
                    $(this).attr("id", new_href.substr(1));
                });
            }
            $(this).attr("href", new_href);
        } else {
            $(this).attr("href", absoluteUrl(includedPageRelativeUrl, href));
        }
    });

    return jqueryElement.html();
}

/* This function looks at the html of the page to be included, and changes it in the following ways:
- It fixes heading levels and figures out whether a title is needed.
- It fixes urls of images, links and includes to be relative to the includedPageUrl (which is inturn relative to the current page url), so that they work as expected when included in the given page.
*/
// An async function returns results wrapped in Promise objects.
async function processAjaxResponseHtml(responseHtml, addTitle, includedPageNewLevelForH1, includedPageRelativeUrl) {
    // We want to use jquery to parse html, but without loading images. Hence this.
    // Tip from: https://stackoverflow.com/questions/15113910/jquery-parse-html-without-loading-images
    var virtualDocument = document.implementation.createHTMLDocument('virtual');

    var titleElements = $(responseHtml, virtualDocument).find("h1");
    var title = "";
    if (titleElements.length > 0) {
        // console.debug(titleElements[0]);
        title = titleElements[0].textContent;
    }

    var contentElements = $(responseHtml, virtualDocument).find("#post_content");
    // console.log(contentElements);
    if (contentElements.length === 0) {
        let message = "Could not get \"post-content\" class element.";
        console.warn(message);
        console.log(responseHtml);
        throw Error(message);
    } else {
        // We don't want multiple post-content divs, hence we replace with an included-post-content div.
        var editLinkElements = $(responseHtml, virtualDocument).find("#editLink");
        var editLinkHtml = "";
        if (editLinkElements.length > 0) {
            // console.debug(editLinkElements);
            editLinkHtml = `<a class="btn btn-secondary" href="${editLinkElements.attr("href")}"><i class="fas fa-edit"></i></a>`
        }
        // console.debug(addTitle);
        var titleHtml = "<div />";
        if (addTitle && addTitle != "false") {
            titleHtml = "<h1 id='" + title + "'>" + title + "</h1>";
        }
        var popoutHtml = "<div class='border d-flex justify-content-between'>" + titleHtml + "<div><a class='btn btn-secondary' href='" + absoluteUrl(document.location, includedPageRelativeUrl) + "'><i class=\"fas fa-external-link-square-alt\"></i></a>" +
            editLinkHtml + "</div>"
        "</div>";
        var contentHtml = `<div class=''>${contentElements[0].innerHTML}</div>`;
        var elementToInclude = $("<div class='included-post-content border'/>");
        elementToInclude.html(fixIncludedHtml(includedPageRelativeUrl, popoutHtml, includedPageNewLevelForH1) + fixIncludedHtml(includedPageRelativeUrl, contentHtml, includedPageNewLevelForH1));
        return elementToInclude;
    }
}

/*
Get included page url relative to the current page url.
* */
function getRelativeIncludedPageUrl(jsIncludeJqueryElement) {
    var includedPageUrl = jsIncludeJqueryElement.attr("url");
    if (includedPageUrl.endsWith("/")) {
        // In case one loads file://x/y/z/ rather than http://x/y/z/, the following is needed. 
        includedPageUrl = includedPageUrl + "index.html";
    }
    return includedPageUrl;
}

async function fillJsInclude(jsIncludeJqueryElement, includedPageNewLevelForH1) {
    if (jsIncludeJqueryElement.html().trim() !== "") {
        console.warn("Refusing to refill element with non-empty html - ", jsIncludeJqueryElement);
        return "Already loaded";
    }
    console.info("Inserting include for ", jsIncludeJqueryElement);

    let includedPageUrl = getRelativeIncludedPageUrl(jsIncludeJqueryElement);
    if (includedPageUrl == "") {
        console.error("Invalid url!", jsIncludeJqueryElement);
        return "Invalid url!"
    }
    if (includedPageNewLevelForH1 === undefined) {
        includedPageNewLevelForH1 = parseInt(jsIncludeJqueryElement.attr("newLevelForH1"));
    }
    if (includedPageNewLevelForH1 === undefined) {
        includedPageNewLevelForH1 = 6;
    }
    // console.debug(includedPageNewLevelForH1);
    let getAjaxResponsePromise = $.ajax(includedPageUrl);
    function processingFn(responseHtml) {
        return processAjaxResponseHtml(responseHtml, jsIncludeJqueryElement.attr("includeTitle"), includedPageNewLevelForH1, includedPageUrl);
    }
    return getAjaxResponsePromise.then(processingFn).then(function(contentElement) {
        // console.log(contentElement);
        jsIncludeJqueryElement.html(contentElement);
        // The below did not work - second level includes did not resolve.
        let secondLevelIncludes = jsIncludeJqueryElement.find('.js_include');
        if (secondLevelIncludes.length > 0) {
            return Promise.all(secondLevelIncludes.map(function () {
                console.debug("Secondary include: ", $(this));
                return fillJsInclude($(this));
            })).then(function () {
                return jsIncludeJqueryElement;
            });
        } else {
            return jsIncludeJqueryElement;
        }
    }).catch(function(error){
        var titleHtml = "";
        var title = "Missing page.";
        if (jsIncludeJqueryElement.attr("includeTitle")) {
            titleHtml = "<h1 id='" + title + "'>" + title + "</h1>";
        }
        var elementToInclude = titleHtml + "Could not get: " + includedPageUrl + " See debug messages in console for details.";
        fixIncludedHtml(includedPageUrl, elementToInclude, includedPageNewLevelForH1);
        jsIncludeJqueryElement.html(elementToInclude);
        console.warn("An error!", error);
        return jsIncludeJqueryElement;
    });
}

import {updateToc} from "./toc";
// Process includes of the form:
// <div class="js_include" url="../xyz/"/>.
// can't easily use a worker - workers cannot access DOM (workaround: pass strings back and forth), cannot access jquery library.
export default function handleIncludes() {
    console.log("Entering handleIncludes.");
    if ($('.js_include').length === 0 ) { return; }
    return Promise.allSettled($('.js_include').map(function() {
        var jsIncludeJqueryElement = $(this);
        // The actual filling happens in a separate thread!
        return fillJsInclude(jsIncludeJqueryElement, undefined);
    }))
        .then(function(values) {
            console.log("Done including.", values);
            // The below lines do not having any effect if not called without the timeout.
            setTimeout(function(){
                main.prepareContentWithoutIncludes();
                updateToc();
            }, 5000);
            return values;
        })
        .catch(reason => console.error(reason));
}