Populate with 'js', 'sound', 'images', 'fonts' and 'css' folders from [dFlip PDF FlipBook jQuery Plugin](https://codecanyon.net/item/dflip-flipbook-jquery-plugin/15834127).

Change the dependency URLS in dflip.js as follows: 
```
    pdfjsSrc: url + "js/libs/pdf.min.js",
    //(NON-OPTION) source link for PDFcompatibility.JS file
    pdfjsCompatibilitySrc: url + "js/libs/compatibility.js",
    //(NON-OPTION) source link for PDF.WORKER.JS file
    pdfjsWorkerSrc: url + "js/libs/pdf.worker.min.js",
    //(NON-OPTION) source link for THREE.JS file
    threejsSrc: url + "js/libs/three.min.js",
    //(NON-OPTION) source link for MOCKUP.JS file
    mockupjsSrc: url + "js/libs/mockup.min.js",
    //(NON-OPTION) File path to the trun sound
    soundFile: url + "sound/turn2.mp3",
    imagesLocation: url + "images",
    imageResourcesPath: url + "images/pdfjs/",
    cMapUrl: url + "cmaps/", 
``` 
