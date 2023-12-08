<template>
    <div>
      Hourly Login Description
      <div id="main" style="height:80vh; width:80vw"></div>
    </div>
  </template>
  
  <script>
  import * as echarts from 'echarts';
  
  export default {
    mounted() {
      this.$nextTick(() => {
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom);
        var option;
  
        option = {
          xAxis: {
            type: 'category',
            name: 'Hour of the day frequency',
            data: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
          },
          yAxis: {
            type: 'value',
            name: 'Frequency'
          },
  
          series: [
            {
              data: [2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 2, 1, 0, 2, 0],
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
  