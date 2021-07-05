// Left Map
var ctx = document.getElementById("myChart").getContext("2d");
var chartOptions = {
  legend: {
    display: false,
  },
  scales: {
    xAxes: [
      {
        barPercentage: 1,
      },
    ],
    yAxes: [
      // {barPercentage: 1},
      // {gridLines:{drawBorder: false}},
      { ticks: { display: false } },
      // {ticks: {mirror: true}},
      { display: false },
    ],
    elements: {
      rectangle: {
        borderSkipped: "left",
      },
    },
  },
};
var chart = new Chart(ctx, {
  type: "horizontalBar",
  data: {
    labels: document.dashboard.countryNames,
    datasets: [
      {
        label: "Infected Counts",
        backgroundColor: "rgb(50, 50,221 )",
        borderColor: "rgb(255, 99, 132)",
        data: document.dashboard.barPlotVals,
      },
    ],
  },
  options: chartOptions,
});

// World Map
var data2 = document.dashboard.dataForMap;
Highcharts.getJSON(
  "https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/world-population-density.json",
  function (data) {
    // Prevent logarithmic errors in color calulcation
    data2.forEach(function (p) {
      p.value = p.value < 1 ? 1 : p.value;
    });

    // Initiate the chart
    Highcharts.mapChart("MyMapChart", {
      chart: {
        map: "custom/world",
      },

      title: {
        text: "World Map COVID-19 Infection",
      },

      legend: {
        title: {
          text: "Infected Population Count",
          style: {
            color:
              // theme
              (Highcharts.defaultOptions &&
                Highcharts.defaultOptions.legend &&
                Highcharts.defaultOptions.legend.title &&
                Highcharts.defaultOptions.legend.title.style &&
                Highcharts.defaultOptions.legend.title.style.color) ||
              "black",
          },
        },
      },

      mapNavigation: {
        enabled: true,
        buttonOptions: {
          verticalAlign: "bottom",
        },
      },

      tooltip: {
        backgroundColor: "none",
        borderWidth: 0,
        shadow: false,
        useHTML: true,
        padding: 0,
        pointFormat:
          '<span class="f32"><span class="flag {point.properties.hc-key}">' +
          "</span></span> <b>{point.name}<b><br>" +
          '<span style="font-size:25px">{point.value}</span>',
        positioner: function () {
          return { x: 0, y: 250 };
        },
      },

      colorAxis: {
        min: 1,
        max: 1000,
        type: "logarithmic",
      },

      series: [
        {
          data: data2,
          joinBy: ["iso-a3", "code3"],
          name: "Infected Counts",
          states: {
            hover: {
              color: "#a4edba",
            },
          },
        },
      ],
    });
  }
);
// Line Chart
var dataset = document.dashboard.datasetsForLine;
var chartOptions2 = {
  legend: {
    display: true,
  },
  scales: {
    yAxes: [
      {
        type: "linear",
        display: true,
        position: "left",
        id: "y-axis-1",
      },
      {
        type: "linear",
        display: true,
        position: "right",
        id: "y-axis-2",

        gridLines: {
          drawOnChartArea: false,
        },
      },
    ],
  },
};
var ctx2 = document.getElementById("lineChart").getContext("2d");
var myLineChart = new Chart(ctx2, {
  type: "line",
  data: {
    labels: document.dashboard.axisValue,
    datasets: dataset,
  },
  options: chartOptions2,
});

// Heat chart
var options = {
  series: document.dashboard.dataForheatMap,
  chart: {
    height: 6500,
    type: "heatmap",
  },
  dataLabels: {
    enabled: true,
  },
  dataLabels: {
    position: "top",
  },
  colors: ["#008FFB"],
  yaxis: {
    show: false,
  },
  xaxis: {
    type: "category",
    categories: document.dashboard.dataCategory,
  },
};
var chart4 = new ApexCharts(document.querySelector("#heatchart"), options);
chart4.render();
