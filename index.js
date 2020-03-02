const express = require('express');
const bodyParser = require('body-parser');
const multer = require('multer');

const app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.get("/", (req, res) => {
    res.sendFile(`${__dirname}/index.html`);
});

app.get("/gethsv", (req, res) => {
    const editJsonFile = require('edit-json-file');
    let file = editJsonFile(`${__dirname}/parameters/hsvTargetLAST.json`);
    res.send(file.data)
});

app.post("/edit", (req, res) => {
    let hue = req.body.hue;
    let sat = req.body.sat;
    let val = req.body.val;
    hue = [parseInt(hue[0], 10), parseInt(hue[1], 10)];
	sat = [parseInt(sat[0], 10), parseInt(sat[1], 10)];
    val = [parseInt(val[0], 10), parseInt(val[1], 10)];
    console.log(hue, sat, val);
    const editJsonFile = require('edit-json-file');
    let file1 = editJsonFile(`${__dirname}/parameters/hsvTargetLAST.json`);
    if (hue != file1.hue || sat != file1.sat || val != file1.val) {
        let file2 = editJsonFile(`${__dirname}/parameters/hsvTarget.json`);
        file1.set("hue", hue);
        file1.set("sat", sat);
        file1.set("val", val);
        file2.set("hue", hue);
        file2.set("sat", sat);
        file2.set("val", val);
        file2.save();
    }
    file1.save();
    res.send("ok");
});
app.listen(3003);