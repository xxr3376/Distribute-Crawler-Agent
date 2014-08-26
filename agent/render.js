'use strict';
try {
  var args = require('system').args;

  var input_path = args[1];
  var output_path = args[2];

  var fs = require('fs');
  var input_file = fs.open(input_path, 'r');
  var output_file = fs.open(output_path, 'w');

  var argument = JSON.parse(input_file.read());
  var page = require('webpage').create();
  var response_dict = {};

  input_file.close();

  if (argument['cookies']) {
    for (var key in argument['cookies']) {
      phantom.addCookie({
        name: key,
        value: argument['cookies'][key],
        domain: argument['domain'],
      })
    }
  }

  page.settings = {
    userAgent: argument['headers']['User-Agent'],
    ignoreSslErrors: true,
    javascriptEnabled: true,
    loadImages: false,
  }
  page.customHeaders = argument['headers'];

  // set Viewport so that youtube will load comments
  page.viewportSize = { width: 1600, height: 5000, };

  var last_update = Date.now();

  page.onResourceRequested = function (request) {
    console.log('Request (#' + request.id + '): ' + request.url);
    last_update = Date.now();
  };

  page.onResourceReceived = function (response) {
    if (response.stage === 'end') {
      console.log('Response (#' + response.id + '): ' + response.url);
      response_dict[response.url] = response
    }
    last_update = Date.now();
  };

  page.open(argument['url'], function(st) {
    var wait = function() {
      var now = Date.now();
      var diff = now - last_update;
      console.log('diff:', diff);
      var left = 4000 - diff;
      if (left > 0) {
        setTimeout(wait, left);
      }
      else {
        var doc = page.evaluate(function () {
          return document.all[0].outerHTML;
        });
        var url = page.evaluate( function () {
          return document.URL;
        });
        var iframes = page.evaluate( function () {
          var result = [];
          var query = document.querySelectorAll('iframe');
          var _len = query.length;
          for (var i = 0; i < _len; i++) {
            result[i] = query[i].contentDocument.all[0].outerHTML;
          }
          return result;
        });
        var response = response_dict[url] || {status: 200, headers: []};

        var answer = {
          doc: doc,
          url: url,
          iframes: iframes,
          status_code: response.status,
          headers: response.headers,
        };

        output_file.write(JSON.stringify(answer));
        output_file.close();
        phantom.exit(0);
      }
    };
    wait();
  });
}
catch (e) {
  console.log('PhantomJS Error:', e);
  phantom.exit(-1);
}
