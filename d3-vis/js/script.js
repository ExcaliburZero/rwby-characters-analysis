/* global d3 */
/* exported main */

function main() {
    d3.csv("data/RWBY Characters By Volume.csv", (data) => {
        console.log(data);
    });

    let vis_svg = d3.select("#character-visualization")
        .append("svg");

    vis_svg.append("rect")
        .attr("fill", "blue")
        .attr("width", 100)
        .attr("height", 200);
}