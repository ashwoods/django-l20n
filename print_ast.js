var fs = require('fs');

var L20n = require('l20n');
var parser = new L20n.Parser();

var code = fs.readFileSync('./example.l20n').toString();
var ast = parser.parse(code);
var json = JSON.stringify(ast, null, 4);
console.log(json);
