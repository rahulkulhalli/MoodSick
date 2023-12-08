<template>
Day of the week frequency
  <div id="mainDayFreq" style="height: 80vh; width: 100%"></div>
</template>

<script>
import * as echarts from "echarts";

export default {
  props: ["graphData"],
  mounted() {
    var chartDom = document.getElementById("mainDayFreq");
    var myChart = echarts.init(chartDom);
    var option;
    let xAxisData = Object.keys(this.graphData),
      seriesData = Object.values(this.graphData)

    option = {
      xAxis: {
        type: "category",
        name: "Day of the week",
        data: xAxisData,
      },
      yAxis: {
        type: "value",
        name: "Frequency",
      },

      series: [
        {
          data: seriesData,
          type: "bar",
        },
      ],
    };

    option && myChart.setOption(option);
  },
};
</script>

<style>
</style>