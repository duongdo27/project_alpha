var performanceCtx = document.getElementById('performanceChart').getContext('2d');
var performanceChart = new Chart(performanceCtx, {
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

var winCtx = document.getElementById('winChart').getContext('2d');
var winChart = new Chart(winCtx, {
  type: 'pie',
  data: {
    datasets: [{
        data: [
            graph_data.won,
            graph_data.drawn,
            graph_data.lost,
        ],
        backgroundColor: [
            "green",
            "blue",
            "red",
        ],
    }],
    labels: [
        "Won",
        "Drawn",
        "Lost"
    ]
  },
  options: {
    title: {
      display: true,
      text:'Won Ratio'
    },
  }
});

var homewinCtx = document.getElementById('homewinChart').getContext('2d');
var homewinChart = new Chart(homewinCtx, {
  type: 'pie',
  data: {
    datasets: [{
        data: [
            graph_data.home_won,
            graph_data.home_drawn,
            graph_data.home_lost,
        ],
        backgroundColor: [
            "green",
            "blue",
            "red",
        ],
    }],
    labels: [
        "Won",
        "Drawn",
        "Lost"
    ]
  },
  options: {
    title: {
      display: true,
      text:'Home Won Ratio'
    },
  }
});

var awaywinCtx = document.getElementById('awaywinChart').getContext('2d');
var awaywinChart = new Chart(awaywinCtx, {
  type: 'pie',
  data: {
    datasets: [{
        data: [
            graph_data.away_won,
            graph_data.away_drawn,
            graph_data.away_lost,
        ],
        backgroundColor: [
            "green",
            "blue",
            "red",
        ],
    }],
    labels: [
        "Won",
        "Drawn",
        "Lost"
    ]
  },
  options: {
    title: {
      display: true,
      text:'Away Won Ratio'
    },
  }
});

