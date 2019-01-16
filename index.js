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

d3.json("data_names.json", function(error, data) {
  var json_file = data[data.length - 1].filename;

  d3.json("data/" + json_file + ".json", function(error, data) {
    if (error) throw error;

    var root = d3.hierarchy(words(data))
        .sum(function(d) { return d.value; })
        .sort(function(a, b) { return b.value - a.value; });

    bubble(root);
    var node = svg.selectAll(".node")
        .data(root.children)
        .enter().append("g")
        .attr("class", "node")
        .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

    node.append("title")
        .text(function(d) { return d.data.word + ": " + format(d.value); });

    node.append("circle")
        .attr("r", function(d) { return d.r; })
        .style("fill", function(d) {
          return color(d.data.color);
        });

    node.append("text")
        .attr("dy", ".3em")
        .attr("font-size", function(d){
          return d.r/4;
        })
        .attr("fill", "white")
        .style("text-anchor", "middle")
        .text(function(d) { return d.data.word.substring(0, d.r/3); });
  });
});

function words(root) {
  var words = [];

  root.scored_words.forEach(function(elm, index) {
    words.push({color: index, word: elm.word, value: elm.score * 100});
  });

  return {children: words};
}

d3.select(self.frameElement).style("height", diameter + "px");
