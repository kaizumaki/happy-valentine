var diameter = 960,
    format = d3.format(",d"),
    color = color = d3.scaleOrdinal()
    .range(["#CA2B1D", "#CA7112", "#CA3089", "#845E51", "#84367a", "#840d32"]);

var bubble = d3.pack()
    .size([diameter, diameter])
    .padding(1.5);

var svg = d3.select("main").append("svg")
    .attr("width", diameter)
    .attr("height", diameter)
    .attr("class", "bubble");

// Step
var data = [-2, -1, 0];

var sliderStep = d3
  .sliderBottom()
  .min(d3.min(data))
  .max(d3.max(data))
  .width(300)
  .tickFormat(d3.format('0'))
  .tickValues(data)
  .step(1)
  .default(0)
  .on('onchange', val => {
    d3.select('p#value-step').text(d3.format('0')(val));
    update_data(val);
  });

var gStep = d3
  .select('div#slider-step')
  .append('svg')
  .attr('width', 500)
  .attr('height', 100)
  .append('g')
  .attr('transform', 'translate(30,30)');

gStep.call(sliderStep);

update_data(0);
d3.select('p#value-step').text(d3.format('0')(sliderStep.value()));

function update_data(num) {
  d3.json("data_names.json", function (error, data) {
    var json_files = [];
    for (var i=1; i <= 3; i++) {
      json_files.push("data/" + data[data.length - i].filename + ".json")
    }

    var q = d3.queue()
    .defer(d3.json, json_files[0])
    .defer(d3.json, json_files[1])
    .defer(d3.json, json_files[2])
    .awaitAll(function(error, results) {
      if (error) throw error;

      var word_data = words(results[num * -1]);

      // transition
      var t = d3.transition()
        .duration(750);

      var root = d3.hierarchy(word_data)
        .sum(function(d){ return d.value; })
        .sort(function(a, b){ return b.value - a.value; });

      //JOIN
      var circle = svg.selectAll("circle")
          .data(bubble(root).leaves(), function(d){ return d.data.word; });

      var text = svg.selectAll("text")
          .data(bubble(root).leaves(), function(d){ return d.data.word; })
          .style("opacity", 1)
          .style("font-size", function(d){
            return d.r / 4;
          });

      //EXIT
      circle.exit()
        .transition(t)
          .attr("r", 1e-6)
          .remove();

      text.exit()
        .transition(t)
          .style("opacity", 1e-6)
          .remove();

      //UPDATE
      circle
        .transition(t)
          .attr("r", function(d){ return d.r })
          .attr("cx", function(d){ return d.x; })
          .attr("cy", function(d){ return d.y; });

      text
        .transition(t)
          .attr("x", function(d){ return d.x; })
          .attr("y", function(d){ return d.y; })
          .style("opacity", 1);

      //ENTER
      circle.enter().append("circle")
          .attr("r", function(d){ return d.r; })
          .attr("cx", function(d){ return d.x; })
          .attr("cy", function(d){ return d.y; })
          .attr("fill", function(d){ return color(d.data.color); })
        .transition(t)
          .attr("r", function(d){ return d.r });

      text.enter().append("text")
          .style("opacity", 1e-6)
          .attr("x", function(d){ return d.x; })
          .attr("y", function(d){ return d.y; })
          .attr("dy", ".3em")
          .style("font-size", function(d){
            return d.r / 4;
          })
          .attr("fill", "white")
          .style("text-anchor", "middle")
          .text(function(d){
            return d.data.word.substring(0, d.r / 3);
          })
        .transition(t)
          .style("opacity", 1)
          .attr("fill", "white");
    });
  });
}

function words(root) {
  var words = [];

  root.scored_words.forEach(function(elm, index) {
    words.push({color: index, word: elm.word, value: elm.score * 100});
  });

  return {children: words};
}

d3.select(self.frameElement).style("height", diameter + "px");
