<template>
    <div>
      Daily Login Description
      <div id="mainsdjfkhcaskc" style="height:80vh; width: 100%"></div>
    </div>
  </template>
  
  <script>
  import * as echarts from 'echarts';
  
  export default {
  props: ["graphData"],
    mounted() {
      this.$nextTick(() => {
        var chartDom = document.getElementById('mainsdjfkhcaskc');
        var myChart = echarts.init(chartDom);
        var option;
        let xAxisData = Object.keys(this.graphData),
        seriesData = Object.values(this.graphData)
  
        option = {
          xAxis: {
            type: 'category',
            name: 'Hour of the day frequency',
            data: xAxisData
          },
          yAxis: {
            type: 'value',
            name: 'Frequency'
          },
  
          series: [
            {
              data: seriesData,
              type: 'bar'
            }
          ]
        };
  
        option && myChart.setOption(option);
      });
    }
  };
  </script>
  
  <style>
  </style>
  