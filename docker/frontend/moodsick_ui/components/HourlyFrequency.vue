<template>
  <div>
    Hourly Login Description
    <div id="mainHourlyFreq" style="height: 80vh; width: 100%"></div>
  </div>
</template>
  
  <script>
import * as echarts from "echarts";

export default {
  props: ["graphData"],
  mounted() {
    this.$nextTick(() => {
      var chartDom = document.getElementById("mainHourlyFreq");
      var myChart = echarts.init(chartDom);
      var option;
      console.log(this.graphData);
      let xAxisData = Object.keys(this.graphData),
        seriesData = Object.values(this.graphData);

      option = {
        xAxis: {
          type: "category",
          name: "Hour of the day frequency",
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
    });
  },
};
</script>
  
  <style>
</style>
  