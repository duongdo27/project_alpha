$(function () {
	var options = {
		title: {
			text: "Hello"
		},
        animationEnabled: true,
		data: [
		{
			type: "line",
			dataPoints: data,
		}
		]
	};

	$("#chartContainer").CanvasJSChart(options);
});
