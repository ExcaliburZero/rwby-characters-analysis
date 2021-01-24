function main() {
    let vis_svg = d3.select("#character-visualization")
        .append("svg");

    vis_svg.append("rect")
        .attr("fill", "blue")
        .attr("width", 100)
        .attr("height", 200);
}