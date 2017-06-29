var ctx = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: graph_data.rounds,
    datasets: [
    {
      fill: false,
      label: 'Points',
      data: graph_data.points,
      borderColor: "blue",
      yAxisID: "y-axis-1",
    },
    {
      fill: false,
      label: 'Ranks',
      data: graph_data.ranks,
      borderColor: "red",
      yAxisID: "y-axis-2",
    }
    ]
  },
  options: {
    elements: {
        line: {
            tension: 0
        }
    },
    title: {
      display: true,
      text:'Performance'
    },
    scales: {
        xAxes: [
        {
            scaleLabel: {
                display: true,
                labelString: 'Round',
            }
        }
        ],
        yAxes: [
        {
            type: "linear",
            display: true,
            position: "left",
            id: "y-axis-1",
            scaleLabel: {
                display: true,
                labelString: 'Points',
            }
        },
        {
            type: "linear",
            display: true,
            position: "right",
            id: "y-axis-2",
            gridLines: {
                drawOnChartArea: false,
            },
            ticks: {
                reverse: true
            },
            scaleLabel: {
                display: true,
                labelString: 'Rank',
            }
        }
        ]
    }
  }
});
