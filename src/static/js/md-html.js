/**
 * Created by swaroop on 3/30/16.
 */

function mdToHtml(text) {
    var converter = new showdown.Converter();
    return converter.makeHtml(text);
}
(function () {
    mds = document.getElementsByClassName('md');
    for (var i = 0; i < mds.length; i++) {
        text = mds[i].innerHTML;
        mds[i].innerHTML = mdToHtml(text);
    }
})();