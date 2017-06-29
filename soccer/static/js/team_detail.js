var ctx = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: graph_data.rounds,
    datasets: [
    {
      label: 'Points',
      data: graph_data.points,
      backgroundColor: "rgba(153,255,51,0.4)"
    }
    ]
  }
});
