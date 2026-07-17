const fs = require('fs');
const pdf = require('pdf-parse');

let dataBuffer = fs.readFileSync('Oula (1).pdf');

pdf(dataBuffer).then(function(data) {
    fs.writeFileSync('output.txt', data.text.substring(0, 3000), 'utf8');
    console.log("Successfully extracted text. Length: " + data.text.length);
}).catch(function(err){
    console.log("Error: " + err);
});
